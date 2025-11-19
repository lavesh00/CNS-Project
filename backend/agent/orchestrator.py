"""
Orchestrator
Manages the Planner → Worker → Summarizer loop
"""

import asyncio
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

import structlog

from .planner import Planner, Plan, TODO
from .worker import Worker, WorkResult
from .summarizer import Summarizer, Summary
from models.runtime import LlamaCppRuntime
from rag.retriever import Retriever

logger = structlog.get_logger()


@dataclass
class AgentState:
    """Current state of the agent"""
    status: str  # idle, planning, working, summarizing, completed, error
    current_plan: Optional[Plan] = None
    current_todo: Optional[TODO] = None
    summary: Optional[Summary] = None
    progress: float = 0.0
    
    def to_dict(self) -> Dict:
        result = {
            "status": self.status,
            "progress": self.progress
        }
        if self.current_plan:
            result["plan"] = self.current_plan.to_dict()
        if self.current_todo:
            result["current_todo"] = self.current_todo.to_dict()
        if self.summary:
            result["summary"] = self.summary.to_dict()
        return result


class Orchestrator:
    """Orchestrates the agentic loop"""
    
    def __init__(self,
                 runtime: LlamaCppRuntime,
                 retriever: Retriever):
        """Initialize orchestrator"""
        self.planner = Planner(runtime)
        self.worker = Worker(runtime, retriever)
        self.summarizer = Summarizer(runtime)
        
        self.state = AgentState(status="idle")
        self.work_history: List[WorkResult] = []
        self.logs: List[str] = []
        self.code_changes: List[Dict] = []
        
        self.stop_requested = False
        self.progress_callback: Optional[Callable] = None
        
        logger.info("Orchestrator initialized")
    
    async def execute(self,
                     prompt: str,
                     workspace_path: str,
                     max_iterations: int = 50,
                     progress_callback: Optional[Callable] = None) -> Dict:
        """Execute agentic loop
        
        Args:
            prompt: User's high-level request
            workspace_path: Path to workspace
            max_iterations: Maximum number of TODO iterations
            progress_callback: Optional callback for progress updates
        
        Returns:
            Final execution summary
        """
        self.progress_callback = progress_callback
        self.stop_requested = False
        
        logger.info("Starting agent execution",
                   prompt=prompt,
                   workspace=workspace_path)
        
        try:
            # Phase 1: Planning
            await self._update_state("planning")
            workspace_context = await self._get_workspace_context(workspace_path)
            plan = await self.planner.create_plan(prompt, workspace_context)
            self.state.current_plan = plan
            
            logger.info("Plan created", todos=len(plan.todos))
            
            # Phase 2: Execution loop
            iteration = 0
            while not self.planner.is_plan_complete() and iteration < max_iterations:
                if self.stop_requested:
                    logger.info("Stop requested, halting execution")
                    break
                
                iteration += 1
                
                # Get next TODO
                next_todo = self.planner.get_next_todo()
                if not next_todo:
                    logger.warning("No more actionable TODOs")
                    break
                
                self.state.current_todo = next_todo
                await self._update_state("working")
                
                logger.info("Executing TODO",
                           iteration=iteration,
                           todo_id=next_todo.id,
                           title=next_todo.title)
                
                # Execute TODO
                self.planner.mark_todo_status(next_todo.id, "in_progress")
                
                work_result = await self.worker.execute_todo(
                    todo=next_todo.to_dict(),
                    workspace_path=workspace_path,
                    project_context=workspace_context
                )
                
                self.work_history.append(work_result)
                
                # Apply patches
                if work_result.patches:
                    patch_results = await self.worker.apply_patches(
                        work_result.patches,
                        workspace_path
                    )
                    
                    # Track changes
                    for patch in work_result.patches:
                        self.code_changes.append({
                            "file": patch.file,
                            "action": patch.action,
                            "description": f"{patch.action} {patch.file}"
                        })
                    
                    logger.info("Patches applied",
                               successful=sum(patch_results.values()),
                               total=len(patch_results))
                
                # Update TODO status
                if work_result.status == "done":
                    self.planner.mark_todo_status(next_todo.id, "completed")
                elif work_result.status == "cannot":
                    self.planner.mark_todo_status(next_todo.id, "failed")
                    logger.warning("TODO failed", todo_id=next_todo.id)
                
                # Update progress
                self.state.progress = self._calculate_progress()
                await self._notify_progress()
            
            # Phase 3: Summarization
            await self._update_state("summarizing")
            summary = await self.summarizer.summarize(
                logs=self.logs,
                work_results=[r.to_dict() for r in self.work_history],
                code_changes=self.code_changes
            )
            self.state.summary = summary
            
            logger.info("Summarization complete")
            
            # Mark complete
            await self._update_state("completed")
            
            return {
                "status": "success",
                "plan": plan.to_dict(),
                "summary": summary.to_dict(),
                "iterations": iteration,
                "files_changed": len(set(c["file"] for c in self.code_changes))
            }
            
        except Exception as e:
            logger.error("Execution failed", error=str(e), exc_info=True)
            await self._update_state("error")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _get_workspace_context(self, workspace_path: str) -> Dict:
        """Get workspace context information"""
        workspace = Path(workspace_path)
        
        # Gather basic info
        context = {
            "workspace_path": str(workspace),
            "exists": workspace.exists(),
            "is_git_repo": (workspace / ".git").exists()
        }
        
        # Detect project type
        if (workspace / "package.json").exists():
            context["project_type"] = "node"
        elif (workspace / "requirements.txt").exists() or (workspace / "pyproject.toml").exists():
            context["project_type"] = "python"
        else:
            context["project_type"] = "unknown"
        
        return context
    
    def _calculate_progress(self) -> float:
        """Calculate progress percentage"""
        if not self.state.current_plan:
            return 0.0
        
        total = len(self.state.current_plan.todos)
        if total == 0:
            return 100.0
        
        completed = sum(
            1 for todo in self.state.current_plan.todos
            if todo.status == "completed"
        )
        
        return (completed / total) * 100.0
    
    async def _update_state(self, status: str):
        """Update agent state"""
        self.state.status = status
        await self._notify_progress()
        
        log_msg = f"Agent state: {status}"
        self.logs.append(log_msg)
        logger.info("State updated", status=status)
    
    async def _notify_progress(self):
        """Notify progress callback"""
        if self.progress_callback:
            try:
                if asyncio.iscoroutinefunction(self.progress_callback):
                    await self.progress_callback(self.state.to_dict())
                else:
                    self.progress_callback(self.state.to_dict())
            except Exception as e:
                logger.error("Progress callback failed", error=str(e))
    
    def request_stop(self):
        """Request graceful stop"""
        logger.info("Stop requested")
        self.stop_requested = True
    
    def get_state(self) -> Dict:
        """Get current state"""
        return self.state.to_dict()
    
    def get_logs(self) -> List[str]:
        """Get execution logs"""
        return self.logs.copy()

