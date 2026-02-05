import pytest
from unittest.mock import Mock, patch
from mind_q_agent.automation.n8n_client import N8nClient
from mind_q_agent.automation.storage import AutomationStorage
import tempfile
import os
import sqlite3

class TestN8nClient:
    @pytest.fixture
    def client(self):
        return N8nClient("http://localhost:5678", "test-key")

    @patch('requests.get')
    def test_test_connection_success(self, mock_get, client):
        mock_get.return_value.status_code = 200
        assert client.test_connection() is True

    @patch('requests.get')
    def test_test_connection_failure(self, mock_get, client):
        mock_get.side_effect = Exception("Connection refused")
        assert client.test_connection() is False

    @patch('requests.get')
    def test_get_workflows(self, mock_get, client):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'data': [{'id': '1', 'name': 'Test'}]}
        
        workflows = client.get_workflows()
        assert len(workflows) == 1
        assert workflows[0]['name'] == 'Test'

class TestAutomationStorage:
    @pytest.fixture
    def storage(self):
        # Create a temp db
        fd, path = tempfile.mkstemp()
        os.close(fd)
        storage = AutomationStorage(path)
        yield storage
        os.unlink(path)

    def test_create_and_get_automation(self, storage):
        storage.create_automation(
            "auto_1", "user_1", "wf_1", "Test Automation", 
            "Description", {"key": "value"}
        )
        
        auto = storage.get_automation("auto_1")
        assert auto is not None
        assert auto['workflow_name'] == "Test Automation"
        assert auto['metadata']['key'] == "value"

    def test_list_user_automations(self, storage):
        storage.create_automation("a1", "user_1", "w1", "n1", "d1")
        storage.create_automation("a2", "user_1", "w2", "n2", "d2")
        storage.create_automation("a3", "user_2", "w3", "n3", "d3")
        
        user1_autos = storage.list_user_automations("user_1")
        assert len(user1_autos) == 2
