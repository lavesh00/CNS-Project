"""
Planner Agent
Creates structured execution plans from high-level prompts
"""

import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

import structlog

from models.runtime import LlamaCppRuntime, GenerationConfig

logger = structlog.get_logger()


@dataclass
class TODO:
    """A single TODO item in the plan"""
    id: str
    title: str
    description: str
    required_context: List[str]
    estimated_steps: int
    dependencies: List[str]
    status: str = "pending"  # pending, in_progress, completed, failed
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Plan:
    """Execution plan"""
    goal: str
    todos: List[TODO]
    context: Dict
    
    def to_dict(self) -> Dict:
        return {
            "goal": self.goal,
            "todos": [todo.to_dict() for todo in self.todos],
            "context": self.context
        }


class Planner:
    """Creates structured plans from prompts"""
    
    PLANNING_SYSTEM_PROMPT = """You are an expert software architect and planner. Your job is to break down high-level coding tasks into structured, actionable TODO items.

You must output ONLY valid JSON with no additional text. The JSON should have this structure:

{
  "goal": "Brief description of the overall goal",
  "todos": [
    {
      "id": "todo-1",
      "title": "Short title",
      "description": "Detailed description of what needs to be done",
      "required_context": ["list", "of", "files", "or", "context", "needed"],
      "estimated_steps": 3,
      "dependencies": []
    }
  ]
}

Rules:
1. Break complex tasks into atomic, independent steps
2. Each TODO should be completable in one pass
3. Include file creation, modification, and deletion tasks
4. Avoid circular dependencies
5. Be specific about required context (files, APIs, docs)
6. Estimate reasonable number of steps
7. Output ONLY JSON, no explanations
"""
    
    def __init__(self, runtime: Optional[LlamaCppRuntime] = None):
        """Initialize planner"""
        self.runtime = runtime
        self.current_plan: Optional[Plan] = None
        
        logger.info("Planner initialized")
    
    async def create_plan(self,
                         prompt: str,
                         workspace_context: Optional[Dict] = None,
                         project_summary: Optional[str] = None) -> Plan:
        """Create an execution plan from a prompt
        
        Args:
            prompt: User's high-level request
            workspace_context: Information about current workspace
            project_summary: Summary of project state
        
        Returns:
            Structured Plan object
        """
        logger.info("Creating plan", prompt_length=len(prompt))
        
        # Build context
        context_parts = [f"User Request: {prompt}"]
        
        if workspace_context:
            context_parts.append(f"\nWorkspace Context: {json.dumps(workspace_context, indent=2)}")
        
        if project_summary:
            context_parts.append(f"\nProject Summary: {project_summary}")
        
        full_prompt = f"{self.PLANNING_SYSTEM_PROMPT}\n\n{chr(10).join(context_parts)}\n\nGenerate the JSON plan:"
        
        # Generate plan using LLM
        if self.runtime:
            config = GenerationConfig(
                temperature=0.3,  # Lower temperature for more focused planning
                max_tokens=2048,
                json_mode=True
            )
            
            try:
                plan_json = await self.runtime.generate_json(full_prompt, config=config)
            except Exception as e:
                logger.error("Failed to generate plan with LLM", error=str(e))
                # Fallback to simple plan
                plan_json = self._create_fallback_plan(prompt)
        else:
            # No runtime, use fallback
            plan_json = self._create_fallback_plan(prompt)
        
        # Parse and validate plan
        plan = self._parse_plan(plan_json, prompt)
        
        # Store current plan
        self.current_plan = plan
        
        logger.info("Plan created",
                   goal=plan.goal,
                   todo_count=len(plan.todos))
        
        return plan
    
    def _parse_plan(self, plan_json: Dict, original_prompt: str) -> Plan:
        """Parse and validate plan JSON"""
        try:
            goal = plan_json.get("goal", original_prompt)
            todos_data = plan_json.get("todos", [])
            
            # Create TODO objects
            todos = []
            for i, todo_data in enumerate(todos_data):
                todo = TODO(
                    id=todo_data.get("id", f"todo-{i+1}"),
                    title=todo_data.get("title", f"Task {i+1}"),
                    description=todo_data.get("description", ""),
                    required_context=todo_data.get("required_context", []),
                    estimated_steps=todo_data.get("estimated_steps", 1),
                    dependencies=todo_data.get("dependencies", [])
                )
                todos.append(todo)
            
            # Validate dependencies
            todo_ids = {todo.id for todo in todos}
            for todo in todos:
                todo.dependencies = [dep for dep in todo.dependencies if dep in todo_ids]
            
            plan = Plan(
                goal=goal,
                todos=todos,
                context={}
            )
            
            logger.debug("Plan parsed successfully", todos=len(todos))
            return plan
            
        except Exception as e:
            logger.error("Failed to parse plan", error=str(e))
            # Return minimal plan
            return Plan(
                goal=original_prompt,
                todos=[TODO(
                    id="todo-1",
                    title="Execute task",
                    description=original_prompt,
                    required_context=[],
                    estimated_steps=1,
                    dependencies=[]
                )],
                context={}
            )
    
    def _create_fallback_plan(self, prompt: str) -> Dict:
        """Create a simple fallback plan"""
        return {
            "goal": prompt,
            "todos": [
                {
                    "id": "todo-1",
                    "title": "Analyze request",
                    "description": f"Analyze and understand the request: {prompt}",
                    "required_context": [],
                    "estimated_steps": 1,
                    "dependencies": []
                },
                {
                    "id": "todo-2",
                    "title": "Implement solution",
                    "description": "Implement the requested changes",
                    "required_context": [],
                    "estimated_steps": 3,
                    "dependencies": ["todo-1"]
                },
                {
                    "id": "todo-3",
                    "title": "Verify and test",
                    "description": "Verify implementation and run tests",
                    "required_context": [],
                    "estimated_steps": 1,
                    "dependencies": ["todo-2"]
                }
            ]
        }
    
    def get_next_todo(self) -> Optional[TODO]:
        """Get the next pending TODO with satisfied dependencies"""
        if not self.current_plan:
            return None
        
        completed_ids = {
            todo.id for todo in self.current_plan.todos
            if todo.status == "completed"
        }
        
        for todo in self.current_plan.todos:
            if todo.status == "pending":
                # Check if dependencies are satisfied
                deps_satisfied = all(dep in completed_ids for dep in todo.dependencies)
                
                if deps_satisfied:
                    return todo
        
        return None
    
    def mark_todo_status(self, todo_id: str, status: str):
        """Update TODO status"""
        if not self.current_plan:
            return
        
        for todo in self.current_plan.todos:
            if todo.id == todo_id:
                todo.status = status
                logger.debug("TODO status updated", 
                           todo_id=todo_id,
                           status=status)
                break
    
    def is_plan_complete(self) -> bool:
        """Check if all TODOs are completed"""
        if not self.current_plan:
            return True
        
        return all(
            todo.status in ["completed", "failed"]
            for todo in self.current_plan.todos
        )
    
    def get_plan_summary(self) -> Dict:
        """Get summary of current plan"""
        if not self.current_plan:
            return {"status": "no_plan"}
        
        status_counts = {}
        for todo in self.current_plan.todos:
            status_counts[todo.status] = status_counts.get(todo.status, 0) + 1
        
        return {
            "goal": self.current_plan.goal,
            "total_todos": len(self.current_plan.todos),
            "status_counts": status_counts,
            "completed": self.is_plan_complete()
        }

