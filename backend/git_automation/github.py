"""
GitHub Integration
Repository creation, push, PR management
"""

from typing import Optional, Dict, List
import os

import structlog
from github import Github, GithubException
from github.Repository import Repository

logger = structlog.get_logger()


class GitHubManager:
    """Manages GitHub operations"""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub manager
        
        Args:
            token: GitHub personal access token
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.github: Optional[Github] = None
        self.authenticated_user = None
        
        if self.token:
            self._authenticate()
        
        logger.info("GitHub manager initialized", 
                   authenticated=self.github is not None)
    
    def _authenticate(self):
        """Authenticate with GitHub"""
        try:
            self.github = Github(self.token)
            self.authenticated_user = self.github.get_user()
            logger.info("GitHub authenticated", user=self.authenticated_user.login)
        except GithubException as e:
            logger.error("GitHub authentication failed", error=str(e))
            self.github = None
    
    def set_token(self, token: str):
        """Set GitHub token"""
        self.token = token
        self._authenticate()
    
    def is_authenticated(self) -> bool:
        """Check if authenticated"""
        return self.github is not None and self.authenticated_user is not None
    
    def get_user_info(self) -> Optional[Dict]:
        """Get authenticated user info"""
        if not self.authenticated_user:
            return None
        
        try:
            return {
                "login": self.authenticated_user.login,
                "name": self.authenticated_user.name,
                "email": self.authenticated_user.email,
                "avatar_url": self.authenticated_user.avatar_url
            }
        except Exception as e:
            logger.error("Failed to get user info", error=str(e))
            return None
    
    def create_repository(self,
                         name: str,
                         description: str = "",
                         private: bool = False) -> Optional[Repository]:
        """Create a new GitHub repository
        
        Args:
            name: Repository name
            description: Repository description
            private: Make repository private
        
        Returns:
            Repository object if successful
        """
        if not self.github:
            logger.error("Not authenticated")
            return None
        
        try:
            repo = self.authenticated_user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=False  # Don't auto-initialize
            )
            
            logger.info("Repository created",
                       name=name,
                       url=repo.html_url)
            
            return repo
        except GithubException as e:
            logger.error("Failed to create repository",
                        name=name,
                        error=str(e))
            return None
    
    def get_repository(self, full_name: str) -> Optional[Repository]:
        """Get repository by full name (owner/repo)"""
        if not self.github:
            logger.error("Not authenticated")
            return None
        
        try:
            repo = self.github.get_repo(full_name)
            logger.debug("Repository fetched", name=full_name)
            return repo
        except GithubException as e:
            logger.error("Failed to get repository",
                        name=full_name,
                        error=str(e))
            return None
    
    def create_pull_request(self,
                           repo: Repository,
                           title: str,
                           body: str,
                           head_branch: str,
                           base_branch: str = "main") -> Optional[Dict]:
        """Create a pull request
        
        Args:
            repo: Repository object
            title: PR title
            body: PR description
            head_branch: Source branch
            base_branch: Target branch
        
        Returns:
            PR info dict if successful
        """
        try:
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            
            pr_info = {
                "number": pr.number,
                "url": pr.html_url,
                "state": pr.state,
                "title": pr.title
            }
            
            logger.info("Pull request created",
                       number=pr.number,
                       url=pr.html_url)
            
            return pr_info
        except GithubException as e:
            logger.error("Failed to create pull request", error=str(e))
            return None
    
    def add_pr_comment(self,
                      repo: Repository,
                      pr_number: int,
                      comment: str) -> bool:
        """Add comment to pull request"""
        try:
            pr = repo.get_pull(pr_number)
            pr.create_issue_comment(comment)
            
            logger.info("Comment added to PR", pr_number=pr_number)
            return True
        except GithubException as e:
            logger.error("Failed to add comment",
                        pr_number=pr_number,
                        error=str(e))
            return False
    
    def merge_pull_request(self,
                          repo: Repository,
                          pr_number: int,
                          merge_method: str = "merge") -> bool:
        """Merge a pull request
        
        Args:
            repo: Repository object
            pr_number: PR number
            merge_method: merge, squash, or rebase
        
        Returns:
            True if successful
        """
        try:
            pr = repo.get_pull(pr_number)
            
            # Check if mergeable
            if not pr.mergeable:
                logger.warning("PR not mergeable", pr_number=pr_number)
                return False
            
            # Merge
            pr.merge(merge_method=merge_method)
            
            logger.info("Pull request merged",
                       pr_number=pr_number,
                       method=merge_method)
            return True
        except GithubException as e:
            logger.error("Failed to merge PR",
                        pr_number=pr_number,
                        error=str(e))
            return False
    
    def list_user_repositories(self) -> List[Dict]:
        """List user's repositories"""
        if not self.authenticated_user:
            return []
        
        try:
            repos = []
            for repo in self.authenticated_user.get_repos():
                repos.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "private": repo.private
                })
            return repos
        except GithubException as e:
            logger.error("Failed to list repositories", error=str(e))
            return []
    
    def get_repository_url(self, repo: Repository, use_ssh: bool = False) -> str:
        """Get repository clone URL"""
        if use_ssh:
            return repo.ssh_url
        else:
            return repo.clone_url

