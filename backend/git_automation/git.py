"""
Git Integration
Local Git operations
"""

from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

import structlog
from git import Repo, GitCommandError, InvalidGitRepositoryError

logger = structlog.get_logger()


class GitManager:
    """Manages local Git operations"""
    
    def __init__(self, repo_path: Optional[str] = None):
        """Initialize Git manager"""
        self.repo_path = Path(repo_path) if repo_path else None
        self.repo: Optional[Repo] = None
        
        if self.repo_path:
            self._init_or_load_repo()
        
        logger.info("Git manager initialized", repo_path=str(self.repo_path))
    
    def _init_or_load_repo(self):
        """Initialize or load existing repository"""
        try:
            # Try to load existing repo
            self.repo = Repo(self.repo_path)
            logger.info("Loaded existing Git repository")
        except InvalidGitRepositoryError:
            # Not a repo yet
            self.repo = None
            logger.debug("Not a Git repository yet")
    
    def initialize_repo(self) -> bool:
        """Initialize a new Git repository"""
        if not self.repo_path:
            logger.error("Repo path not set")
            return False
        
        try:
            self.repo = Repo.init(self.repo_path)
            logger.info("Initialized new Git repository")
            return True
        except Exception as e:
            logger.error("Failed to initialize repository", error=str(e))
            return False
    
    def is_repo(self) -> bool:
        """Check if current path is a Git repository"""
        return self.repo is not None
    
    def get_status(self) -> Dict:
        """Get repository status"""
        if not self.repo:
            return {"is_repo": False}
        
        try:
            # Get changed files
            changed_files = [item.a_path for item in self.repo.index.diff(None)]
            untracked_files = self.repo.untracked_files
            staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
            
            # Get current branch
            try:
                current_branch = self.repo.active_branch.name
            except:
                current_branch = "HEAD (detached)"
            
            # Get last commit
            try:
                last_commit = {
                    "hash": self.repo.head.commit.hexsha[:8],
                    "message": self.repo.head.commit.message.strip(),
                    "author": str(self.repo.head.commit.author),
                    "date": datetime.fromtimestamp(self.repo.head.commit.committed_date).isoformat()
                }
            except:
                last_commit = None
            
            return {
                "is_repo": True,
                "branch": current_branch,
                "changed_files": changed_files,
                "untracked_files": untracked_files,
                "staged_files": staged_files,
                "last_commit": last_commit
            }
        except Exception as e:
            logger.error("Failed to get status", error=str(e))
            return {"is_repo": True, "error": str(e)}
    
    def stage_file(self, file_path: str) -> bool:
        """Stage a single file
        
        Args:
            file_path: Path relative to repo root
        
        Returns:
            True if successful
        """
        if not self.repo:
            logger.error("No repository loaded")
            return False
        
        try:
            self.repo.index.add([file_path])
            logger.debug("File staged", file=file_path)
            return True
        except Exception as e:
            logger.error("Failed to stage file", file=file_path, error=str(e))
            return False
    
    def stage_files(self, file_paths: List[str]) -> Dict[str, bool]:
        """Stage multiple files
        
        Args:
            file_paths: List of paths relative to repo root
        
        Returns:
            Dict mapping file paths to success status
        """
        results = {}
        for file_path in file_paths:
            results[file_path] = self.stage_file(file_path)
        return results
    
    def stage_all(self) -> bool:
        """Stage all changes"""
        if not self.repo:
            logger.error("No repository loaded")
            return False
        
        try:
            self.repo.git.add(A=True)
            logger.info("All changes staged")
            return True
        except Exception as e:
            logger.error("Failed to stage all", error=str(e))
            return False
    
    def commit(self, 
              message: str,
              author_name: Optional[str] = None,
              author_email: Optional[str] = None) -> Optional[str]:
        """Create a commit
        
        Args:
            message: Commit message
            author_name: Optional author name
            author_email: Optional author email
        
        Returns:
            Commit hash if successful, None otherwise
        """
        if not self.repo:
            logger.error("No repository loaded")
            return None
        
        try:
            # Set author if provided
            if author_name and author_email:
                with self.repo.config_writer() as config:
                    config.set_value("user", "name", author_name)
                    config.set_value("user", "email", author_email)
            
            # Create commit
            commit = self.repo.index.commit(message)
            commit_hash = commit.hexsha[:8]
            
            logger.info("Commit created",
                       hash=commit_hash,
                       message=message[:50])
            
            return commit_hash
            
        except Exception as e:
            logger.error("Failed to create commit", error=str(e))
            return None
    
    def create_branch(self, branch_name: str) -> bool:
        """Create a new branch"""
        if not self.repo:
            logger.error("No repository loaded")
            return False
        
        try:
            self.repo.create_head(branch_name)
            logger.info("Branch created", branch=branch_name)
            return True
        except Exception as e:
            logger.error("Failed to create branch",
                        branch=branch_name,
                        error=str(e))
            return False
    
    def switch_branch(self, branch_name: str) -> bool:
        """Switch to a branch"""
        if not self.repo:
            logger.error("No repository loaded")
            return False
        
        try:
            self.repo.heads[branch_name].checkout()
            logger.info("Switched to branch", branch=branch_name)
            return True
        except Exception as e:
            logger.error("Failed to switch branch",
                        branch=branch_name,
                        error=str(e))
            return False
    
    def get_diff(self, staged: bool = False) -> str:
        """Get diff of changes
        
        Args:
            staged: If True, get staged changes; otherwise unstaged
        
        Returns:
            Diff text
        """
        if not self.repo:
            return ""
        
        try:
            if staged:
                diff = self.repo.index.diff("HEAD")
            else:
                diff = self.repo.index.diff(None)
            
            diff_text = "\n".join([str(d) for d in diff])
            return diff_text
        except Exception as e:
            logger.error("Failed to get diff", error=str(e))
            return ""
    
    def get_commit_history(self, max_count: int = 10) -> List[Dict]:
        """Get commit history
        
        Args:
            max_count: Maximum number of commits to return
        
        Returns:
            List of commit dicts
        """
        if not self.repo:
            return []
        
        try:
            commits = []
            for commit in self.repo.iter_commits(max_count=max_count):
                commits.append({
                    "hash": commit.hexsha[:8],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": datetime.fromtimestamp(commit.committed_date).isoformat()
                })
            return commits
        except Exception as e:
            logger.error("Failed to get commit history", error=str(e))
            return []
    
    def add_remote(self, name: str, url: str) -> bool:
        """Add a remote"""
        if not self.repo:
            logger.error("No repository loaded")
            return False
        
        try:
            # Check if remote exists
            if name in [remote.name for remote in self.repo.remotes]:
                logger.warning("Remote already exists", name=name)
                return True
            
            self.repo.create_remote(name, url)
            logger.info("Remote added", name=name, url=url)
            return True
        except Exception as e:
            logger.error("Failed to add remote", name=name, error=str(e))
            return False
    
    def push(self, 
            remote: str = "origin",
            branch: Optional[str] = None,
            force: bool = False) -> bool:
        """Push to remote
        
        Args:
            remote: Remote name
            branch: Branch name (current branch if None)
            force: Force push
        
        Returns:
            True if successful
        """
        if not self.repo:
            logger.error("No repository loaded")
            return False
        
        try:
            if branch is None:
                branch = self.repo.active_branch.name
            
            remote_obj = self.repo.remote(remote)
            
            if force:
                remote_obj.push(branch, force=True)
                logger.warning("Force pushed to remote",
                             remote=remote,
                             branch=branch)
            else:
                remote_obj.push(branch)
                logger.info("Pushed to remote",
                          remote=remote,
                          branch=branch)
            
            return True
        except Exception as e:
            logger.error("Failed to push",
                        remote=remote,
                        branch=branch,
                        error=str(e))
            return False

