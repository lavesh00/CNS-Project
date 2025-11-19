"""
RAG Retriever
Retrieves relevant context for prompts
"""

from typing import List, Dict, Optional
import structlog

from .vectorstore import VectorStore

logger = structlog.get_logger()


class Retriever:
    """Retrieves relevant code context"""
    
    def __init__(self, vector_store: VectorStore):
        """Initialize retriever"""
        self.vector_store = vector_store
    
    async def retrieve(self,
                      query: str,
                      k: int = 10,
                      min_score: float = 0.3,
                      file_filter: Optional[str] = None) -> List[Dict]:
        """Retrieve relevant code chunks
        
        Args:
            query: Search query
            k: Number of results
            min_score: Minimum similarity score
            file_filter: Optional file path filter
        
        Returns:
            List of relevant code chunks
        """
        # Build filter
        filter_metadata = {}
        if file_filter:
            filter_metadata["file_path"] = file_filter
        
        # Search vector store
        results = await self.vector_store.search(
            query=query,
            k=k,
            filter_metadata=filter_metadata if filter_metadata else None
        )
        
        # Filter by minimum score
        filtered = [r for r in results if r['score'] >= min_score]
        
        logger.debug("Retrieved context",
                    query_length=len(query),
                    results=len(filtered),
                    min_score=min_score)
        
        return filtered
    
    async def retrieve_by_file(self,
                              file_path: str,
                              k: int = 5) -> List[Dict]:
        """Retrieve chunks from a specific file"""
        results = await self.vector_store.search_by_file(file_path, k=k)
        
        logger.debug("Retrieved file context",
                    file=file_path,
                    chunks=len(results))
        
        return results
    
    async def retrieve_hybrid(self,
                             query: str,
                             file_paths: List[str],
                             k: int = 10) -> List[Dict]:
        """Hybrid retrieval: semantic + file-based
        
        Args:
            query: Search query
            file_paths: Files to prioritize
            k: Number of results
        
        Returns:
            Combined results
        """
        # Get semantic results
        semantic_results = await self.retrieve(query, k=k)
        
        # Get results from specific files
        file_results = []
        for file_path in file_paths[:3]:  # Limit to top 3 files
            results = await self.retrieve_by_file(file_path, k=2)
            file_results.extend(results)
        
        # Combine and deduplicate
        seen = set()
        combined = []
        
        for result in semantic_results + file_results:
            file_path = result['metadata']['file_path']
            line_start = result['metadata']['line_start']
            
            key = f"{file_path}:{line_start}"
            if key not in seen:
                seen.add(key)
                combined.append(result)
        
        # Sort by score
        combined.sort(key=lambda x: x['score'], reverse=True)
        
        logger.debug("Hybrid retrieval",
                    query_length=len(query),
                    semantic=len(semantic_results),
                    file_based=len(file_results),
                    combined=len(combined))
        
        return combined[:k]
    
    def format_context(self, chunks: List[Dict], max_length: int = 8000) -> str:
        """Format retrieved chunks into context string
        
        Args:
            chunks: Retrieved chunks
            max_length: Maximum context length in characters
        
        Returns:
            Formatted context string
        """
        context_parts = []
        current_length = 0
        
        for chunk in chunks:
            metadata = chunk['metadata']
            text = chunk['text']
            
            # Format chunk with metadata
            chunk_header = f"\n# File: {metadata['file_path']} (lines {metadata['line_start']}-{metadata['line_end']})\n"
            chunk_formatted = f"{chunk_header}```{metadata.get('language', 'text')}\n{text}\n```\n"
            
            chunk_length = len(chunk_formatted)
            
            # Check if adding this chunk would exceed max length
            if current_length + chunk_length > max_length:
                break
            
            context_parts.append(chunk_formatted)
            current_length += chunk_length
        
        context = '\n'.join(context_parts)
        
        logger.debug("Formatted context",
                    chunks_used=len(context_parts),
                    length=len(context))
        
        return context

