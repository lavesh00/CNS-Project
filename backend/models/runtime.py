"""
llama.cpp Runtime Integration
Python wrapper for local model inference using llama.cpp
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, List, AsyncIterator
from dataclasses import dataclass

import structlog

logger = structlog.get_logger()


@dataclass
class GenerationConfig:
    """Configuration for text generation"""
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    max_tokens: int = 2048
    stop_sequences: List[str] = None
    json_mode: bool = False
    stream: bool = False
    
    def __post_init__(self):
        if self.stop_sequences is None:
            self.stop_sequences = []


class LlamaCppRuntime:
    """Wrapper for llama.cpp inference"""
    
    def __init__(self, models_dir: Optional[Path] = None):
        """Initialize runtime"""
        self.models_dir = models_dir or Path.home() / ".agent-lucky" / "models"
        self.llama_cpp_path = self._find_llama_cpp()
        self.loaded_model_path: Optional[Path] = None
        self.model_process: Optional[subprocess.Popen] = None
        self.context_size = 4096
        
        logger.info("Llama.cpp runtime initialized", 
                   llama_cpp=str(self.llama_cpp_path))
    
    def _find_llama_cpp(self) -> Optional[Path]:
        """Find llama.cpp binary"""
        # Check common locations
        possible_paths = [
            Path("llama.cpp/main"),
            Path("llama.cpp/main.exe"),
            Path(__file__).parent.parent / "bin" / "llama-cli",
            Path(__file__).parent.parent / "bin" / "llama-cli.exe",
            Path.home() / ".agent-lucky" / "bin" / "llama-cli",
            Path.home() / ".agent-lucky" / "bin" / "llama-cli.exe",
        ]
        
        # Check system PATH
        if sys.platform == "win32":
            llama_names = ["llama-cli.exe", "main.exe"]
        else:
            llama_names = ["llama-cli", "main"]
        
        for name in llama_names:
            result = subprocess.run(
                ["where" if sys.platform == "win32" else "which", name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                path = Path(result.stdout.strip().split('\n')[0])
                if path.exists():
                    return path
        
        # Check possible paths
        for path in possible_paths:
            if path.exists():
                return path
        
        logger.warning("llama.cpp binary not found, will need to download/compile")
        return None
    
    async def load_model(self, model_path: Path, context_size: int = 4096) -> bool:
        """Load a model for inference"""
        if not model_path.exists():
            logger.error("Model file not found", path=str(model_path))
            return False
        
        if not self.llama_cpp_path:
            logger.error("llama.cpp binary not available")
            return False
        
        self.loaded_model_path = model_path
        self.context_size = context_size
        
        logger.info("Model loaded", 
                   model=str(model_path),
                   context_size=context_size)
        
        return True
    
    async def generate(self, 
                      prompt: str,
                      config: Optional[GenerationConfig] = None) -> str:
        """Generate text from prompt"""
        
        if config is None:
            config = GenerationConfig()
        
        if not self.loaded_model_path:
            raise RuntimeError("No model loaded")
        
        if not self.llama_cpp_path:
            raise RuntimeError("llama.cpp binary not available")
        
        # Build llama.cpp command
        cmd = [
            str(self.llama_cpp_path),
            "-m", str(self.loaded_model_path),
            "-p", prompt,
            "-c", str(self.context_size),
            "-n", str(config.max_tokens),
            "--temp", str(config.temperature),
            "--top-p", str(config.top_p),
            "--top-k", str(config.top_k),
            "-b", "512",  # Batch size
            "--threads", str(os.cpu_count() or 4),
        ]
        
        # Add JSON mode if requested
        if config.json_mode:
            cmd.extend(["--json-schema", json.dumps({
                "type": "object"
            })])
        
        # Add stop sequences
        for stop in config.stop_sequences:
            cmd.extend(["--reverse-prompt", stop])
        
        try:
            logger.debug("Running inference", prompt_length=len(prompt))
            
            # Run llama.cpp
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                logger.error("Inference failed", 
                           stderr=stderr.decode(),
                           returncode=result.returncode)
                raise RuntimeError(f"Inference failed: {stderr.decode()}")
            
            output = stdout.decode()
            
            logger.debug("Inference completed", 
                        output_length=len(output))
            
            return output.strip()
            
        except Exception as e:
            logger.error("Failed to run inference", error=str(e), exc_info=True)
            raise
    
    async def generate_stream(self,
                             prompt: str,
                             config: Optional[GenerationConfig] = None) -> AsyncIterator[str]:
        """Generate text with streaming"""
        
        if config is None:
            config = GenerationConfig(stream=True)
        
        if not self.loaded_model_path:
            raise RuntimeError("No model loaded")
        
        if not self.llama_cpp_path:
            raise RuntimeError("llama.cpp binary not available")
        
        # Build command
        cmd = [
            str(self.llama_cpp_path),
            "-m", str(self.loaded_model_path),
            "-p", prompt,
            "-c", str(self.context_size),
            "-n", str(config.max_tokens),
            "--temp", str(config.temperature),
            "--top-p", str(config.top_p),
            "--top-k", str(config.top_k),
            "-b", "512",
            "--threads", str(os.cpu_count() or 4),
        ]
        
        if config.json_mode:
            cmd.extend(["--json-schema", json.dumps({"type": "object"})])
        
        try:
            # Start process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Stream output
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                
                text = line.decode().strip()
                if text:
                    yield text
            
            await process.wait()
            
        except Exception as e:
            logger.error("Stream generation failed", error=str(e))
            raise
    
    async def generate_json(self, 
                           prompt: str,
                           schema: Optional[Dict] = None,
                           config: Optional[GenerationConfig] = None) -> Dict:
        """Generate JSON output with validation"""
        
        if config is None:
            config = GenerationConfig(json_mode=True)
        else:
            config.json_mode = True
        
        # Add JSON instruction to prompt
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        
        output = await self.generate(json_prompt, config)
        
        # Try to parse JSON
        try:
            # Find JSON in output (may have extra text)
            start_idx = output.find('{')
            end_idx = output.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                # Try array format
                start_idx = output.find('[')
                end_idx = output.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                json_str = output[start_idx:end_idx+1]
                result = json.loads(json_str)
                return result
            else:
                raise ValueError("No valid JSON found in output")
                
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON output",
                        error=str(e),
                        output=output[:500])
            
            # Try to repair JSON
            repaired = self._repair_json(output)
            if repaired:
                return repaired
            
            raise ValueError(f"Invalid JSON output: {e}")
    
    def _repair_json(self, text: str) -> Optional[Dict]:
        """Attempt to repair malformed JSON"""
        try:
            # Remove common issues
            text = text.strip()
            
            # Find JSON boundaries
            start = text.find('{')
            end = text.rfind('}')
            
            if start == -1 or end == -1:
                start = text.find('[')
                end = text.rfind(']')
            
            if start == -1 or end == -1:
                return None
            
            json_str = text[start:end+1]
            
            # Try parsing
            return json.loads(json_str)
            
        except:
            return None
    
    async def unload_model(self):
        """Unload the current model"""
        if self.model_process:
            self.model_process.terminate()
            self.model_process = None
        
        self.loaded_model_path = None
        logger.info("Model unloaded")
    
    async def get_status(self) -> Dict:
        """Get runtime status"""
        return {
            "llama_cpp_available": self.llama_cpp_path is not None,
            "llama_cpp_path": str(self.llama_cpp_path) if self.llama_cpp_path else None,
            "model_loaded": self.loaded_model_path is not None,
            "loaded_model": str(self.loaded_model_path) if self.loaded_model_path else None,
            "context_size": self.context_size
        }


# Singleton instance
_runtime_instance: Optional[LlamaCppRuntime] = None


def get_runtime() -> LlamaCppRuntime:
    """Get global runtime instance"""
    global _runtime_instance
    if _runtime_instance is None:
        _runtime_instance = LlamaCppRuntime()
    return _runtime_instance

