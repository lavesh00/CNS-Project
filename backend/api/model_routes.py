"""Model management API routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ModelDownloadRequest(BaseModel):
    """Request to download a model"""
    model_id: str
    quantization: Optional[str] = "Q4_K_M"


class ModelInfo(BaseModel):
    """Model information"""
    id: str
    name: str
    size: str
    context_length: int
    status: str


@router.get("/list")
async def list_models():
    """List available models"""
    return {
        "installed": [],
        "available": [
            {
                "id": "codellama-7b",
                "name": "Code Llama 7B",
                "size": "7B",
                "context_length": 16384,
                "status": "available"
            },
            {
                "id": "codellama-13b",
                "name": "Code Llama 13B",
                "size": "13B",
                "context_length": 16384,
                "status": "available"
            },
            {
                "id": "starcoder-7b",
                "name": "StarCoder 7B",
                "size": "7B",
                "context_length": 8192,
                "status": "available"
            },
            {
                "id": "deepseek-coder-6.7b",
                "name": "DeepSeek Coder 6.7B",
                "size": "6.7B",
                "context_length": 16384,
                "status": "available"
            }
        ]
    }


@router.post("/download")
async def download_model(request: ModelDownloadRequest):
    """Download a model"""
    return {
        "status": "started",
        "model_id": request.model_id,
        "download_id": f"download-{request.model_id}"
    }


@router.get("/status/{model_id}")
async def get_model_status(model_id: str):
    """Get model download/load status"""
    return {
        "model_id": model_id,
        "status": "not_downloaded",
        "progress": 0
    }


@router.delete("/{model_id}")
async def delete_model(model_id: str):
    """Delete an installed model"""
    return {
        "status": "deleted",
        "model_id": model_id
    }

