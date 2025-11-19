"""
Code Chunker
Splits code into semantic chunks for embedding
"""

from typing import List, Dict
import structlog

logger = structlog.get_logger()


class CodeChunker:
    """Chunks code files into manageable pieces"""
    
    def __init__(self, 
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        """Initialize chunker
        
        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_code(self, 
                   content: str,
                   language: str = "text") -> List[Dict]:
        """Chunk code content
        
        Args:
            content: File content
            language: Programming language
        
        Returns:
            List of chunks with metadata
        """
        lines = content.split('\n')
        
        # For small files, return as single chunk
        if len(content) <= self.chunk_size:
            return [{
                "text": content,
                "line_start": 1,
                "line_end": len(lines),
                "type": "full_file"
            }]
        
        # Split by logical boundaries
        chunks = []
        
        # Try to split by functions/classes
        if language in ["python", "javascript", "typescript", "java", "cpp", "csharp"]:
            chunks = self._chunk_by_functions(content, lines, language)
        
        # Fallback to sliding window
        if not chunks:
            chunks = self._chunk_sliding_window(content, lines)
        
        return chunks
    
    def _chunk_by_functions(self,
                           content: str,
                           lines: List[str],
                           language: str) -> List[Dict]:
        """Chunk code by functions and classes"""
        chunks = []
        current_chunk = []
        current_start_line = 1
        current_size = 0
        indent_stack = []
        
        # Simple heuristic-based chunking
        for i, line in enumerate(lines, 1):
            # Detect function/class definitions
            stripped = line.lstrip()
            
            is_boundary = False
            if language == "python":
                if stripped.startswith("def ") or stripped.startswith("class "):
                    is_boundary = True
            elif language in ["javascript", "typescript"]:
                if "function " in stripped or "class " in stripped or "const " in stripped and "=>" in stripped:
                    is_boundary = True
            elif language in ["java", "cpp", "csharp"]:
                if "class " in stripped or "public " in stripped or "private " in stripped:
                    is_boundary = True
            
            # If we hit a boundary and have accumulated enough content
            if is_boundary and current_size > self.chunk_size // 2:
                chunk_text = '\n'.join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "line_start": current_start_line,
                    "line_end": i - 1,
                    "type": "function"
                })
                
                # Start new chunk with overlap
                overlap_lines = current_chunk[-5:] if len(current_chunk) > 5 else current_chunk
                current_chunk = overlap_lines + [line]
                current_start_line = max(1, i - len(overlap_lines))
                current_size = sum(len(l) for l in current_chunk)
            else:
                current_chunk.append(line)
                current_size += len(line)
            
            # Force split if chunk too large
            if current_size > self.chunk_size * 1.5:
                chunk_text = '\n'.join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "line_start": current_start_line,
                    "line_end": i,
                    "type": "function"
                })
                current_chunk = []
                current_start_line = i + 1
                current_size = 0
        
        # Add remaining content
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "line_start": current_start_line,
                "line_end": len(lines),
                "type": "function"
            })
        
        return chunks
    
    def _chunk_sliding_window(self,
                             content: str,
                             lines: List[str]) -> List[Dict]:
        """Chunk using sliding window approach"""
        chunks = []
        current_lines = []
        current_size = 0
        start_line = 1
        
        for i, line in enumerate(lines, 1):
            current_lines.append(line)
            current_size += len(line)
            
            # Check if chunk is large enough
            if current_size >= self.chunk_size:
                chunk_text = '\n'.join(current_lines)
                chunks.append({
                    "text": chunk_text,
                    "line_start": start_line,
                    "line_end": i,
                    "type": "window"
                })
                
                # Calculate overlap
                overlap_chars = 0
                overlap_lines = []
                for line in reversed(current_lines):
                    if overlap_chars >= self.chunk_overlap:
                        break
                    overlap_lines.insert(0, line)
                    overlap_chars += len(line)
                
                # Start new chunk
                current_lines = overlap_lines
                current_size = overlap_chars
                start_line = i - len(overlap_lines) + 1
        
        # Add remaining lines
        if current_lines:
            chunk_text = '\n'.join(current_lines)
            chunks.append({
                "text": chunk_text,
                "line_start": start_line,
                "line_end": len(lines),
                "type": "window"
            })
        
        return chunks

