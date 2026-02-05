import requests
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class N8nClient:
    """Client for interacting with n8n API"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'X-N8N-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
    def test_connection(self) -> bool:
        """Test connection to n8n"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/users",
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to connect to n8n: {e}")
            return False
            
    def get_workflows(self, active: bool = None) -> List[Dict]:
        """Get all workflows"""
        params = {}
        if active is not None:
            params['active'] = str(active).lower()
            
        response = requests.get(
            f"{self.base_url}/api/v1/workflows",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json().get('data', [])
        
    def get_workflow(self, workflow_id: str) -> Dict:
        """Get a specific workflow"""
        response = requests.get(
            f"{self.base_url}/api/v1/workflows/{workflow_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
        
    def create_workflow(self, name: str, nodes: List[Dict], connections: Dict) -> Dict:
        """Create a new workflow"""
        payload = {
            'name': name,
            'nodes': nodes,
            'connections': connections,
            'settings': {
                'saveManualExecutions': True,
                'saveDataErrorExecution': 'all',
                'saveDataSuccessExecution': 'all',
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/workflows",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
        
    def activate_workflow(self, workflow_id: str, active: bool = True) -> Dict:
        """Activate or deactivate a workflow"""
        response = requests.post(
            f"{self.base_url}/api/v1/workflows/{workflow_id}/{'activate' if active else 'deactivate'}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
        
    def get_executions(self, workflow_id: str = None, limit: int = 10) -> List[Dict]:
        """Get past executions"""
        params = {'limit': limit}
        if workflow_id:
            params['workflowId'] = workflow_id
            
        response = requests.get(
            f"{self.base_url}/api/v1/executions",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json().get('data', [])
        
    def get_execution(self, execution_id: str) -> Dict:
        """Get detailed execution data"""
        response = requests.get(
            f"{self.base_url}/api/v1/executions/{execution_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
