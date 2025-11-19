"""Agent API routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class AgentStartRequest(BaseModel):
    """Request to start agent task"""
    prompt: str
    workspace_path: str
    context: dict = {}


class AgentStopRequest(BaseModel):
    """Request to stop agent task"""
    task_id: str


@router.post("/start")
async def start_agent(request: AgentStartRequest):
    """Start agent with a prompt"""
    # Will be implemented by orchestrator
    return {
        "status": "started",
        "task_id": "task-001",
        "message": "Agent task started"
    }


@router.post("/stop")
async def stop_agent(request: AgentStopRequest):
    """Stop running agent task"""
    return {
        "status": "stopped",
        "task_id": request.task_id
    }


@router.get("/status")
async def get_agent_status():
    """Get current agent status"""
    return {
        "state": "idle",
        "current_task": None,
        "progress": 0
    }


@router.get("/plan/current")
async def get_current_plan():
    """Get current execution plan"""
    return {
        "plan": None,
        "todos": [],
        "completed": [],
        "in_progress": None
    }

