import json
import logging
from typing import Dict, Optional, Any
from mind_q_agent.llm.provider import LLMProvider
from mind_q_agent.automation.template_loader import TemplateLoader

logger = logging.getLogger(__name__)

class WorkflowConverter:
    """Converts natural language to n8n workflow using LLM"""
    
    def __init__(self, llm_provider: LLMProvider, template_loader: TemplateLoader):
        self.llm = llm_provider
        self.loader = template_loader
        
    async def convert(self, user_prompt: str) -> Dict[str, Any]:
        """
        Convert user prompt to workflow definition.
        Returns dict with 'workflow' (the n8n JSON) and 'metadata' (name, desc).
        """
        templates = self.loader.list_templates()
        template_summaries = [
            f"- ID: {t['id']}\n  Name: {t['name']}\n  Description: {t['description']}\n  Params: {[p['name'] for p in t['parameters']]}"
            for t in templates
        ]
        
        system_prompt = f"""You are an automation expert.
        Match the user request to one of the following templates:
        
        {chr(10).join(template_summaries)}
        
        Return a JSON object with:
        1. 'template_id': The ID of the best matching template.
        2. 'parameters': A dictionary of parameter values extracted from the request.
        3. 'reason': Brief explanation of why you chose this template.
        
        If no template matches, return 'template_id': null.
        only return valid JSON. provided strings should be properly escaped.
        """
        
        try:
            response_text = await self.llm.generate(user_prompt, system_prompt=system_prompt)
            # Basic cleanup in case LLM adds markdown blocks
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(response_text)
            
            if not result.get('template_id'):
                raise ValueError("No matching template found for your request.")
                
            template_id = result['template_id']
            parameters = result.get('parameters', {})
            
            # Fill template
            workflow = self.loader.fill_template(template_id, parameters)
            
            return {
                'workflow': workflow,
                'metadata': {
                    'template_id': template_id,
                    'parameters': parameters,
                    'reason': result.get('reason'),
                    'name': workflow.get('name', 'Automation'),
                    'description': workflow.get('meta', {}).get('description', '')
                }
            }
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response: {response_text}")
            raise ValueError("Failed to understand the automation request.")
        except Exception as e:
            logger.error(f"Error converting workflow: {e}")
            raise e
