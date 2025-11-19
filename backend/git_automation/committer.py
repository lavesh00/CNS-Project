"""
Committer
Handles commit strategies (per-file, per-TODO, batch)
"""

from typing import List, Dict, Optional
from enum import Enum
from pathlib import Path

import structlog

from .git import GitManager

logger = structlog.get_logger()


class CommitMode(str, Enum):
    """Commit strategy modes"""
    PER_FILE = "per-file"
    PER_TODO = "per-todo"
    BATCH = "batch"


class Committer:
    """Manages commits with different strategies"""
    
    def __init__(self, git_manager: GitManager, mode: CommitMode = CommitMode.PER_TODO):
        """Initialize committer"""
        self.git_manager = git_manager
        self.mode = mode
        self.pending_changes: List[Dict] = []
        
        logger.info("Committer initialized", mode=mode)
    
    def set_mode(self, mode: CommitMode):
        """Change commit mode"""
        self.mode = mode
        logger.info("Commit mode changed", mode=mode)
    
    async def add_change(self,
                        file_path: str,
                        action: str,
                        todo_id: Optional[str] = None,
                        description: Optional[str] = None):
        """Add a change to be committed
        
        Args:
            file_path: Path to changed file
            action: create, modify, or delete
            todo_id: Associated TODO ID
            description: Change description
        """
        change = {
            "file": file_path,
            "action": action,
            "todo_id": todo_id,
            "description": description or f"{action} {file_path}"
        }
        
        self.pending_changes.append(change)
        
        logger.debug("Change added",
                    file=file_path,
                    action=action,
                    todo_id=todo_id)
        
        # Auto-commit based on mode
        if self.mode == CommitMode.PER_FILE:
            await self.commit_file(file_path, action, description)
    
    async def commit_file(self,
                         file_path: str,
                         action: str,
                         description: Optional[str] = None) -> Optional[str]:
        """Commit a single file
        
        Args:
            file_path: Path to file
            action: create, modify, or delete
            description: Optional description
        
        Returns:
            Commit hash if successful
        """
        # Stage file
        success = self.git_manager.stage_file(file_path)
        if not success:
            logger.error("Failed to stage file", file=file_path)
            return None
        
        # Create commit message
        message = self._format_commit_message(
            title=f"{action.capitalize()} {Path(file_path).name}",
            files=[file_path],
            description=description
        )
        
        # Commit
        commit_hash = self.git_manager.commit(message)
        
        if commit_hash:
            logger.info("File committed",
                       file=file_path,
                       hash=commit_hash)
        
        return commit_hash
    
    async def commit_todo(self, todo_id: str, todo_title: str) -> Optional[str]:
        """Commit all changes for a TODO
        
        Args:
            todo_id: TODO ID
            todo_title: TODO title
        
        Returns:
            Commit hash if successful
        """
        # Find changes for this TODO
        todo_changes = [
            c for c in self.pending_changes
            if c.get("todo_id") == todo_id
        ]
        
        if not todo_changes:
            logger.warning("No changes for TODO", todo_id=todo_id)
            return None
        
        # Stage files
        files = [c["file"] for c in todo_changes]
        results = self.git_manager.stage_files(files)
        
        successful_files = [f for f, success in results.items() if success]
        
        if not successful_files:
            logger.error("No files staged for TODO", todo_id=todo_id)
            return None
        
        # Create commit message
        message = self._format_commit_message(
            title=todo_title,
            files=successful_files,
            description=f"Completed TODO: {todo_id}"
        )
        
        # Commit
        commit_hash = self.git_manager.commit(message)
        
        if commit_hash:
            # Remove committed changes from pending
            self.pending_changes = [
                c for c in self.pending_changes
                if c not in todo_changes
            ]
            
            logger.info("TODO committed",
                       todo_id=todo_id,
                       files=len(successful_files),
                       hash=commit_hash)
        
        return commit_hash
    
    async def commit_batch(self, message: str) -> Optional[str]:
        """Commit all pending changes in one batch
        
        Args:
            message: Batch commit message
        
        Returns:
            Commit hash if successful
        """
        if not self.pending_changes:
            logger.warning("No pending changes to commit")
            return None
        
        # Stage all changed files
        files = [c["file"] for c in self.pending_changes]
        results = self.git_manager.stage_files(files)
        
        successful_files = [f for f, success in results.items() if success]
        
        if not successful_files:
            logger.error("No files staged for batch")
            return None
        
        # Create commit message
        full_message = self._format_commit_message(
            title=message,
            files=successful_files,
            description="Batch commit"
        )
        
        # Commit
        commit_hash = self.git_manager.commit(full_message)
        
        if commit_hash:
            self.pending_changes.clear()
            logger.info("Batch committed",
                       files=len(successful_files),
                       hash=commit_hash)
        
        return commit_hash
    
    def _format_commit_message(self,
                              title: str,
                              files: List[str],
                              description: Optional[str] = None) -> str:
        """Format commit message
        
        Args:
            title: Commit title
            files: List of files changed
            description: Optional description
        
        Returns:
            Formatted commit message
        """
        message_parts = [f"[Agent] {title}"]
        
        if description:
            message_parts.append(f"\n{description}")
        
        # Add file list (limit to avoid huge messages)
        if len(files) <= 10:
            message_parts.append(f"\nFiles changed:")
            for file in files:
                message_parts.append(f"- {file}")
        else:
            message_parts.append(f"\n{len(files)} files changed")
        
        message_parts.append("\nGenerated by Agent Lucky")
        
        return "\n".join(message_parts)
    
    def get_pending_changes(self) -> List[Dict]:
        """Get list of pending changes"""
        return self.pending_changes.copy()
    
    def clear_pending(self):
        """Clear pending changes"""
        self.pending_changes.clear()
        logger.info("Pending changes cleared")

