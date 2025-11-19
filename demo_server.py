"""
Agent Lucky Demo Server
Simplified version to demonstrate the system
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Agent Lucky Demo",
    description="Demo of Agent Lucky agentic AI system",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AgentRequest(BaseModel):
    prompt: str
    workspace_path: str


@app.get("/")
async def root():
    return {
        "message": "🍀 Welcome to Agent Lucky!",
        "status": "running",
        "version": "1.0.0 Demo"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "agent-lucky-demo",
        "version": "1.0.0"
    }


@app.get("/status")
async def status():
    """System status"""
    return {
        "backend": "running",
        "models": {
            "available": ["codellama-7b-q4", "codellama-13b-q4", "starcoder-7b-q4"],
            "installed": [],
            "status": "ready_for_download"
        },
        "features": {
            "planner": "✅ Ready",
            "worker": "✅ Ready",
            "summarizer": "✅ Ready",
            "rag": "✅ Ready",
            "git": "✅ Ready",
            "github": "✅ Ready",
            "scraper": "✅ Ready",
            "mcp": "✅ Ready"
        }
    }


@app.post("/agent/start")
async def start_agent(request: AgentRequest):
    """Start agent task"""
    return {
        "status": "started",
        "task_id": "demo-task-001",
        "message": f"Agent will process: {request.prompt}",
        "workspace": request.workspace_path,
        "plan": {
            "goal": request.prompt,
            "todos": [
                {"id": "todo-1", "title": "Analyze requirements", "status": "pending"},
                {"id": "todo-2", "title": "Generate code", "status": "pending"},
                {"id": "todo-3", "title": "Create tests", "status": "pending"}
            ]
        },
        "note": "This is a demo. Full implementation requires model installation."
    }


@app.get("/agent/status")
async def agent_status():
    """Get agent status"""
    return {
        "state": "idle",
        "current_task": None,
        "progress": 0,
        "message": "Ready to receive tasks"
    }


@app.get("/models/list")
async def list_models():
    """List available models"""
    return {
        "installed": [],
        "available": [
            {
                "id": "codellama-7b-q4",
                "name": "Code Llama 7B Q4",
                "size": "4.1GB",
                "context_length": 16384,
                "description": "Fast code generation"
            },
            {
                "id": "codellama-13b-q4",
                "name": "Code Llama 13B Q4",
                "size": "7.9GB",
                "context_length": 16384,
                "description": "High quality code generation"
            },
            {
                "id": "deepseek-coder-6.7b-q4",
                "name": "DeepSeek Coder 6.7B Q4",
                "size": "4.0GB",
                "context_length": 16384,
                "description": "Advanced code understanding"
            }
        ]
    }


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🍀 Agent Lucky Demo Server")
    print("="*60)
    print("\n✅ Server starting on http://127.0.0.1:7777")
    print("\n📚 Available endpoints:")
    print("   GET  /           - Welcome message")
    print("   GET  /health     - Health check")
    print("   GET  /status     - System status")
    print("   POST /agent/start - Start agent task")
    print("   GET  /agent/status - Agent status")
    print("   GET  /models/list - List models")
    print("\n🔗 Try: http://127.0.0.1:7777/status")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="127.0.0.1", port=7777, log_level="info")


