"""
Test Sandbox Runner
Executes tests in isolated Docker containers
"""

from typing import Dict, Optional, List
from pathlib import Path
import asyncio

import structlog

logger = structlog.get_logger()


class TestRunner:
    """Runs tests in isolated sandbox"""
    
    def __init__(self, use_docker: bool = True):
        """Initialize test runner
        
        Args:
            use_docker: Use Docker for isolation (fallback to local if False)
        """
        self.use_docker = use_docker
        self.docker_available = False
        
        if use_docker:
            self._check_docker()
        
        logger.info("Test runner initialized",
                   use_docker=use_docker,
                   docker_available=self.docker_available)
    
    def _check_docker(self):
        """Check if Docker is available"""
        try:
            import docker
            client = docker.from_env()
            client.ping()
            self.docker_available = True
            logger.info("Docker is available")
        except Exception as e:
            logger.warning("Docker not available", error=str(e))
            self.docker_available = False
    
    async def run_tests(self,
                       workspace_path: str,
                       test_commands: List[str],
                       timeout: int = 300) -> Dict:
        """Run tests
        
        Args:
            workspace_path: Path to workspace
            test_commands: List of test commands to run
            timeout: Timeout in seconds
        
        Returns:
            Test results
        """
        logger.info("Running tests",
                   workspace=workspace_path,
                   commands=test_commands)
        
        if self.use_docker and self.docker_available:
            return await self._run_in_docker(workspace_path, test_commands, timeout)
        else:
            return await self._run_local(workspace_path, test_commands, timeout)
    
    async def _run_in_docker(self,
                            workspace_path: str,
                            test_commands: List[str],
                            timeout: int) -> Dict:
        """Run tests in Docker container"""
        try:
            import docker
            client = docker.from_env()
            
            # Detect project type and select image
            workspace = Path(workspace_path)
            
            if (workspace / "package.json").exists():
                image = "node:18-alpine"
                setup_commands = ["npm install"]
            elif (workspace / "requirements.txt").exists():
                image = "python:3.10-slim"
                setup_commands = ["pip install -r requirements.txt"]
            else:
                image = "python:3.10-slim"
                setup_commands = []
            
            logger.info("Running in Docker", image=image)
            
            # Create container
            container = client.containers.run(
                image,
                command="/bin/sh -c 'sleep infinity'",
                volumes={
                    str(workspace.absolute()): {
                        'bind': '/workspace',
                        'mode': 'ro'
                    }
                },
                working_dir='/workspace',
                detach=True,
                remove=True
            )
            
            results = {
                "setup": [],
                "tests": [],
                "success": True
            }
            
            try:
                # Run setup commands
                for cmd in setup_commands:
                    exit_code, output = container.exec_run(cmd)
                    results["setup"].append({
                        "command": cmd,
                        "exit_code": exit_code,
                        "output": output.decode()
                    })
                
                # Run test commands
                for cmd in test_commands:
                    exit_code, output = container.exec_run(cmd, workdir='/workspace')
                    
                    test_result = {
                        "command": cmd,
                        "exit_code": exit_code,
                        "output": output.decode(),
                        "passed": exit_code == 0
                    }
                    
                    results["tests"].append(test_result)
                    
                    if exit_code != 0:
                        results["success"] = False
                
            finally:
                container.stop()
            
            logger.info("Docker tests complete", success=results["success"])
            return results
            
        except Exception as e:
            logger.error("Docker test execution failed", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _run_local(self,
                        workspace_path: str,
                        test_commands: List[str],
                        timeout: int) -> Dict:
        """Run tests locally (fallback)"""
        logger.info("Running tests locally")
        
        results = {
            "tests": [],
            "success": True
        }
        
        for cmd in test_commands:
            try:
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    cwd=workspace_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        proc.communicate(),
                        timeout=timeout
                    )
                    
                    test_result = {
                        "command": cmd,
                        "exit_code": proc.returncode,
                        "output": stdout.decode() + "\n" + stderr.decode(),
                        "passed": proc.returncode == 0
                    }
                    
                    results["tests"].append(test_result)
                    
                    if proc.returncode != 0:
                        results["success"] = False
                    
                except asyncio.TimeoutError:
                    proc.kill()
                    results["tests"].append({
                        "command": cmd,
                        "exit_code": -1,
                        "output": "Test timed out",
                        "passed": False
                    })
                    results["success"] = False
                
            except Exception as e:
                logger.error("Test execution failed", command=cmd, error=str(e))
                results["tests"].append({
                    "command": cmd,
                    "exit_code": -1,
                    "output": str(e),
                    "passed": False
                })
                results["success"] = False
        
        logger.info("Local tests complete", success=results["success"])
        return results

