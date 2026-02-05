from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
import uuid
import os

from mind_q_agent.automation.storage import AutomationStorage
from mind_q_agent.automation.n8n_client import N8nClient
from mind_q_agent.automation.template_loader import TemplateLoader
from mind_q_agent.automation.converter import WorkflowConverter
from mind_q_agent.api.settings import settings
# Assuming we can import a default LLM provider or similar
# For now, we will mock/placeholder this dependency or use a factory
# from mind_q_agent.llm.factory import get_llm

router = APIRouter(prefix="/automation", tags=["automation"])

# Dependency Providers
def get_storage():
    return AutomationStorage()

def get_n8n_client():
    # In real app, these come from settings
    n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
    n8n_key = os.getenv("N8N_API_KEY", "")
    return N8nClient(n8n_url, n8n_key)

async def get_converter():
    # TODO: Replace with real LLM provider injection
    from mind_q_agent.llm.provider import LLMProvider
    # This is a temporary hack until LLM factory is standardized in the project
    class MockLLM(LLMProvider):
        async def generate(self, prompt, system_prompt=None):
            return '{"template_id": "daily_digest", "parameters": {"email": "test@example.com"}}'
        async def stream(self, prompt, system_prompt=None): yield ""
        def get_provider_name(self): return "mock"
        
    llm = MockLLM() 
    loader = TemplateLoader()
    return WorkflowConverter(llm, loader)

# Models
class CreateAutomationRequest(BaseModel):
    prompt: str
    user_id: str

class AutomationResponse(BaseModel):
    id: str
    workflow_id: str
    name: str
    description: str
    active: bool

# Routes
@router.post("/create")
async def create_automation(
    request: CreateAutomationRequest,
    storage: AutomationStorage = Depends(get_storage),
    n8n: N8nClient = Depends(get_n8n_client),
    converter: WorkflowConverter = Depends(get_converter)
):
    """Create automation from natural language"""
    try:
        # 1. Convert Prompt to Workflow
        result = await converter.convert(request.prompt)
        workflow_json = result['workflow']
        metadata = result['metadata']
        
        # 2. Create in n8n
        n8n_wf = n8n.create_workflow(
            name=f"{metadata['name']} ({uuid.uuid4().hex[:6]})",
            nodes=workflow_json['nodes'],
            connections=workflow_json['connections']
        )
        
        # 3. Store metadata
        automation_id = str(uuid.uuid4())
        workflow_id = n8n_wf['id']
        
        storage.create_automation(
            automation_id=automation_id,
            user_id=request.user_id,
            workflow_id=workflow_id,
            workflow_name=n8n_wf['name'],
            description=metadata['description'],
            metadata=metadata
        )
        
        # 4. Activate
        n8n.activate_workflow(workflow_id, True)
        
        return {
            "id": automation_id,
            "workflow_id": workflow_id,
            "name": n8n_wf['name'],
            "status": "created_and_activated",
            "explanation": f"I've created a workflow based on template '{metadata['template_id']}'."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list/{user_id}", response_model=List[AutomationResponse])
async def list_automations(
    user_id: str,
    storage: AutomationStorage = Depends(get_storage)
):
    """List user automations"""
    automations = storage.list_user_automations(user_id)
    return [
        AutomationResponse(
            id=a['id'],
            workflow_id=a['workflow_id'],
            name=a['workflow_name'],
            description=a['description'] or "",
            active=bool(a['active'])
        ) for a in automations
    ]

@router.post("/{automation_id}/activate")
async def activate_automation(
    automation_id: str,
    active: bool = True,
    storage: AutomationStorage = Depends(get_storage),
    n8n: N8nClient = Depends(get_n8n_client)
):
    """Activate/Deactivate automation"""
    auto = storage.get_automation(automation_id)
    if not auto:
        raise HTTPException(status_code=404, detail="Automation not found")
        
    try:
        n8n.activate_workflow(auto['workflow_id'], active)
        storage.update_status(automation_id, active)
        return {"status": "updated", "active": active}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
