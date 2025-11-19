"""
Workspace Indexer
Watches and indexes code files for RAG
"""

import asyncio
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set
import mimetypes

import structlog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .vectorstore import VectorStore
from .chunker import CodeChunker

logger = structlog.get_logger()


class WorkspaceIndexer:
    """Indexes workspace files for semantic search"""
    
    # File extensions to index
    CODE_EXTENSIONS = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
        '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.r',
        '.m', '.mm', '.sh', '.bash', '.zsh', '.sql', '.html', '.css', '.scss',
        '.sass', '.less', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini',
        '.md', '.txt', '.vue', '.svelte'
    }
    
    # Directories to ignore
    IGNORE_DIRS = {
        'node_modules', '.git', '.venv', 'venv', 'env', '__pycache__',
        '.pytest_cache', 'dist', 'build', 'out', '.next', '.nuxt',
        'coverage', '.coverage', 'htmlcov', '.tox', 'target'
    }
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        """Initialize indexer"""
        self.vector_store = vector_store
        self.chunker = CodeChunker()
        self.indexed_files: Dict[str, str] = {}  # file_path -> content_hash
        self.workspace_path: Optional[Path] = None
        self.observer: Optional[Observer] = None
        self._indexing_lock = asyncio.Lock()
        
        logger.info("Workspace indexer initialized")
    
    async def initialize(self, workspace_path: str):
        """Initialize indexer with workspace path"""
        self.workspace_path = Path(workspace_path)
        
        if self.vector_store is None:
            self.vector_store = VectorStore()
            await self.vector_store.initialize()
        
        logger.info("Indexer ready", workspace=str(self.workspace_path))
    
    async def index_workspace(self, force_reindex: bool = False):
        """Index entire workspace"""
        if not self.workspace_path:
            raise RuntimeError("Workspace path not set")
        
        async with self._indexing_lock:
            logger.info("Starting workspace indexing",
                       workspace=str(self.workspace_path),
                       force=force_reindex)
            
            if force_reindex:
                await self.vector_store.clear()
                self.indexed_files.clear()
            
            # Find all code files
            files_to_index = self._find_code_files(self.workspace_path)
            
            logger.info("Found code files", count=len(files_to_index))
            
            # Index files in batches
            batch_size = 10
            for i in range(0, len(files_to_index), batch_size):
                batch = files_to_index[i:i+batch_size]
                await self._index_files_batch(batch)
            
            logger.info("Workspace indexing complete",
                       total_files=len(self.indexed_files))
    
    def _find_code_files(self, root_path: Path) -> List[Path]:
        """Find all code files in workspace"""
        code_files = []
        
        for path in root_path.rglob('*'):
            # Skip directories
            if path.is_dir():
                continue
            
            # Skip ignored directories
            if any(ignored in path.parts for ignored in self.IGNORE_DIRS):
                continue
            
            # Check extension
            if path.suffix.lower() in self.CODE_EXTENSIONS:
                code_files.append(path)
        
        return code_files
    
    async def _index_files_batch(self, files: List[Path]):
        """Index a batch of files"""
        for file_path in files:
            try:
                await self.index_file(file_path)
            except Exception as e:
                logger.error("Failed to index file",
                           file=str(file_path),
                           error=str(e))
    
    async def index_file(self, file_path: Path):
        """Index a single file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Calculate content hash
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Check if already indexed with same content
            rel_path = str(file_path.relative_to(self.workspace_path)) if self.workspace_path else str(file_path)
            
            if rel_path in self.indexed_files and self.indexed_files[rel_path] == content_hash:
                logger.debug("File already indexed", file=rel_path)
                return
            
            # Detect language
            language = self._detect_language(file_path)
            
            # Chunk the file
            chunks = self.chunker.chunk_code(content, language)
            
            # Remove old chunks for this file
            await self.vector_store.delete_by_file(rel_path)
            
            # Create documents for each chunk
            documents = []
            for chunk in chunks:
                doc = {
                    "text": chunk["text"],
                    "metadata": {
                        "file_path": rel_path,
                        "line_start": chunk["line_start"],
                        "line_end": chunk["line_end"],
                        "language": language,
                        "chunk_type": chunk.get("type", "code")
                    }
                }
                documents.append(doc)
            
            # Add to vector store
            if documents:
                await self.vector_store.add_documents(documents)
            
            # Update indexed files
            self.indexed_files[rel_path] = content_hash
            
            logger.debug("File indexed",
                        file=rel_path,
                        chunks=len(documents))
            
        except Exception as e:
            logger.error("Failed to index file",
                        file=str(file_path),
                        error=str(e),
                        exc_info=True)
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        ext = file_path.suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.sh': 'bash',
            '.bash': 'bash',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.vue': 'vue',
            '.md': 'markdown'
        }
        
        return language_map.get(ext, 'text')
    
    async def start_watching(self):
        """Start watching workspace for changes"""
        if not self.workspace_path:
            raise RuntimeError("Workspace path not set")
        
        class IndexerEventHandler(FileSystemEventHandler):
            def __init__(self, indexer):
                self.indexer = indexer
            
            def on_modified(self, event: FileSystemEvent):
                if not event.is_directory:
                    path = Path(event.src_path)
                    if path.suffix in WorkspaceIndexer.CODE_EXTENSIONS:
                        asyncio.create_task(self.indexer.index_file(path))
            
            def on_created(self, event: FileSystemEvent):
                self.on_modified(event)
            
            def on_deleted(self, event: FileSystemEvent):
                if not event.is_directory:
                    path = Path(event.src_path)
                    if path.suffix in WorkspaceIndexer.CODE_EXTENSIONS:
                        rel_path = str(path.relative_to(self.indexer.workspace_path))
                        asyncio.create_task(
                            self.indexer.vector_store.delete_by_file(rel_path)
                        )
        
        event_handler = IndexerEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.workspace_path), recursive=True)
        self.observer.start()
        
        logger.info("Started watching workspace", path=str(self.workspace_path))
    
    async def stop_watching(self):
        """Stop watching workspace"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Stopped watching workspace")
    
    async def shutdown(self):
        """Cleanup on shutdown"""
        await self.stop_watching()
        logger.info("Indexer shut down")
    
    async def get_status(self) -> Dict:
        """Get indexer status"""
        stats = await self.vector_store.get_stats() if self.vector_store else {}
        
        return {
            "workspace_path": str(self.workspace_path) if self.workspace_path else None,
            "indexed_files": len(self.indexed_files),
            "watching": self.observer is not None and self.observer.is_alive(),
            "vector_store": stats
        }

