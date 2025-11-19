"""
Project Generator
Generates complete projects from templates
"""

import json
from pathlib import Path
from typing import Dict, Optional
import structlog

from .planner import Planner
from .worker import Worker
from models.runtime import LlamaCppRuntime

logger = structlog.get_logger()


class ProjectGenerator:
    """Generates full projects from templates and prompts"""
    
    def __init__(self, 
                 runtime: Optional[LlamaCppRuntime] = None,
                 templates_dir: Optional[Path] = None):
        """Initialize project generator"""
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates"
        
        self.templates_dir = Path(templates_dir)
        self.runtime = runtime
        self.planner = Planner(runtime)
        self.worker = Worker(runtime, None)
        
        logger.info("Project generator initialized",
                   templates_dir=str(self.templates_dir))
    
    def list_templates(self) -> list[Dict]:
        """List available project templates"""
        templates = []
        
        if not self.templates_dir.exists():
            return templates
        
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                
                templates.append({
                    "id": template_file.stem,
                    "name": template_data.get("name", template_file.stem),
                    "description": template_data.get("description", "")
                })
            except Exception as e:
                logger.error("Failed to load template",
                           file=str(template_file),
                           error=str(e))
        
        return templates
    
    def load_template(self, template_id: str) -> Optional[Dict]:
        """Load a template by ID"""
        template_path = self.templates_dir / f"{template_id}.json"
        
        if not template_path.exists():
            logger.error("Template not found", template_id=template_id)
            return None
        
        try:
            with open(template_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error("Failed to load template",
                        template_id=template_id,
                        error=str(e))
            return None
    
    async def generate_from_template(self,
                                    template_id: str,
                                    output_dir: str,
                                    customizations: Optional[Dict] = None) -> Dict:
        """Generate project from template
        
        Args:
            template_id: Template identifier
            output_dir: Output directory
            customizations: Optional customizations
        
        Returns:
            Generation result
        """
        logger.info("Generating project from template",
                   template_id=template_id,
                   output_dir=output_dir)
        
        # Load template
        template = self.load_template(template_id)
        if not template:
            return {"success": False, "error": "Template not found"}
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create files from template
        files_created = []
        template_files = template.get("files", {})
        
        for file_path, content in template_files.items():
            full_path = output_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Apply customizations
            if customizations:
                content = self._apply_customizations(content, customizations)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            files_created.append(file_path)
            logger.debug("Created file", path=file_path)
        
        logger.info("Project generated",
                   template=template_id,
                   files=len(files_created))
        
        return {
            "success": True,
            "template": template_id,
            "files_created": files_created,
            "output_dir": str(output_path)
        }
    
    def _apply_customizations(self, content: str, customizations: Dict) -> str:
        """Apply customizations to file content"""
        # Simple placeholder replacement
        for key, value in customizations.items():
            placeholder = f"{{{{ {key} }}}}"
            content = content.replace(placeholder, value)
        
        return content

