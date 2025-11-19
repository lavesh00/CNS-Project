"""Model management API routes"""

import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict
import structlog

from backend.models.manager import ModelManager

logger = structlog.get_logger()
router = APIRouter()

# Global model manager instance
model_manager = ModelManager()

# Global download status tracker
download_status: Dict[str, Dict] = {}


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


async def download_model_background(model_id: str):
    """Background task to download model"""
    try:
        download_status[model_id] = {
            "status": "downloading",
            "progress": 0,
            "message": "Starting download..."
        }
        
        logger.info(f"Starting download for model: {model_id}")
        
        # Simulate download progress (replace with actual download)
        for i in range(0, 101, 10):
            download_status[model_id]["progress"] = i
            download_status[model_id]["message"] = f"Downloading... {i}%"
            await asyncio.sleep(1)  # Simulate work
        
        # Check if model exists in preset
        if model_id in model_manager.PRESET_MODELS:
            try:
                model_path = await asyncio.to_thread(
                    model_manager.download_model,
                    model_id
                )
                
                download_status[model_id] = {
                    "status": "completed",
                    "progress": 100,
                    "message": "Download completed!",
                    "path": str(model_path)
                }
                logger.info(f"Model {model_id} downloaded successfully to {model_path}")
                
            except Exception as e:
                download_status[model_id] = {
                    "status": "error",
                    "progress": 0,
                    "message": f"Download failed: {str(e)}"
                }
                logger.error(f"Failed to download model {model_id}: {e}")
        else:
            download_status[model_id] = {
                "status": "error",
                "progress": 0,
                "message": f"Model {model_id} not found in preset models"
            }
            
    except Exception as e:
        download_status[model_id] = {
            "status": "error",
            "progress": 0,
            "message": str(e)
        }
        logger.error(f"Error in download_model_background: {e}")


@router.get("/list")
async def list_models():
    """List available models"""
    installed = []
    available = []
    
    # Get installed models
    installed_models = model_manager.list_installed()
    for model_path in installed_models:
        model_id = model_path.stem
        installed.append({
            "id": model_id,
            "name": model_id,
            "size": "Unknown",
            "context_length": 4096,
            "status": "installed",
            "path": str(model_path)
        })
    
    # Get available preset models
    for model_id, config in model_manager.PRESET_MODELS.items():
        available.append({
            "id": model_id,
            "name": config.name,
            "size": config.size,
            "context_length": config.context_length,
            "status": "available",
            "description": config.description
        })
    
    return {
        "installed": installed,
        "available": available
    }


@router.post("/download")
async def download_model(request: ModelDownloadRequest, background_tasks: BackgroundTasks):
    """Download a model"""
    model_id = request.model_id
    
    # Check if already downloading
    if model_id in download_status and download_status[model_id]["status"] == "downloading":
        return {
            "status": "already_downloading",
            "model_id": model_id,
            "message": "Model is already being downloaded"
        }
    
    # Check if model exists
    if model_id not in model_manager.PRESET_MODELS:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    # Start download in background
    background_tasks.add_task(download_model_background, model_id)
    
    download_status[model_id] = {
        "status": "queued",
        "progress": 0,
        "message": "Download queued"
    }
    
    return {
        "status": "started",
        "model_id": model_id,
        "download_id": f"download-{model_id}",
        "message": "Download started in background"
    }


@router.get("/status/{model_id}")
async def get_model_status(model_id: str):
    """Get model download/load status"""
    
    # Check if downloading
    if model_id in download_status:
        return {
            "model_id": model_id,
            **download_status[model_id]
        }
    
    # Check if installed
    installed = model_manager.list_installed()
    for model_path in installed:
        if model_id in str(model_path):
            return {
                "model_id": model_id,
                "status": "installed",
                "progress": 100,
                "message": "Model is installed",
                "path": str(model_path)
            }
    
    # Not downloaded
    return {
        "model_id": model_id,
        "status": "not_downloaded",
        "progress": 0,
        "message": "Model not downloaded"
    }


@router.get("/downloads")
async def get_all_downloads():
    """Get status of all active downloads"""
    return {
        "downloads": download_status
    }


@router.delete("/{model_id}")
async def delete_model(model_id: str):
    """Delete an installed model"""
    try:
        # Find and delete the model file
        installed = model_manager.list_installed()
        for model_path in installed:
            if model_id in str(model_path):
                model_path.unlink()
                logger.info(f"Deleted model: {model_path}")
                
                # Clear from download status
                if model_id in download_status:
                    del download_status[model_id]
                
                return {
                    "status": "deleted",
                    "model_id": model_id,
                    "message": "Model deleted successfully"
                }
        
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

