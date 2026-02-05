import pytest
from unittest.mock import Mock, AsyncMock
from mind_q_agent.automation.converter import WorkflowConverter
from mind_q_agent.automation.template_loader import TemplateLoader
from mind_q_agent.llm.provider import LLMProvider

class MockLLM(LLMProvider):
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        return '{"template_id": "test_template", "parameters": {"param1": "test"}}'
        
    async def stream(self, prompt: str, system_prompt: str = None):
        yield ""
        
    def get_provider_name(self) -> str:
        return "mock"

@pytest.mark.asyncio
async def test_convert_success():
    llm = MockLLM()
    # Mock template loader
    loader = Mock(spec=TemplateLoader)
    loader.list_templates.return_value = [{'id': 'test_template', 'name': 'Test', 'description': 'desc', 'parameters': [{'name': 'param1'}]}]
    loader.fill_template.return_value = {'name': 'Filled Workflow', 'nodes': [], 'meta': {'description': 'filled desc'}}
    
    converter = WorkflowConverter(llm, loader)
    result = await converter.convert("I want a test workflow")
    
    assert result['metadata']['template_id'] == 'test_template'
    assert result['metadata']['parameters']['param1'] == 'test'
    assert result['workflow']['name'] == 'Filled Workflow'
    loader.fill_template.assert_called_with('test_template', {'param1': 'test'})
