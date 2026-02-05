import json
import os
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TemplateLoader:
    """Loads and manages workflow templates"""
    
    def __init__(self, templates_dir: str = None):
        if templates_dir is None:
            # Default to 'templates' dir relative to this file
            templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.templates_dir = templates_dir
        
    def list_templates(self) -> List[Dict]:
        """List available templates"""
        templates = []
        if not os.path.exists(self.templates_dir):
            return []
            
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.templates_dir, filename), 'r') as f:
                        data = json.load(f)
                        templates.append({
                            'id': filename.replace('.json', ''),
                            'name': data.get('name', 'Unknown'),
                            'description': data.get('description', ''),
                            'parameters': data.get('meta', {}).get('parameters', [])
                        })
                except Exception as e:
                    logger.error(f"Error loading template {filename}: {e}")
                    
        return templates
        
    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get full template definition"""
        filepath = os.path.join(self.templates_dir, f"{template_id}.json")
        if not os.path.exists(filepath):
            return None
            
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception:
            return None
            
    def fill_template(self, template_id: str, parameters: Dict) -> Dict:
        """Fill template with parameters"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
            
        # Convert to string for replacement
        template_str = json.dumps(template)
        
        # Replace placeholders {{PARAM}}
        for key, value in parameters.items():
            template_str = template_str.replace(f"{{{{{key}}}}}", str(value))
            
        return json.loads(template_str)
