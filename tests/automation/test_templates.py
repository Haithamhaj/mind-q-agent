import pytest
import json
import os
from mind_q_agent.automation.template_loader import TemplateLoader
import tempfile

class TestTemplateLoader:
    @pytest.fixture
    def templates_dir(self):
        # Create temp dir
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test template
            template_path = os.path.join(temp_dir, 'test_template.json')
            with open(template_path, 'w') as f:
                json.dump({
                    "name": "Test Template",
                    "description": "A test template",
                    "meta": {
                        "parameters": [{"name": "param1"}]
                    },
                    "nodes": [{"name": "{{param1}}"}]
                }, f)
            yield temp_dir

    def test_list_templates(self, templates_dir):
        loader = TemplateLoader(templates_dir)
        templates = loader.list_templates()
        assert len(templates) == 1
        assert templates[0]['id'] == 'test_template'
        assert templates[0]['name'] == 'Test Template'

    def test_get_template(self, templates_dir):
        loader = TemplateLoader(templates_dir)
        template = loader.get_template('test_template')
        assert template is not None
        assert template['name'] == 'Test Template'

    def test_fill_template(self, templates_dir):
        loader = TemplateLoader(templates_dir)
        filled = loader.fill_template('test_template', {'param1': 'MyNode'})
        assert filled['nodes'][0]['name'] == 'MyNode'
