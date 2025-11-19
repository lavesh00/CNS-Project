"""
Worker Agent
Executes TODOs and generates code patches
"""

import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

import structlog

from models.runtime import LlamaCppRuntime, GenerationConfig
from rag.retriever import Retriever

logger = structlog.get_logger()


@dataclass
class Patch:
    """A code patch/change"""
    file: str
    action: str  # create, modify, delete
    content: Optional[str] = None
    diff: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Evidence:
    """Evidence reference"""
    file: str
    lines: List[int]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class WorkResult:
    """Result of worker execution"""
    status: str  # done, partial, cannot
    explanation: str
    patches: List[Patch]
    evidence: List[Evidence]
    tests: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "explanation": self.explanation,
            "patches": [p.to_dict() for p in self.patches],
            "evidence": [e.to_dict() for e in self.evidence],
            "tests": self.tests
        }


class Worker:
    """Executes TODOs and produces code changes"""
    
    WORKER_SYSTEM_PROMPT = """You are an expert software engineer. Your job is to implement specific coding tasks.

You will receive:
1. A TODO with description and requirements
2. Relevant code context from the codebase
3. Project information

You must output ONLY valid JSON with this structure:

{
  "status": "done",
  "explanation": "Brief explanation of what was done",
  "patches": [
    {
      "file": "path/to/file.py",
      "action": "create",
      "content": "full file content here"
    }
  ],
  "evidence": [
    {
      "file": "path/to/file.py",
      "lines": [10, 25]
    }
  ],
  "tests": ["pytest tests/test_feature.py"]
}

Rules:
1. Never invent files that don't exist (unless action is "create")
2. Provide complete, working code
3. Include proper error handling
4. Follow existing code style
5. Add evidence references (file:line) for key changes
6. Suggest tests to run
7. Output ONLY JSON, no explanations outside JSON
8. Use "status": "done" when complete, "partial" when incomplete, "cannot" when impossible
"""
    
    def __init__(self,
                 runtime: Optional[LlamaCppRuntime] = None,
                 retriever: Optional[Retriever] = None):
        """Initialize worker"""
        self.runtime = runtime
        self.retriever = retriever
        
        logger.info("Worker initialized")
    
    async def execute_todo(self,
                          todo: Dict,
                          workspace_path: str,
                          project_context: Optional[Dict] = None) -> WorkResult:
        """Execute a TODO and generate patches
        
        Args:
            todo: TODO dictionary
            workspace_path: Path to workspace
            project_context: Additional context
        
        Returns:
            WorkResult with patches and evidence
        """
        logger.info("Executing TODO",
                   todo_id=todo.get("id"),
                   title=todo.get("title"))
        
        # Retrieve relevant context
        context = await self._get_context(todo, workspace_path)
        
        # Build prompt
        prompt = self._build_prompt(todo, context, project_context)
        
        # Generate solution
        if self.runtime:
            try:
                result_json = await self.runtime.generate_json(
                    prompt,
                    config=GenerationConfig(
                        temperature=0.4,
                        max_tokens=4096,
                        json_mode=True
                    )
                )
            except Exception as e:
                logger.error("Failed to generate solution", error=str(e))
                return self._create_error_result(str(e))
        else:
            return self._create_placeholder_result(todo)
        
        # Parse result
        work_result = self._parse_result(result_json)
        
        # Validate patches
        work_result = self._validate_patches(work_result, workspace_path)
        
        logger.info("TODO execution complete",
                   status=work_result.status,
                   patches=len(work_result.patches))
        
        return work_result
    
    async def _get_context(self, todo: Dict, workspace_path: str) -> str:
        """Retrieve relevant context for TODO"""
        if not self.retriever:
            return ""
        
        # Get required context files
        required_files = todo.get("required_context", [])
        
        # Search for relevant code
        query = f"{todo.get('title')} {todo.get('description')}"
        
        try:
            if required_files:
                # Hybrid retrieval: semantic + specific files
                chunks = await self.retriever.retrieve_hybrid(
                    query=query,
                    file_paths=required_files,
                    k=15
                )
            else:
                # Pure semantic search
                chunks = await self.retriever.retrieve(query=query, k=10)
            
            # Format context
            context = self.retriever.format_context(chunks, max_length=6000)
            
            logger.debug("Context retrieved",
                        chunks=len(chunks),
                        length=len(context))
            
            return context
            
        except Exception as e:
            logger.error("Failed to retrieve context", error=str(e))
            return ""
    
    def _build_prompt(self,
                     todo: Dict,
                     context: str,
                     project_context: Optional[Dict]) -> str:
        """Build worker prompt"""
        parts = [self.WORKER_SYSTEM_PROMPT]
        
        parts.append(f"\n## TODO Task")
        parts.append(f"ID: {todo.get('id')}")
        parts.append(f"Title: {todo.get('title')}")
        parts.append(f"Description: {todo.get('description')}")
        
        if todo.get('required_context'):
            parts.append(f"Required Context: {', '.join(todo.get('required_context'))}")
        
        if context:
            parts.append(f"\n## Relevant Code Context")
            parts.append(context)
        
        if project_context:
            parts.append(f"\n## Project Context")
            parts.append(json.dumps(project_context, indent=2))
        
        parts.append(f"\n## Your Task")
        parts.append("Implement the TODO described above. Output the JSON result:")
        
        return "\n".join(parts)
    
    def _parse_result(self, result_json: Dict) -> WorkResult:
        """Parse worker result JSON"""
        try:
            status = result_json.get("status", "done")
            explanation = result_json.get("explanation", "")
            
            # Parse patches
            patches = []
            for patch_data in result_json.get("patches", []):
                patch = Patch(
                    file=patch_data.get("file", ""),
                    action=patch_data.get("action", "modify"),
                    content=patch_data.get("content"),
                    diff=patch_data.get("diff")
                )
                patches.append(patch)
            
            # Parse evidence
            evidence = []
            for ev_data in result_json.get("evidence", []):
                ev = Evidence(
                    file=ev_data.get("file", ""),
                    lines=ev_data.get("lines", [])
                )
                evidence.append(ev)
            
            # Parse tests
            tests = result_json.get("tests", [])
            
            return WorkResult(
                status=status,
                explanation=explanation,
                patches=patches,
                evidence=evidence,
                tests=tests
            )
            
        except Exception as e:
            logger.error("Failed to parse result", error=str(e))
            return WorkResult(
                status="cannot",
                explanation=f"Failed to parse result: {e}",
                patches=[],
                evidence=[],
                tests=[]
            )
    
    def _validate_patches(self, result: WorkResult, workspace_path: str) -> WorkResult:
        """Validate patches against workspace"""
        workspace = Path(workspace_path)
        validated_patches = []
        
        for patch in result.patches:
            file_path = workspace / patch.file
            
            # Check action validity
            if patch.action == "modify" or patch.action == "delete":
                if not file_path.exists():
                    logger.warning("Patch targets non-existent file",
                                 file=patch.file,
                                 action=patch.action)
                    # Skip this patch
                    continue
            elif patch.action == "create":
                if file_path.exists():
                    logger.warning("Create patch targets existing file",
                                 file=patch.file)
                    # Change to modify
                    patch.action = "modify"
            
            # Validate content
            if patch.action in ["create", "modify"] and not patch.content:
                logger.warning("Patch missing content", file=patch.file)
                continue
            
            validated_patches.append(patch)
        
        result.patches = validated_patches
        return result
    
    def _create_error_result(self, error: str) -> WorkResult:
        """Create error result"""
        return WorkResult(
            status="cannot",
            explanation=f"Error: {error}",
            patches=[],
            evidence=[],
            tests=[]
        )
    
    def _create_placeholder_result(self, todo: Dict) -> WorkResult:
        """Create placeholder result when no runtime available"""
        return WorkResult(
            status="partial",
            explanation=f"TODO '{todo.get('title')}' requires implementation (no runtime available)",
            patches=[],
            evidence=[],
            tests=[]
        )
    
    async def apply_patches(self,
                          patches: List[Patch],
                          workspace_path: str) -> Dict[str, bool]:
        """Apply patches to workspace
        
        Args:
            patches: List of patches to apply
            workspace_path: Workspace root path
        
        Returns:
            Dict mapping file paths to success status
        """
        logger.info("Applying patches", count=len(patches))
        
        workspace = Path(workspace_path)
        results = {}
        
        for patch in patches:
            file_path = workspace / patch.file
            
            try:
                if patch.action == "create" or patch.action == "modify":
                    # Ensure parent directory exists
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(patch.content)
                    
                    logger.info("Patch applied",
                              file=patch.file,
                              action=patch.action)
                    results[patch.file] = True
                    
                elif patch.action == "delete":
                    if file_path.exists():
                        file_path.unlink()
                        logger.info("File deleted", file=patch.file)
                        results[patch.file] = True
                    else:
                        logger.warning("File to delete not found", file=patch.file)
                        results[patch.file] = False
                        
            except Exception as e:
                logger.error("Failed to apply patch",
                           file=patch.file,
                           error=str(e))
                results[patch.file] = False
        
        return results

