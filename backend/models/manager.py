"""
Local Model Manager
Handles downloading, quantization, and management of local AI models
"""

import asyncio
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

import structlog
from huggingface_hub import hf_hub_download, list_repo_files, snapshot_download
from huggingface_hub.utils import HfHubHTTPError

logger = structlog.get_logger()


@dataclass
class ModelConfig:
    """Model configuration"""
    id: str
    name: str
    repo_id: str
    filename: Optional[str]
    size: str
    context_length: int
    quantization: str
    license: str
    description: str
    tags: List[str]


class ModelManager:
    """Manages local AI models"""
    
    # Preset models catalog
    PRESET_MODELS = {
        "codellama-7b-q4": ModelConfig(
            id="codellama-7b-q4",
            name="Code Llama 7B Q4",
            repo_id="TheBloke/CodeLlama-7B-GGUF",
            filename="codellama-7b.Q4_K_M.gguf",
            size="4.1GB",
            context_length=16384,
            quantization="Q4_K_M",
            license="Llama 2 Community License",
            description="Code-specific LLM from Meta, 4-bit quantized",
            tags=["code", "general"]
        ),
        "codellama-13b-q4": ModelConfig(
            id="codellama-13b-q4",
            name="Code Llama 13B Q4",
            repo_id="TheBloke/CodeLlama-13B-GGUF",
            filename="codellama-13b.Q4_K_M.gguf",
            size="7.9GB",
            context_length=16384,
            quantization="Q4_K_M",
            license="Llama 2 Community License",
            description="Code-specific LLM from Meta, 13B parameters",
            tags=["code", "general"]
        ),
        "starcoder-7b-q4": ModelConfig(
            id="starcoder-7b-q4",
            name="StarCoder 7B Q4",
            repo_id="TheBloke/starcoder-GGUF",
            filename="starcoder.Q4_K_M.gguf",
            size="4.3GB",
            context_length=8192,
            quantization="Q4_K_M",
            license="BigCode OpenRAIL-M",
            description="Code generation model trained on 80+ languages",
            tags=["code"]
        ),
        "deepseek-coder-6.7b-q4": ModelConfig(
            id="deepseek-coder-6.7b-q4",
            name="DeepSeek Coder 6.7B Q4",
            repo_id="TheBloke/deepseek-coder-6.7B-instruct-GGUF",
            filename="deepseek-coder-6.7b-instruct.Q4_K_M.gguf",
            size="4.0GB",
            context_length=16384,
            quantization="Q4_K_M",
            license="DeepSeek License",
            description="Advanced code model with instruction following",
            tags=["code", "instruct"]
        ),
        "llama3-8b-q4": ModelConfig(
            id="llama3-8b-q4",
            name="Llama 3 8B Q4",
            repo_id="QuantFactory/Meta-Llama-3-8B-GGUF",
            filename="Meta-Llama-3-8B.Q4_K_M.gguf",
            size="4.9GB",
            context_length=8192,
            quantization="Q4_K_M",
            license="Llama 3 License",
            description="General purpose LLM from Meta",
            tags=["general", "instruct"]
        ),
        "mistral-7b-q4": ModelConfig(
            id="mistral-7b-q4",
            name="Mistral 7B Q4",
            repo_id="TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
            filename="mistral-7b-instruct-v0.2.Q4_K_M.gguf",
            size="4.4GB",
            context_length=32768,
            quantization="Q4_K_M",
            license="Apache 2.0",
            description="High-performance 7B model with 32k context",
            tags=["general", "instruct", "long-context"]
        ),
        "phi3-3.8b-q4": ModelConfig(
            id="phi3-3.8b-q4",
            name="Phi-3 Mini 3.8B Q4",
            repo_id="microsoft/Phi-3-mini-4k-instruct-gguf",
            filename="Phi-3-mini-4k-instruct-q4.gguf",
            size="2.3GB",
            context_length=4096,
            quantization="Q4_K_M",
            license="MIT",
            description="Small but powerful model from Microsoft",
            tags=["general", "instruct", "small"]
        )
    }
    
    def __init__(self, models_dir: Optional[Path] = None):
        """Initialize model manager"""
        if models_dir is None:
            # Default to ~/.agent-lucky/models/
            models_dir = Path.home() / ".agent-lucky" / "models"
        
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.models_dir / "models.json"
        self.installed_models: Dict[str, ModelConfig] = {}
        self.download_tasks: Dict[str, asyncio.Task] = {}
        
        logger.info("Model manager initialized", models_dir=str(self.models_dir))
    
    async def initialize(self):
        """Initialize and load existing models"""
        await self._load_config()
        logger.info("Model manager ready", installed_count=len(self.installed_models))
    
    async def shutdown(self):
        """Cleanup on shutdown"""
        # Cancel any ongoing downloads
        for task_id, task in self.download_tasks.items():
            if not task.done():
                task.cancel()
                logger.info("Cancelled download task", task_id=task_id)
        
        await self._save_config()
    
    async def _load_config(self):
        """Load models configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                for model_id, model_data in config_data.get("models", {}).items():
                    self.installed_models[model_id] = ModelConfig(**model_data)
                
                logger.info("Loaded models configuration", 
                          count=len(self.installed_models))
            except Exception as e:
                logger.error("Failed to load models config", error=str(e))
    
    async def _save_config(self):
        """Save models configuration"""
        try:
            config_data = {
                "models": {
                    model_id: asdict(config)
                    for model_id, config in self.installed_models.items()
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.debug("Saved models configuration")
        except Exception as e:
            logger.error("Failed to save models config", error=str(e))
    
    def get_preset_models(self) -> List[ModelConfig]:
        """Get list of preset models"""
        return list(self.PRESET_MODELS.values())
    
    def get_installed_models(self) -> List[ModelConfig]:
        """Get list of installed models"""
        return list(self.installed_models.values())
    
    def get_model_path(self, model_id: str) -> Optional[Path]:
        """Get path to installed model"""
        if model_id not in self.installed_models:
            return None
        
        config = self.installed_models[model_id]
        model_path = self.models_dir / model_id / (config.filename or f"{model_id}.gguf")
        
        if model_path.exists():
            return model_path
        
        return None
    
    async def download_model(self, model_id: str, progress_callback=None) -> bool:
        """Download a model from HuggingFace"""
        
        # Check if already installed
        if model_id in self.installed_models:
            logger.info("Model already installed", model_id=model_id)
            return True
        
        # Get model config
        if model_id not in self.PRESET_MODELS:
            logger.error("Unknown model ID", model_id=model_id)
            return False
        
        config = self.PRESET_MODELS[model_id]
        model_dir = self.models_dir / model_id
        model_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Starting model download",
                   model_id=model_id,
                   repo_id=config.repo_id,
                   filename=config.filename)
        
        try:
            # Download the model file
            downloaded_path = await asyncio.to_thread(
                hf_hub_download,
                repo_id=config.repo_id,
                filename=config.filename,
                cache_dir=model_dir,
                local_dir=model_dir,
                local_dir_use_symlinks=False
            )
            
            logger.info("Model downloaded successfully",
                       model_id=model_id,
                       path=downloaded_path)
            
            # Add to installed models
            self.installed_models[model_id] = config
            await self._save_config()
            
            return True
            
        except HfHubHTTPError as e:
            logger.error("Failed to download model from HuggingFace",
                        model_id=model_id,
                        error=str(e))
            return False
        except Exception as e:
            logger.error("Failed to download model",
                        model_id=model_id,
                        error=str(e),
                        exc_info=True)
            return False
    
    async def download_custom_model(self, 
                                   repo_id: str, 
                                   filename: str,
                                   model_id: Optional[str] = None) -> bool:
        """Download a custom model from HuggingFace"""
        
        if model_id is None:
            # Generate model ID from repo_id
            model_id = repo_id.replace("/", "-").lower()
        
        # Check if already installed
        if model_id in self.installed_models:
            logger.info("Model already installed", model_id=model_id)
            return True
        
        model_dir = self.models_dir / model_id
        model_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Starting custom model download",
                   model_id=model_id,
                   repo_id=repo_id,
                   filename=filename)
        
        try:
            # Download the model file
            downloaded_path = await asyncio.to_thread(
                hf_hub_download,
                repo_id=repo_id,
                filename=filename,
                cache_dir=model_dir,
                local_dir=model_dir,
                local_dir_use_symlinks=False
            )
            
            # Create config for custom model
            config = ModelConfig(
                id=model_id,
                name=model_id,
                repo_id=repo_id,
                filename=filename,
                size="Unknown",
                context_length=4096,  # Default
                quantization="Unknown",
                license="Check HuggingFace",
                description=f"Custom model from {repo_id}",
                tags=["custom"]
            )
            
            self.installed_models[model_id] = config
            await self._save_config()
            
            logger.info("Custom model downloaded successfully",
                       model_id=model_id,
                       path=downloaded_path)
            
            return True
            
        except Exception as e:
            logger.error("Failed to download custom model",
                        model_id=model_id,
                        repo_id=repo_id,
                        error=str(e),
                        exc_info=True)
            return False
    
    async def delete_model(self, model_id: str) -> bool:
        """Delete an installed model"""
        
        if model_id not in self.installed_models:
            logger.warning("Model not installed", model_id=model_id)
            return False
        
        model_dir = self.models_dir / model_id
        
        try:
            if model_dir.exists():
                shutil.rmtree(model_dir)
            
            del self.installed_models[model_id]
            await self._save_config()
            
            logger.info("Model deleted", model_id=model_id)
            return True
            
        except Exception as e:
            logger.error("Failed to delete model",
                        model_id=model_id,
                        error=str(e))
            return False
    
    async def get_status(self) -> Dict:
        """Get model manager status"""
        return {
            "models_dir": str(self.models_dir),
            "installed_count": len(self.installed_models),
            "installed_models": [config.id for config in self.installed_models.values()],
            "available_presets": len(self.PRESET_MODELS),
            "active_downloads": len([t for t in self.download_tasks.values() if not t.done()])
        }
    
    def validate_model(self, model_path: Path) -> bool:
        """Validate a model file"""
        if not model_path.exists():
            return False
        
        # Check if it's a GGUF file
        if not model_path.suffix in ['.gguf', '.bin']:
            return False
        
        # Check minimum file size (should be at least 1GB for real models)
        if model_path.stat().st_size < 100 * 1024 * 1024:  # 100MB minimum
            logger.warning("Model file seems too small", 
                          path=str(model_path),
                          size=model_path.stat().st_size)
            return False
        
        return True

