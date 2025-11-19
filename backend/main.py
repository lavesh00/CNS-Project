"""
Agent Lucky Backend
Main FastAPI application entry point
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import structlog
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.agent_routes import router as agent_router
from api.model_routes import router as model_router
from api.scraper_routes import router as scraper_router
from api.github_routes import router as github_router
from models.manager import ModelManager
from rag.indexer import WorkspaceIndexer

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global instances
model_manager: ModelManager = None
workspace_indexer: WorkspaceIndexer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global model_manager, workspace_indexer
    
    logger.info("Starting Agent Lucky backend")
    
    # Initialize model manager
    model_manager = ModelManager()
    await model_manager.initialize()
    
    # Initialize workspace indexer
    workspace_indexer = WorkspaceIndexer()
    
    logger.info("Agent Lucky backend started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Agent Lucky backend")
    if model_manager:
        await model_manager.shutdown()
    if workspace_indexer:
        await workspace_indexer.shutdown()


# Create FastAPI app
app = FastAPI(
    title="Agent Lucky Backend",
    description="Production-grade agentic AI coding system backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for localhost communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:*",
        "http://127.0.0.1:*",
        "vscode-webview://*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "agent-lucky-backend",
        "version": "1.0.0"
    }


# Status endpoint
@app.get("/status")
async def get_status():
    """Get backend status"""
    model_status = await model_manager.get_status() if model_manager else {}
    indexer_status = await workspace_indexer.get_status() if workspace_indexer else {}
    
    return {
        "backend": "running",
        "models": model_status,
        "indexer": indexer_status
    }


# WebSocket for streaming responses
@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """WebSocket endpoint for streaming agent responses"""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            msg_type = data.get("type")
            
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            elif msg_type == "agent_request":
                # Handle agent request (will be implemented by orchestrator)
                await websocket.send_json({
                    "type": "agent_response",
                    "status": "processing",
                    "message": "Request received"
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}"
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        await websocket.close(code=1011, reason=str(e))


# Include API routers
app.include_router(agent_router, prefix="/agent", tags=["agent"])
app.include_router(model_router, prefix="/models", tags=["models"])
app.include_router(scraper_router, prefix="/scraper", tags=["scraper"])
app.include_router(github_router, prefix="/github", tags=["github"])


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error("Unhandled exception", 
                 path=request.url.path,
                 error=str(exc),
                 exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": request.url.path
        }
    )


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Lucky Backend")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7777, help="Port to bind to")
    parser.add_argument("--dev", action="store_true", help="Development mode with reload")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    # Configure logging level
    logging.basicConfig(level=args.log_level.upper())
    
    logger.info(
        "Starting Agent Lucky backend",
        host=args.host,
        port=args.port,
        dev_mode=args.dev
    )
    
    # Run uvicorn server
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.dev,
        log_level=args.log_level,
        access_log=True
    )


if __name__ == "__main__":
    main()

