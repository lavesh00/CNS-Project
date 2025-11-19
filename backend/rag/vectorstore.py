"""
FAISS Vector Store
CPU-optimized vector similarity search
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import faiss
import numpy as np
import structlog
from sentence_transformers import SentenceTransformer

logger = structlog.get_logger()


class VectorStore:
    """FAISS-based vector store for code embeddings"""
    
    def __init__(self, 
                 embedding_model: str = "all-MiniLM-L6-v2",
                 index_path: Optional[Path] = None):
        """Initialize vector store"""
        
        self.embedding_model_name = embedding_model
        self.embedding_model: Optional[SentenceTransformer] = None
        self.dimension: Optional[int] = None
        
        self.index: Optional[faiss.IndexFlatL2] = None
        self.documents: List[Dict] = []
        
        if index_path is None:
            index_path = Path.home() / ".agent-lucky" / "index"
        
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Vector store initialized", 
                   model=embedding_model,
                   index_path=str(self.index_path))
    
    async def initialize(self):
        """Initialize embedding model"""
        logger.info("Loading embedding model", model=self.embedding_model_name)
        
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        
        # Create FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Try to load existing index
        await self._load_index()
        
        logger.info("Vector store ready",
                   dimension=self.dimension,
                   documents=len(self.documents))
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if self.embedding_model is None:
            raise RuntimeError("Embedding model not initialized")
        
        return self.embedding_model.encode(text, show_progress_bar=False)
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        if self.embedding_model is None:
            raise RuntimeError("Embedding model not initialized")
        
        return self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32
        )
    
    async def add_documents(self, documents: List[Dict]):
        """Add documents to the index
        
        Args:
            documents: List of dicts with keys:
                - text: str (content to embed)
                - metadata: dict (file_path, line_start, line_end, language, etc.)
        """
        if not documents:
            return
        
        logger.info("Adding documents to index", count=len(documents))
        
        # Extract text for embedding
        texts = [doc["text"] for doc in documents]
        
        # Generate embeddings
        embeddings = self.embed_batch(texts)
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Store document metadata
        self.documents.extend(documents)
        
        logger.info("Documents added", 
                   total=len(self.documents),
                   index_size=self.index.ntotal)
        
        # Save index
        await self._save_index()
    
    async def search(self, 
                    query: str,
                    k: int = 5,
                    filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """Search for similar documents
        
        Args:
            query: Query text
            k: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of documents with scores
        """
        if self.index.ntotal == 0:
            logger.warning("Index is empty")
            return []
        
        # Generate query embedding
        query_embedding = self.embed_text(query)
        
        # Search FAISS index
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'),
            k
        )
        
        # Retrieve documents
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # No more results
                break
            
            doc = self.documents[idx].copy()
            doc['score'] = float(1 / (1 + dist))  # Convert distance to similarity score
            
            # Apply metadata filters
            if filter_metadata:
                if all(doc['metadata'].get(k) == v for k, v in filter_metadata.items()):
                    results.append(doc)
            else:
                results.append(doc)
        
        logger.debug("Search completed",
                    query_length=len(query),
                    results=len(results))
        
        return results
    
    async def search_by_file(self,
                            file_path: str,
                            k: int = 5) -> List[Dict]:
        """Search for documents from a specific file"""
        return await self.search("", k=k, filter_metadata={"file_path": file_path})
    
    async def delete_by_file(self, file_path: str):
        """Remove all documents from a specific file"""
        # Find indices to remove
        indices_to_remove = [
            i for i, doc in enumerate(self.documents)
            if doc['metadata'].get('file_path') == file_path
        ]
        
        if not indices_to_remove:
            return
        
        logger.info("Removing documents", file=file_path, count=len(indices_to_remove))
        
        # Remove from documents list (in reverse to maintain indices)
        for idx in sorted(indices_to_remove, reverse=True):
            del self.documents[idx]
        
        # Rebuild index (FAISS doesn't support efficient deletion)
        await self._rebuild_index()
    
    async def _rebuild_index(self):
        """Rebuild the entire index"""
        logger.info("Rebuilding index", documents=len(self.documents))
        
        if not self.documents:
            self.index = faiss.IndexFlatL2(self.dimension)
            return
        
        # Extract texts and re-embed
        texts = [doc["text"] for doc in self.documents]
        embeddings = self.embed_batch(texts)
        
        # Create new index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings.astype('float32'))
        
        await self._save_index()
    
    async def _save_index(self):
        """Save index and documents to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path / "index.faiss"))
            
            # Save documents metadata
            with open(self.index_path / "documents.pkl", 'wb') as f:
                pickle.dump(self.documents, f)
            
            # Save config
            config = {
                "embedding_model": self.embedding_model_name,
                "dimension": self.dimension,
                "document_count": len(self.documents)
            }
            with open(self.index_path / "config.json", 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.debug("Index saved")
            
        except Exception as e:
            logger.error("Failed to save index", error=str(e))
    
    async def _load_index(self):
        """Load index from disk"""
        index_file = self.index_path / "index.faiss"
        docs_file = self.index_path / "documents.pkl"
        
        if not index_file.exists() or not docs_file.exists():
            logger.info("No existing index found")
            return
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(index_file))
            
            # Load documents
            with open(docs_file, 'rb') as f:
                self.documents = pickle.load(f)
            
            logger.info("Index loaded",
                       documents=len(self.documents),
                       index_size=self.index.ntotal)
            
        except Exception as e:
            logger.error("Failed to load index", error=str(e))
            # Create new index on error
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
    
    async def clear(self):
        """Clear all documents from index"""
        logger.info("Clearing index")
        
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        
        await self._save_index()
    
    async def get_stats(self) -> Dict:
        """Get index statistics"""
        return {
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "model": self.embedding_model_name
        }

