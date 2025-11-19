"""
Configuration Management
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Model settings
    model_path: Path = Path.home() / ".agent-lucky" / "models"
    default_model: str = "codellama-13b-q4"
    
    # Backend settings
    backend_host: str = "127.0.0.1"
    backend_port: int = 7777
    log_level: str = "info"
    
    # Git settings
    git_commit_mode: str = "per-todo"  # per-file, per-todo, batch
    git_auto_push: bool = False
    
    # GitHub settings
    github_token: Optional[str] = None
    
    # RAG settings
    rag_enabled: bool = True
    rag_chunk_size: int = 1000
    rag_overlap: int = 200
    
    # Scraper settings
    scraper_respect_robots: bool = True
    scraper_max_depth: int = 2
    
    # Test sandbox
    use_docker: bool = True
    
    class Config:
        env_prefix = "AGENT_LUCKY_"
        case_sensitive = False
        env_file = ".env"


# Global settings instance
settings = Settings()

