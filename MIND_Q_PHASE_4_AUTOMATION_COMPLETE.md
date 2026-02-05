# 🗺️ Mind-Q Phase 4: Complete Automation & Smart Features
## Tasks 71-90 - Full Implementation Guide

**Version:** 2.0 Complete  
**Date:** February 5, 2026  
**Status:** Ready for AI Agent Implementation

---

## 📋 TABLE OF CONTENTS

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Phase 4D: n8n Integration (Tasks 71-80)](#phase-4d-n8n-integration)
- [Phase 4E: Smart Features (Tasks 81-90)](#phase-4e-smart-features)
- [Testing Strategy](#testing-strategy)
- [Deployment Guide](#deployment-guide)

---

## 🎯 OVERVIEW

**What We're Building:**
- Natural language → n8n workflow automation
- Smart AI-powered features
- Proactive assistance system
- Full frontend integration

**Architecture:**
```
User (Natural Language) 
    ↓
Mind-Q API + LLM (Understanding)
    ↓
n8n API (Workflow Creation)
    ↓
n8n Engine (Execution)
    ↓
Mind-Q Custom Nodes (Actions)
```

---

## 📦 PREREQUISITES

Before starting, ensure you have:

```bash
# 1. n8n installed
npm install -g n8n

# 2. Mind-Q API running (from Phase 4A)
cd mind-q-agent
source venv/bin/activate
python scripts/run_api.py

# 3. Required dependencies
pip install openai anthropic  # For LLM
npm install @n8n/api-client    # For n8n integration
```

---

# 🔷 PHASE 4D: n8n INTEGRATION (Tasks 71-80)

---

## ✅ Task 71: n8n Setup & Mind-Q Custom Nodes

**Description:** Install n8n and create custom Mind-Q nodes  
**Time:** 6 hours  
**🧪 Command:** `npm test n8n-nodes/`

### 🤖 AI AGENT PROMPT:

```markdown
Task 71: n8n Setup & Mind-Q Custom Nodes

**PART 1: Install n8n**

1. Install n8n globally:
```bash
npm install -g n8n

# Verify installation
n8n --version
```

2. Create n8n workspace:
```bash
mkdir -p ~/.n8n
n8n start &  # Start in background
# Access at: http://localhost:5678
```

3. Generate API key in n8n:
- Go to http://localhost:5678
- Settings → API
- Generate new API key
- Save it securely

**PART 2: Create Mind-Q Custom Nodes Package**

Create directory structure:
```bash
cd mind-q-agent
mkdir -p n8n-nodes-mindq
cd n8n-nodes-mindq
npm init -y
```

Install dependencies:
```bash
npm install n8n-workflow n8n-core
npm install --save-dev @types/node typescript
```

Update package.json:
```json
{
  "name": "n8n-nodes-mindq",
  "version": "1.0.0",
  "description": "Mind-Q custom nodes for n8n",
  "main": "index.js",
  "scripts": {
    "build": "tsc",
    "test": "jest"
  },
  "n8n": {
    "nodes": [
      "dist/nodes/MindQSearch/MindQSearch.node.js",
      "dist/nodes/MindQAddDocument/MindQAddDocument.node.js",
      "dist/nodes/MindQGetConcepts/MindQGetConcepts.node.js",
      "dist/nodes/MindQAskQuestion/MindQAskQuestion.node.js"
    ],
    "credentials": [
      "dist/credentials/MindQApi.credentials.js"
    ]
  },
  "keywords": ["n8n-community-node-package"],
  "license": "MIT"
}
```

Create tsconfig.json:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

**PART 3: Create Credentials**

Create file: src/credentials/MindQApi.credentials.ts
```typescript
import {
    IAuthenticateGeneric,
    ICredentialTestRequest,
    ICredentialType,
    INodeProperties,
} from 'n8n-workflow';

export class MindQApi implements ICredentialType {
    name = 'mindQApi';
    displayName = 'Mind-Q API';
    documentationUrl = 'https://github.com/yourusername/mind-q-agent';
    properties: INodeProperties[] = [
        {
            displayName: 'API URL',
            name: 'apiUrl',
            type: 'string',
            default: 'http://localhost:8000',
            placeholder: 'http://localhost:8000',
        },
        {
            displayName: 'API Key',
            name: 'apiKey',
            type: 'string',
            typeOptions: {
                password: true,
            },
            default: '',
        },
    ];

    authenticate: IAuthenticateGeneric = {
        type: 'generic',
        properties: {
            headers: {
                'X-API-Key': '={{$credentials.apiKey}}',
            },
        },
    };

    test: ICredentialTestRequest = {
        request: {
            baseURL: '={{$credentials.apiUrl}}',
            url: '/health',
        },
    };
}
```

**PART 4: Create Mind-Q Search Node**

Create file: src/nodes/MindQSearch/MindQSearch.node.ts
```typescript
import {
    IExecuteFunctions,
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
    NodeOperationError,
} from 'n8n-workflow';

import axios from 'axios';

export class MindQSearch implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Mind-Q Search',
        name: 'mindQSearch',
        icon: 'file:mindq.svg',
        group: ['transform'],
        version: 1,
        subtitle: '={{$parameter["operation"]}}',
        description: 'Search Mind-Q Knowledge Graph',
        defaults: {
            name: 'Mind-Q Search',
        },
        inputs: ['main'],
        outputs: ['main'],
        credentials: [
            {
                name: 'mindQApi',
                required: true,
            },
        ],
        properties: [
            {
                displayName: 'Operation',
                name: 'operation',
                type: 'options',
                noDataExpression: true,
                options: [
                    {
                        name: 'Search',
                        value: 'search',
                        description: 'Search for content',
                        action: 'Search for content',
                    },
                    {
                        name: 'Get Recent',
                        value: 'recent',
                        description: 'Get recent documents',
                        action: 'Get recent documents',
                    },
                ],
                default: 'search',
            },
            {
                displayName: 'Query',
                name: 'query',
                type: 'string',
                displayOptions: {
                    show: {
                        operation: ['search'],
                    },
                },
                default: '',
                placeholder: 'Enter search query',
                description: 'What to search for in Mind-Q',
            },
            {
                displayName: 'Search Type',
                name: 'searchType',
                type: 'options',
                displayOptions: {
                    show: {
                        operation: ['search'],
                    },
                },
                options: [
                    {
                        name: 'Semantic',
                        value: 'semantic',
                    },
                    {
                        name: 'Keyword',
                        value: 'keyword',
                    },
                    {
                        name: 'Concept',
                        value: 'concept',
                    },
                ],
                default: 'semantic',
            },
            {
                displayName: 'Max Results',
                name: 'maxResults',
                type: 'number',
                default: 10,
                description: 'Maximum number of results to return',
            },
            {
                displayName: 'Time Range (hours)',
                name: 'timeRange',
                type: 'number',
                displayOptions: {
                    show: {
                        operation: ['recent'],
                    },
                },
                default: 24,
                description: 'Get documents from last N hours',
            },
        ],
    };

    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
        const items = this.getInputData();
        const returnData: INodeExecutionData[] = [];

        const credentials = await this.getCredentials('mindQApi');
        const apiUrl = credentials.apiUrl as string;
        const apiKey = credentials.apiKey as string;

        for (let i = 0; i < items.length; i++) {
            try {
                const operation = this.getNodeParameter('operation', i) as string;

                let results;

                if (operation === 'search') {
                    const query = this.getNodeParameter('query', i) as string;
                    const searchType = this.getNodeParameter('searchType', i) as string;
                    const maxResults = this.getNodeParameter('maxResults', i) as number;

                    const response = await axios.post(
                        `${apiUrl}/search`,
                        {
                            query,
                            search_type: searchType,
                            max_results: maxResults,
                        },
                        {
                            headers: {
                                'X-API-Key': apiKey,
                                'Content-Type': 'application/json',
                            },
                        }
                    );

                    results = response.data;
                } else if (operation === 'recent') {
                    const timeRange = this.getNodeParameter('timeRange', i) as number;
                    const maxResults = this.getNodeParameter('maxResults', i) as number;

                    const response = await axios.get(
                        `${apiUrl}/documents/recent`,
                        {
                            params: {
                                hours: timeRange,
                                limit: maxResults,
                            },
                            headers: {
                                'X-API-Key': apiKey,
                            },
                        }
                    );

                    results = response.data;
                }

                returnData.push({
                    json: results,
                    pairedItem: { item: i },
                });
            } catch (error) {
                if (this.continueOnFail()) {
                    returnData.push({
                        json: {
                            error: error.message,
                        },
                        pairedItem: { item: i },
                    });
                    continue;
                }
                throw new NodeOperationError(this.getNode(), error);
            }
        }

        return [returnData];
    }
}
```

**PART 5: Create Add Document Node**

Create file: src/nodes/MindQAddDocument/MindQAddDocument.node.ts
```typescript
import {
    IExecuteFunctions,
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
} from 'n8n-workflow';

import axios from 'axios';

export class MindQAddDocument implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Mind-Q Add Document',
        name: 'mindQAddDocument',
        icon: 'file:mindq.svg',
        group: ['transform'],
        version: 1,
        description: 'Add document to Mind-Q',
        defaults: {
            name: 'Mind-Q Add Document',
        },
        inputs: ['main'],
        outputs: ['main'],
        credentials: [
            {
                name: 'mindQApi',
                required: true,
            },
        ],
        properties: [
            {
                displayName: 'Title',
                name: 'title',
                type: 'string',
                default: '',
                placeholder: 'Document title',
                description: 'Title of the document',
            },
            {
                displayName: 'Content',
                name: 'content',
                type: 'string',
                typeOptions: {
                    rows: 4,
                },
                default: '',
                placeholder: 'Document content',
                description: 'Content of the document',
            },
            {
                displayName: 'Source',
                name: 'source',
                type: 'string',
                default: 'n8n_automation',
                description: 'Source identifier',
            },
            {
                displayName: 'Tags',
                name: 'tags',
                type: 'string',
                default: '',
                placeholder: 'tag1, tag2, tag3',
                description: 'Comma-separated tags',
            },
        ],
    };

    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
        const items = this.getInputData();
        const returnData: INodeExecutionData[] = [];

        const credentials = await this.getCredentials('mindQApi');
        const apiUrl = credentials.apiUrl as string;
        const apiKey = credentials.apiKey as string;

        for (let i = 0; i < items.length; i++) {
            const title = this.getNodeParameter('title', i) as string;
            const content = this.getNodeParameter('content', i) as string;
            const source = this.getNodeParameter('source', i) as string;
            const tagsString = this.getNodeParameter('tags', i) as string;

            const tags = tagsString ? tagsString.split(',').map(t => t.trim()) : [];

            const response = await axios.post(
                `${apiUrl}/documents`,
                {
                    title,
                    content,
                    source,
                    tags,
                },
                {
                    headers: {
                        'X-API-Key': apiKey,
                        'Content-Type': 'application/json',
                    },
                }
            );

            returnData.push({
                json: response.data,
                pairedItem: { item: i },
            });
        }

        return [returnData];
    }
}
```

**PART 6: Create Get Concepts Node**

Create file: src/nodes/MindQGetConcepts/MindQGetConcepts.node.ts
```typescript
import {
    IExecuteFunctions,
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
} from 'n8n-workflow';

import axios from 'axios';

export class MindQGetConcepts implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Mind-Q Get Concepts',
        name: 'mindQGetConcepts',
        icon: 'file:mindq.svg',
        group: ['transform'],
        version: 1,
        description: 'Extract concepts from Mind-Q',
        defaults: {
            name: 'Mind-Q Get Concepts',
        },
        inputs: ['main'],
        outputs: ['main'],
        credentials: [
            {
                name: 'mindQApi',
                required: true,
            },
        ],
        properties: [
            {
                displayName: 'Operation',
                name: 'operation',
                type: 'options',
                noDataExpression: true,
                options: [
                    {
                        name: 'Top Concepts',
                        value: 'top',
                        description: 'Get top weighted concepts',
                    },
                    {
                        name: 'Related Concepts',
                        value: 'related',
                        description: 'Get concepts related to a given concept',
                    },
                ],
                default: 'top',
            },
            {
                displayName: 'Concept Name',
                name: 'conceptName',
                type: 'string',
                displayOptions: {
                    show: {
                        operation: ['related'],
                    },
                },
                default: '',
                placeholder: 'Enter concept name',
            },
            {
                displayName: 'Limit',
                name: 'limit',
                type: 'number',
                default: 10,
                description: 'Number of concepts to return',
            },
        ],
    };

    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
        const items = this.getInputData();
        const returnData: INodeExecutionData[] = [];

        const credentials = await this.getCredentials('mindQApi');
        const apiUrl = credentials.apiUrl as string;
        const apiKey = credentials.apiKey as string;

        for (let i = 0; i < items.length; i++) {
            const operation = this.getNodeParameter('operation', i) as string;
            const limit = this.getNodeParameter('limit', i) as number;

            let endpoint = '';
            let params: any = { limit };

            if (operation === 'top') {
                endpoint = '/graph/concepts/top';
            } else if (operation === 'related') {
                const conceptName = this.getNodeParameter('conceptName', i) as string;
                endpoint = `/graph/concepts/${conceptName}/related`;
            }

            const response = await axios.get(`${apiUrl}${endpoint}`, {
                params,
                headers: {
                    'X-API-Key': apiKey,
                },
            });

            returnData.push({
                json: response.data,
                pairedItem: { item: i },
            });
        }

        return [returnData];
    }
}
```

**PART 7: Create Ask Question Node**

Create file: src/nodes/MindQAskQuestion/MindQAskQuestion.node.ts
```typescript
import {
    IExecuteFunctions,
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
} from 'n8n-workflow';

import axios from 'axios';

export class MindQAskQuestion implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Mind-Q Ask Question',
        name: 'mindQAskQuestion',
        icon: 'file:mindq.svg',
        group: ['transform'],
        version: 1,
        description: 'Ask questions using Mind-Q knowledge',
        defaults: {
            name: 'Mind-Q Ask Question',
        },
        inputs: ['main'],
        outputs: ['main'],
        credentials: [
            {
                name: 'mindQApi',
                required: true,
            },
        ],
        properties: [
            {
                displayName: 'Question',
                name: 'question',
                type: 'string',
                typeOptions: {
                    rows: 2,
                },
                default: '',
                placeholder: 'Ask a question',
                description: 'Question to ask',
            },
            {
                displayName: 'Use Context',
                name: 'useContext',
                type: 'boolean',
                default: true,
                description: 'Whether to use Mind-Q knowledge for context',
            },
        ],
    };

    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
        const items = this.getInputData();
        const returnData: INodeExecutionData[] = [];

        const credentials = await this.getCredentials('mindQApi');
        const apiUrl = credentials.apiUrl as string;
        const apiKey = credentials.apiKey as string;

        for (let i = 0; i < items.length; i++) {
            const question = this.getNodeParameter('question', i) as string;
            const useContext = this.getNodeParameter('useContext', i) as boolean;

            const response = await axios.post(
                `${apiUrl}/chat/ask`,
                {
                    question,
                    use_context: useContext,
                },
                {
                    headers: {
                        'X-API-Key': apiKey,
                        'Content-Type': 'application/json',
                    },
                }
            );

            returnData.push({
                json: response.data,
                pairedItem: { item: i },
            });
        }

        return [returnData];
    }
}
```

**PART 8: Create Icon**

Create file: src/nodes/MindQSearch/mindq.svg (use same for all)
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="45" fill="#667eea"/>
  <text x="50" y="65" font-family="Arial" font-size="40" font-weight="bold" text-anchor="middle" fill="white">M</text>
</svg>
```

Copy to all node directories:
```bash
cp src/nodes/MindQSearch/mindq.svg src/nodes/MindQAddDocument/
cp src/nodes/MindQSearch/mindq.svg src/nodes/MindQGetConcepts/
cp src/nodes/MindQSearch/mindq.svg src/nodes/MindQAskQuestion/
```

**PART 9: Build and Link**

```bash
# Build
npm run build

# Link to n8n
npm link
cd ~/.n8n/custom
npm link n8n-nodes-mindq

# Restart n8n
pkill -f n8n
n8n start &
```

**PART 10: Verify**

1. Open http://localhost:5678
2. Create new workflow
3. Search for "Mind-Q" nodes
4. You should see:
   - Mind-Q Search
   - Mind-Q Add Document
   - Mind-Q Get Concepts
   - Mind-Q Ask Question

**VERIFICATION:**
- [ ] n8n running on port 5678
- [ ] 4 Mind-Q nodes visible in n8n
- [ ] Credentials page shows "Mind-Q API"
- [ ] Test connection successful

**Tests to create:**
Create file: tests/n8n/test_nodes.ts
```typescript
describe('Mind-Q Nodes', () => {
    test('Search node executes', async () => {
        // Test search node
    });
    
    test('Add document node executes', async () => {
        // Test add document
    });
});
```

Ready? Implement this.
```

---

## ✅ Task 72: n8n API Integration Layer

**Description:** Python client to communicate with n8n API  
**Time:** 4 hours  
**🧪 Command:** `pytest tests/automation/test_n8n_client.py -v`

### 🤖 AI AGENT PROMPT:

```markdown
Task 72: n8n API Integration Layer

Create file: automation/__init__.py
Create file: automation/n8n_client.py
Create file: automation/config.py

**STEP 1: Configuration**

Create file: automation/config.py
```python
from pydantic_settings import BaseSettings

class AutomationSettings(BaseSettings):
    n8n_url: str = "http://localhost:5678"
    n8n_api_key: str = ""
    
    class Config:
        env_prefix = "N8N_"

settings = AutomationSettings()
```

**STEP 2: n8n Client**

Create file: automation/n8n_client.py
```python
import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class N8nClient:
    """
    Client for n8n API communication
    """
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-N8N-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
    
    def create_workflow(self, workflow_data: Dict) -> str:
        """
        Create a new workflow in n8n
        
        Args:
            workflow_data: Workflow definition (name, nodes, connections)
            
        Returns:
            workflow_id: ID of created workflow
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/workflows",
                headers=self.headers,
                json=workflow_data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            workflow_id = result['data']['id']
            
            logger.info(f"Created workflow: {workflow_id}")
            return workflow_id
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create workflow: {e}")
            raise
    
    def get_workflow(self, workflow_id: str) -> Dict:
        """
        Get workflow details
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()['data']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get workflow {workflow_id}: {e}")
            raise
    
    def update_workflow(self, workflow_id: str, workflow_data: Dict) -> bool:
        """
        Update existing workflow
        """
        try:
            response = requests.patch(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                json=workflow_data,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(f"Updated workflow: {workflow_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update workflow {workflow_id}: {e}")
            raise
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow
        """
        try:
            response = requests.delete(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(f"Deleted workflow: {workflow_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete workflow {workflow_id}: {e}")
            raise
    
    def activate_workflow(self, workflow_id: str) -> bool:
        """
        Activate a workflow
        """
        try:
            response = requests.patch(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                json={'active': True},
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(f"Activated workflow: {workflow_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to activate workflow {workflow_id}: {e}")
            raise
    
    def deactivate_workflow(self, workflow_id: str) -> bool:
        """
        Deactivate a workflow
        """
        try:
            response = requests.patch(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                json={'active': False},
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(f"Deactivated workflow: {workflow_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to deactivate workflow {workflow_id}: {e}")
            raise
    
    def list_workflows(self, active: Optional[bool] = None) -> List[Dict]:
        """
        List all workflows
        
        Args:
            active: Filter by active status (None = all)
        """
        try:
            params = {}
            if active is not None:
                params['active'] = active
            
            response = requests.get(
                f"{self.base_url}/api/v1/workflows",
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()['data']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list workflows: {e}")
            raise
    
    def execute_workflow(
        self, 
        workflow_id: str, 
        data: Optional[Dict] = None
    ) -> str:
        """
        Manually execute a workflow
        
        Returns:
            execution_id: ID of the execution
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/execute",
                headers=self.headers,
                json=data or {},
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()['data']
            execution_id = result['executionId']
            
            logger.info(f"Executed workflow {workflow_id}: {execution_id}")
            return execution_id
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            raise
    
    def get_executions(
        self, 
        workflow_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get execution history
        """
        try:
            params = {'limit': limit}
            if workflow_id:
                params['workflowId'] = workflow_id
            
            response = requests.get(
                f"{self.base_url}/api/v1/executions",
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()['data']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get executions: {e}")
            raise
    
    def get_execution(self, execution_id: str) -> Dict:
        """
        Get details of a specific execution
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/executions/{execution_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()['data']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get execution {execution_id}: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test n8n API connection
        """
        try:
            response = requests.get(
                f"{self.base_url}/healthz",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
            
        except requests.exceptions.RequestException:
            return False
```

**STEP 3: Tests**

Create file: tests/automation/__init__.py
Create file: tests/automation/test_n8n_client.py
```python
import pytest
from automation.n8n_client import N8nClient
from automation.config import settings

@pytest.fixture
def n8n_client():
    """Create n8n client for testing"""
    return N8nClient(settings.n8n_url, settings.n8n_api_key)

def test_connection(n8n_client):
    """Test n8n connection"""
    assert n8n_client.test_connection() is True

def test_create_workflow(n8n_client):
    """Test workflow creation"""
    workflow_data = {
        "name": "Test Workflow",
        "nodes": [
            {
                "name": "Start",
                "type": "n8n-nodes-base.start",
                "position": [250, 300],
                "parameters": {}
            }
        ],
        "connections": {},
        "active": False
    }
    
    workflow_id = n8n_client.create_workflow(workflow_data)
    assert workflow_id is not None
    
    # Cleanup
    n8n_client.delete_workflow(workflow_id)

def test_list_workflows(n8n_client):
    """Test listing workflows"""
    workflows = n8n_client.list_workflows()
    assert isinstance(workflows, list)

def test_activate_deactivate(n8n_client):
    """Test workflow activation/deactivation"""
    # Create test workflow
    workflow_data = {
        "name": "Test Activation",
        "nodes": [
            {
                "name": "Start",
                "type": "n8n-nodes-base.start",
                "position": [250, 300],
                "parameters": {}
            }
        ],
        "connections": {},
        "active": False
    }
    
    workflow_id = n8n_client.create_workflow(workflow_data)
    
    # Test activation
    assert n8n_client.activate_workflow(workflow_id) is True
    
    # Verify active
    workflow = n8n_client.get_workflow(workflow_id)
    assert workflow['active'] is True
    
    # Test deactivation
    assert n8n_client.deactivate_workflow(workflow_id) is True
    
    # Cleanup
    n8n_client.delete_workflow(workflow_id)
```

**STEP 4: Update Requirements**

Add to requirements-api.txt:
```
requests>=2.31.0
```

Install:
```bash
pip install requests
```

**VERIFICATION:**
Run tests:
```bash
# Set n8n credentials
export N8N_URL="http://localhost:5678"
export N8N_API_KEY="your_api_key_here"

# Run tests
pytest tests/automation/test_n8n_client.py -v
```

All tests should pass:
- test_connection ✓
- test_create_workflow ✓
- test_list_workflows ✓
- test_activate_deactivate ✓

Ready? Implement this.
```

---

## ✅ Task 73: Workflow Template Library

**Description:** Pre-built workflow templates  
**Time:** 3 hours  
**🧪 Command:** `pytest tests/automation/test_templates.py -v`

### 🤖 AI AGENT PROMPT:

```markdown
Task 73: Workflow Template Library

Create file: automation/workflow_templates.py

**STEP 1: Base Template Class**

```python
from typing import Dict, List, Optional
from datetime import datetime

class WorkflowTemplates:
    """
    Library of pre-built n8n workflow templates
    """
    
    @staticmethod
    def _create_schedule_trigger(
        hours_interval: int = 24,
        position: List[int] = [250, 300]
    ) -> Dict:
        """Helper: Create schedule trigger node"""
        return {
            "name": "Schedule Trigger",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1,
            "position": position,
            "parameters": {
                "rule": {
                    "interval": [{
                        "field": "hours",
                        "hoursInterval": hours_interval
                    }]
                }
            }
        }
    
    @staticmethod
    def _create_mindq_search(
        query: str = "",
        search_type: str = "semantic",
        max_results: int = 10,
        position: List[int] = [450, 300]
    ) -> Dict:
        """Helper: Create Mind-Q search node"""
        return {
            "name": "Mind-Q Search",
            "type": "mindQSearch",
            "typeVersion": 1,
            "position": position,
            "parameters": {
                "operation": "search",
                "query": query,
                "searchType": search_type,
                "maxResults": max_results
            },
            "credentials": {
                "mindQApi": {
                    "id": "1",
                    "name": "Mind-Q API"
                }
            }
        }
    
    @staticmethod
    def _create_openai_node(
        prompt: str,
        position: List[int] = [650, 300]
    ) -> Dict:
        """Helper: Create OpenAI node"""
        return {
            "name": "OpenAI",
            "type": "n8n-nodes-base.openAi",
            "typeVersion": 1,
            "position": position,
            "parameters": {
                "operation": "message",
                "text": prompt,
                "options": {}
            },
            "credentials": {
                "openAiApi": {
                    "id": "2",
                    "name": "OpenAI API"
                }
            }
        }
    
    @staticmethod
    def _create_email_node(
        subject: str,
        text: str,
        to_email: str = "{{$json.user_email}}",
        position: List[int] = [850, 300]
    ) -> Dict:
        """Helper: Create email send node"""
        return {
            "name": "Send Email",
            "type": "n8n-nodes-base.emailSend",
            "typeVersion": 1,
            "position": position,
            "parameters": {
                "fromEmail": "mindq@example.com",
                "toEmail": to_email,
                "subject": subject,
                "text": text,
                "options": {}
            }
        }
    
    @staticmethod
    def daily_digest(
        hours_interval: int = 24,
        max_documents: int = 20
    ) -> Dict:
        """
        Template: Daily digest of new documents
        
        Workflow:
        1. Trigger daily
        2. Get new documents from Mind-Q
        3. Summarize with LLM
        4. Send email
        """
        nodes = [
            WorkflowTemplates._create_schedule_trigger(
                hours_interval=hours_interval,
                position=[250, 300]
            ),
            {
                "name": "Get New Documents",
                "type": "mindQSearch",
                "typeVersion": 1,
                "position": [450, 300],
                "parameters": {
                    "operation": "recent",
                    "timeRange": hours_interval,
                    "maxResults": max_documents
                },
                "credentials": {
                    "mindQApi": {
                        "id": "1",
                        "name": "Mind-Q API"
                    }
                }
            },
            WorkflowTemplates._create_openai_node(
                prompt="Summarize these documents in a concise daily digest:\n\n{{$json}}",
                position=[650, 300]
            ),
            WorkflowTemplates._create_email_node(
                subject="Mind-Q Daily Digest",
                text="{{$json.choices[0].message.content}}",
                position=[850, 300]
            )
        ]
        
        connections = {
            "Schedule Trigger": {
                "main": [[{"node": "Get New Documents", "type": "main", "index": 0}]]
            },
            "Get New Documents": {
                "main": [[{"node": "OpenAI", "type": "main", "index": 0}]]
            },
            "OpenAI": {
                "main": [[{"node": "Send Email", "type": "main", "index": 0}]]
            }
        }
        
        return {
            "name": "Daily Mind-Q Digest",
            "nodes": nodes,
            "connections": connections,
            "active": False,
            "settings": {
                "saveExecutionProgress": True,
                "saveManualExecutions": True
            }
        }
    
    @staticmethod
    def topic_monitor(
        topic: str,
        check_interval_hours: int = 6,
        notify_slack: bool = False,
        slack_channel: str = "#general"
    ) -> Dict:
        """
        Template: Monitor a specific topic
        
        Workflow:
        1. Trigger periodically
        2. Search web for topic
        3. Add new content to Mind-Q
        4. Notify user
        """
        nodes = [
            WorkflowTemplates._create_schedule_trigger(
                hours_interval=check_interval_hours,
                position=[250, 300]
            ),
            {
                "name": "Web Search",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 1,
                "position": [450, 300],
                "parameters": {
                    "url": f"https://api.search.brave.com/res/v1/web/search?q={topic}",
                    "authentication": "genericCredentialType",
                    "genericAuthType": "httpHeaderAuth",
                    "method": "GET",
                    "options": {}
                }
            },
            {
                "name": "Add to Mind-Q",
                "type": "mindQAddDocument",
                "typeVersion": 1,
                "position": [650, 300],
                "parameters": {
                    "title": f"{{{{$json.title}}}} - {topic}",
                    "content": "={{$json.description}}",
                    "source": "web_monitor",
                    "tags": topic
                },
                "credentials": {
                    "mindQApi": {
                        "id": "1",
                        "name": "Mind-Q API"
                    }
                }
            }
        ]
        
        # Add notification node
        if notify_slack:
            nodes.append({
                "name": "Notify Slack",
                "type": "n8n-nodes-base.slack",
                "typeVersion": 1,
                "position": [850, 300],
                "parameters": {
                    "channel": slack_channel,
                    "text": f"New content found for topic: {topic}\\n{{{{$json.title}}}}",
                    "otherOptions": {}
                },
                "credentials": {
                    "slackApi": {
                        "id": "3",
                        "name": "Slack API"
                    }
                }
            })
        else:
            nodes.append(
                WorkflowTemplates._create_email_node(
                    subject=f"New Content: {topic}",
                    text="New content found:\\n\\n{{$json.title}}\\n{{$json.content}}",
                    position=[850, 300]
                )
            )
        
        connections = {
            "Schedule Trigger": {
                "main": [[{"node": "Web Search", "type": "main", "index": 0}]]
            },
            "Web Search": {
                "main": [[{"node": "Add to Mind-Q", "type": "main", "index": 0}]]
            },
            "Add to Mind-Q": {
                "main": [[{
                    "node": "Notify Slack" if notify_slack else "Send Email",
                    "type": "main",
                    "index": 0
                }]]
            }
        }
        
        return {
            "name": f"Monitor Topic: {topic}",
            "nodes": nodes,
            "connections": connections,
            "active": False
        }
    
    @staticmethod
    def auto_tag_documents() -> Dict:
        """
        Template: Automatically tag new documents
        
        Workflow:
        1. Triggered by webhook (new document)
        2. Extract concepts from Mind-Q
        3. Generate tags with LLM
        4. Apply tags back to document
        """
        nodes = [
            {
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [250, 300],
                "parameters": {
                    "path": "mindq-new-document",
                    "responseMode": "onReceived",
                    "options": {}
                },
                "webhookId": "auto-tag-webhook"
            },
            {
                "name": "Get Concepts",
                "type": "mindQGetConcepts",
                "typeVersion": 1,
                "position": [450, 300],
                "parameters": {
                    "operation": "related",
                    "conceptName": "={{$json.document_title}}",
                    "limit": 10
                },
                "credentials": {
                    "mindQApi": {
                        "id": "1",
                        "name": "Mind-Q API"
                    }
                }
            },
            WorkflowTemplates._create_openai_node(
                prompt="Generate 5 relevant tags for a document about these concepts:\\n{{$json}}\\n\\nReturn only comma-separated tags.",
                position=[650, 300]
            ),
            {
                "name": "Apply Tags",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 1,
                "position": [850, 300],
                "parameters": {
                    "url": "http://localhost:8000/documents/={{$json.document_id}}/tags",
                    "method": "PUT",
                    "bodyParameters": {
                        "parameters": [{
                            "name": "tags",
                            "value": "={{$json.choices[0].message.content.split(',')}}"
                        }]
                    },
                    "options": {}
                }
            }
        ]
        
        connections = {
            "Webhook": {
                "main": [[{"node": "Get Concepts", "type": "main", "index": 0}]]
            },
            "Get Concepts": {
                "main": [[{"node": "OpenAI", "type": "main", "index": 0}]]
            },
            "OpenAI": {
                "main": [[{"node": "Apply Tags", "type": "main", "index": 0}]]
            }
        }
        
        return {
            "name": "Auto-Tag New Documents",
            "nodes": nodes,
            "connections": connections,
            "active": False
        }
    
    @staticmethod
    def research_assistant(
        research_topic: str,
        sources: List[str] = ["arxiv", "scholar", "news"],
        frequency_days: int = 7
    ) -> Dict:
        """
        Template: Proactive research assistant
        
        Workflow:
        1. Weekly trigger
        2. Search multiple sources
        3. Compile and analyze
        4. Generate research report
        5. Send to user
        """
        hours_interval = frequency_days * 24
        
        nodes = [
            WorkflowTemplates._create_schedule_trigger(
                hours_interval=hours_interval,
                position=[250, 300]
            )
        ]
        
        # Add search nodes for each source
        y_pos = 200
        for idx, source in enumerate(sources):
            nodes.append({
                "name": f"Search {source.title()}",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 1,
                "position": [450, y_pos + (idx * 100)],
                "parameters": {
                    "url": f"https://api.{source}.com/search?q={research_topic}",
                    "method": "GET"
                }
            })
        
        # Merge results
        nodes.append({
            "name": "Merge Results",
            "type": "n8n-nodes-base.merge",
            "typeVersion": 1,
            "position": [650, 300],
            "parameters": {
                "mode": "mergeByIndex"
            }
        })
        
        # Analyze with LLM
        nodes.append(
            WorkflowTemplates._create_openai_node(
                prompt=f"Analyze these research results about {research_topic} and create a comprehensive summary with key findings:\\n\\n{{{{$json}}}}",
                position=[850, 300]
            )
        )
        
        # Send report
        nodes.append(
            WorkflowTemplates._create_email_node(
                subject=f"Research Report: {research_topic}",
                text="={{$json.choices[0].message.content}}",
                position=[1050, 300]
            )
        )
        
        # Build connections
        connections = {
            "Schedule Trigger": {
                "main": [[{"node": f"Search {src.title()}", "type": "main", "index": 0}] for src in sources]
            },
            "Merge Results": {
                "main": [[{"node": "OpenAI", "type": "main", "index": 0}]]
            },
            "OpenAI": {
                "main": [[{"node": "Send Email", "type": "main", "index": 0}]]
            }
        }
        
        # Connect all searches to merge
        for source in sources:
            connections[f"Search {source.title()}"] = {
                "main": [[{"node": "Merge Results", "type": "main", "index": 0}]]
            }
        
        return {
            "name": f"Research Assistant: {research_topic}",
            "nodes": nodes,
            "connections": connections,
            "active": False
        }
    
    @staticmethod
    def learning_path_tracker(
        learning_goal: str,
        check_frequency_days: int = 3
    ) -> Dict:
        """
        Template: Track learning progress
        
        Workflow:
        1. Periodic trigger
        2. Get user's recent documents/concepts
        3. Analyze progress with LLM
        4. Suggest next steps
        5. Update learning path
        """
        hours_interval = check_frequency_days * 24
        
        nodes = [
            WorkflowTemplates._create_schedule_trigger(
                hours_interval=hours_interval,
                position=[250, 300]
            ),
            {
                "name": "Get Learning Progress",
                "type": "mindQSearch",
                "typeVersion": 1,
                "position": [450, 300],
                "parameters": {
                    "operation": "search",
                    "query": learning_goal,
                    "searchType": "semantic",
                    "maxResults": 50
                },
                "credentials": {
                    "mindQApi": {"id": "1", "name": "Mind-Q API"}
                }
            },
            WorkflowTemplates._create_openai_node(
                prompt=f"Analyze this learning progress toward goal: {learning_goal}\\n\\nDocuments: {{{{$json}}}}\\n\\nProvide:\\n1. Progress assessment\\n2. Knowledge gaps\\n3. Next steps\\n4. Resources needed",
                position=[650, 300]
            ),
            WorkflowTemplates._create_email_node(
                subject=f"Learning Progress: {learning_goal}",
                text="={{$json.choices[0].message.content}}",
                position=[850, 300]
            )
        ]
        
        connections = {
            "Schedule Trigger": {
                "main": [[{"node": "Get Learning Progress", "type": "main", "index": 0}]]
            },
            "Get Learning Progress": {
                "main": [[{"node": "OpenAI", "type": "main", "index": 0}]]
            },
            "OpenAI": {
                "main": [[{"node": "Send Email", "type": "main", "index": 0}]]
            }
        }
        
        return {
            "name": f"Learning Path: {learning_goal}",
            "nodes": nodes,
            "connections": connections,
            "active": False
        }
```

**STEP 2: Tests**

Create file: tests/automation/test_templates.py
```python
import pytest
from automation.workflow_templates import WorkflowTemplates

def test_daily_digest_template():
    """Test daily digest template creation"""
    workflow = WorkflowTemplates.daily_digest()
    
    assert workflow['name'] == "Daily Mind-Q Digest"
    assert len(workflow['nodes']) == 4
    assert 'connections' in workflow
    assert workflow['active'] is False

def test_topic_monitor_template():
    """Test topic monitor template"""
    workflow = WorkflowTemplates.topic_monitor(
        topic="AI Research",
        check_interval_hours=6
    )
    
    assert "AI Research" in workflow['name']
    assert len(workflow['nodes']) >= 4

def test_auto_tag_template():
    """Test auto-tag template"""
    workflow = WorkflowTemplates.auto_tag_documents()
    
    assert workflow['name'] == "Auto-Tag New Documents"
    assert any(node['type'] == 'n8n-nodes-base.webhook' for node in workflow['nodes'])

def test_research_assistant_template():
    """Test research assistant template"""
    workflow = WorkflowTemplates.research_assistant(
        research_topic="Quantum Computing",
        sources=["arxiv", "scholar"]
    )
    
    assert "Quantum Computing" in workflow['name']
    # Should have schedule + 2 searches + merge + llm + email
    assert len(workflow['nodes']) >= 5

def test_learning_path_template():
    """Test learning path tracker"""
    workflow = WorkflowTemplates.learning_path_tracker(
        learning_goal="Master Python",
        check_frequency_days=7
    )
    
    assert "Master Python" in workflow['name']
    assert len(workflow['nodes']) == 4
```

**VERIFICATION:**
```bash
pytest tests/automation/test_templates.py -v
```

All tests should pass ✓

Ready? Implement this.
```

---

## ✅ Task 74: Natural Language to Workflow Converter

**Description:** Convert natural language requests to n8n workflows using LLM  
**Time:** 5 hours  
**🧪 Command:** `pytest tests/automation/test_generator.py -v`

### 🤖 AI AGENT PROMPT:

```markdown
Task 74: Natural Language to Workflow Converter

Create file: automation/workflow_generator.py

**STEP 1: LLM Integration**

First, install LLM client:
```bash
pip install openai anthropic
```

Create file: automation/llm_client.py
```python
import os
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Unified LLM client (supports OpenAI, Anthropic, local models)
    """
    
    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        
        # Default models
        default_models = {
            "openai": "gpt-4-turbo-preview",
            "anthropic": "claude-3-sonnet-20240229"
        }
        
        self.model = model or default_models.get(self.provider)
        
        # Initialize client
        if self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Get completion from LLM
        """
        try:
            if self.provider == "openai":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return response.choices[0].message.content
                
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt or "",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"LLM completion error: {e}")
            raise
    
    def extract_json(self, text: str) -> dict:
        """
        Extract JSON from LLM response
        """
        # Try to find JSON in response
        import re
        
        # Look for JSON blocks
        json_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            json_str = match.group(1)
        else:
            # Try to parse entire response
            json_str = text
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try to extract first {...} or [...]
            brace_pattern = r'[{\[].*[}\]]'
            match = re.search(brace_pattern, text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise
```

**STEP 2: Workflow Generator**

Create file: automation/workflow_generator.py
```python
from typing import Dict, List, Optional
import json
import logging
from automation.workflow_templates import WorkflowTemplates
from automation.llm_client import LLMClient

logger = logging.getLogger(__name__)

class WorkflowGenerator:
    """
    Generate n8n workflows from natural language descriptions
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None
    ):
        self.llm = llm_client or LLMClient()
        self.templates = WorkflowTemplates()
    
    def generate_from_description(
        self,
        user_request: str,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Main entry point: Generate workflow from natural language
        
        Args:
            user_request: User's natural language request
            user_context: Additional context (email, preferences, etc.)
            
        Returns:
            n8n workflow definition
        """
        logger.info(f"Generating workflow from: {user_request}")
        
        # 1. Extract intent and parameters
        intent_analysis = self._analyze_intent(user_request)
        
        intent = intent_analysis['intent']
        params = intent_analysis['parameters']
        
        logger.info(f"Detected intent: {intent}")
        logger.info(f"Parameters: {params}")
        
        # 2. Select appropriate template
        template_method = self._select_template(intent)
        
        # 3. Generate workflow from template
        workflow = self._customize_template(
            template_method,
            params,
            user_context
        )
        
        # 4. Enhance with LLM if needed
        if params.get('complex', False):
            workflow = self._enhance_workflow(workflow, user_request)
        
        return workflow
    
    def _analyze_intent(self, text: str) -> Dict:
        """
        Use LLM to understand user intent and extract parameters
        """
        system_prompt = """You are an expert at understanding automation requests.
Analyze the user's request and extract:
1. Primary intent (what they want to automate)
2. Parameters (frequency, topics, actions, etc.)
3. Complexity level

Return ONLY valid JSON."""

        prompt = f"""Analyze this automation request:

User Request: "{text}"

Classify the intent and extract parameters as JSON:

{{
  "intent": "one of: daily_digest, topic_monitor, auto_tag, research_assistant, learning_tracker, custom",
  "parameters": {{
    "topic": "main topic or keyword (if applicable)",
    "frequency": "how often: hourly, every_6_hours, daily, weekly",
    "frequency_hours": numeric hours between runs,
    "action": "what to do: email, slack, save, notify",
    "search_terms": ["list of search terms"],
    "filters": ["any specific criteria"],
    "sources": ["where to search: web, arxiv, scholar, news"],
    "notification_channel": "email, slack, etc.",
    "user_email": "if mentioned",
    "complex": true/false (is this a complex multi-step workflow?)
  }},
  "confidence": 0.0-1.0
}}

Return ONLY the JSON, no explanation."""

        response = self.llm.complete(prompt, system_prompt=system_prompt)
        
        try:
            result = self.llm.extract_json(response)
            return result
        except Exception as e:
            logger.error(f"Failed to parse intent: {e}")
            # Fallback
            return {
                "intent": "custom",
                "parameters": {"description": text},
                "confidence": 0.0
            }
    
    def _select_template(self, intent: str) -> callable:
        """
        Select appropriate template based on intent
        """
        template_map = {
            'daily_digest': self.templates.daily_digest,
            'topic_monitor': self.templates.topic_monitor,
            'auto_tag': self.templates.auto_tag_documents,
            'research_assistant': self.templates.research_assistant,
            'learning_tracker': self.templates.learning_path_tracker,
        }
        
        return template_map.get(intent, self.templates.daily_digest)
    
    def _customize_template(
        self,
        template_method: callable,
        params: Dict,
        user_context: Optional[Dict]
    ) -> Dict:
        """
        Customize template with extracted parameters
        """
        # Extract template-specific parameters
        template_params = {}
        
        # Frequency
        if 'frequency_hours' in params:
            template_params['hours_interval'] = params['frequency_hours']
        elif 'frequency' in params:
            freq_map = {
                'hourly': 1,
                'every_6_hours': 6,
                'daily': 24,
                'weekly': 168
            }
            template_params['hours_interval'] = freq_map.get(
                params['frequency'], 24
            )
        
        # Topic-based templates
        if 'topic' in params:
            template_params['topic'] = params['topic']
        
        if 'learning_goal' in params:
            template_params['learning_goal'] = params['learning_goal']
        
        if 'research_topic' in params:
            template_params['research_topic'] = params['research_topic']
        
        # Sources
        if 'sources' in params:
            template_params['sources'] = params['sources']
        
        # Notification preferences
        if params.get('action') == 'slack':
            template_params['notify_slack'] = True
            if 'notification_channel' in params:
                template_params['slack_channel'] = params['notification_channel']
        
        # Generate workflow
        workflow = template_method(**template_params)
        
        # Add user context to email nodes if available
        if user_context and 'email' in user_context:
            self._update_email_addresses(workflow, user_context['email'])
        
        return workflow
    
    def _update_email_addresses(self, workflow: Dict, email: str):
        """
        Update email addresses in workflow nodes
        """
        for node in workflow['nodes']:
            if node['type'] == 'n8n-nodes-base.emailSend':
                if 'toEmail' in node['parameters']:
                    node['parameters']['toEmail'] = email
    
    def _enhance_workflow(self, workflow: Dict, original_request: str) -> Dict:
        """
        Use LLM to add custom logic or nodes for complex workflows
        """
        system_prompt = """You are an expert at designing n8n workflows.
Enhance the given workflow based on the user's specific needs."""

        prompt = f"""Original Request: "{original_request}"

Current Workflow:
{json.dumps(workflow, indent=2)}

Suggest enhancements:
1. Additional nodes needed
2. Better error handling
3. Optimization opportunities

Return the enhanced workflow as JSON."""

        # This is advanced - for now, just return original
        # In production, you'd parse LLM response and merge changes
        return workflow
    
    def explain_workflow(self, workflow: Dict) -> str:
        """
        Generate human-readable explanation of workflow
        """
        prompt = f"""Explain this n8n workflow in simple terms:

Workflow:
{json.dumps(workflow, indent=2)}

Provide:
1. What it does (2-3 sentences)
2. When it runs
3. What actions it takes
4. What the user receives

Keep it simple and clear."""

        response = self.llm.complete(prompt)
        return response
    
    def validate_workflow(self, workflow: Dict) -> bool:
        """
        Validate workflow structure
        """
        required_keys = ['name', 'nodes', 'connections']
        
        if not all(key in workflow for key in required_keys):
            return False
        
        if not workflow['nodes']:
            return False
        
        # Check all nodes have required fields
        for node in workflow['nodes']:
            if not all(key in node for key in ['name', 'type', 'position']):
                return False
        
        return True
```

**STEP 3: Conversation Examples**

Create file: automation/conversation_examples.py
```python
"""
Example conversations showing workflow generation
"""

EXAMPLES = [
    {
        "user": "أريد كل صباح الساعة 8 ملخص عن المستندات الجديدة",
        "intent": "daily_digest",
        "parameters": {
            "frequency": "daily",
            "frequency_hours": 24,
            "action": "email"
        },
        "workflow_name": "Daily Mind-Q Digest"
    },
    {
        "user": "راقب كل المستجدات عن Quantum Computing وأخبرني فوراً على Slack",
        "intent": "topic_monitor",
        "parameters": {
            "topic": "Quantum Computing",
            "frequency_hours": 6,
            "action": "slack",
            "notification_channel": "#research"
        },
        "workflow_name": "Monitor Topic: Quantum Computing"
    },
    {
        "user": "كل ملف PDF أرفعه، استخرج منه المفاهيم وصنفه تلقائياً",
        "intent": "auto_tag",
        "parameters": {
            "trigger": "webhook",
            "action": "tag"
        },
        "workflow_name": "Auto-Tag New Documents"
    },
    {
        "user": "ساعدني في البحث عن آخر الأوراق العلمية في AI كل أسبوع",
        "intent": "research_assistant",
        "parameters": {
            "research_topic": "AI",
            "sources": ["arxiv", "scholar"],
            "frequency": "weekly",
            "frequency_hours": 168
        },
        "workflow_name": "Research Assistant: AI"
    },
    {
        "user": "تتبع تقدمي في تعلم Machine Learning واقترح لي خطوات تالية كل 3 أيام",
        "intent": "learning_tracker",
        "parameters": {
            "learning_goal": "Machine Learning",
            "frequency_hours": 72,
            "action": "email"
        },
        "workflow_name": "Learning Path: Machine Learning"
    }
]
```

**STEP 4: Tests**

Create file: tests/automation/test_generator.py
```python
import pytest
from automation.workflow_generator import WorkflowGenerator
from automation.llm_client import LLMClient

@pytest.fixture
def generator():
    """Create workflow generator for testing"""
    # Use mock LLM for tests to avoid API calls
    return WorkflowGenerator()

def test_intent_analysis(generator):
    """Test intent extraction"""
    request = "I want daily summaries of new documents"
    
    analysis = generator._analyze_intent(request)
    
    assert 'intent' in analysis
    assert 'parameters' in analysis
    assert 'confidence' in analysis

def test_daily_digest_generation(generator):
    """Test generating daily digest workflow"""
    request = "Send me a daily email with new documents"
    
    workflow = generator.generate_from_description(request)
    
    assert workflow['name'] is not None
    assert len(workflow['nodes']) >= 3
    assert generator.validate_workflow(workflow)

def test_topic_monitor_generation(generator):
    """Test generating topic monitor workflow"""
    request = "Monitor AI research and notify me on Slack"
    
    workflow = generator.generate_from_description(request)
    
    assert "monitor" in workflow['name'].lower() or "ai" in workflow['name'].lower()
    assert generator.validate_workflow(workflow)

def test_workflow_explanation(generator):
    """Test workflow explanation generation"""
    workflow = {
        "name": "Test Workflow",
        "nodes": [
            {"name": "Schedule", "type": "scheduleTrigger", "position": [0, 0]},
            {"name": "Action", "type": "httpRequest", "position": [100, 0]}
        ],
        "connections": {}
    }
    
    explanation = generator.explain_workflow(workflow)
    
    assert len(explanation) > 50
    assert isinstance(explanation, str)

def test_arabic_request(generator):
    """Test handling Arabic language requests"""
    request = "أريد ملخص يومي للمستندات الجديدة"
    
    workflow = generator.generate_from_description(request)
    
    assert generator.validate_workflow(workflow)

@pytest.mark.parametrize("request,expected_nodes", [
    ("daily digest", 4),  # schedule + search + llm + email
    ("monitor topic", 4),  # schedule + search + add + notify
])
def test_workflow_structure(generator, request, expected_nodes):
    """Test generated workflows have correct structure"""
    workflow = generator.generate_from_description(request)
    
    assert len(workflow['nodes']) >= expected_nodes
    assert 'connections' in workflow
```

**VERIFICATION:**
```bash
# Install dependencies
pip install openai anthropic

# Set API key
export OPENAI_API_KEY="your_key_here"
# or
export ANTHROPIC_API_KEY="your_key_here"

# Run tests
pytest tests/automation/test_generator.py -v
```

Ready? Implement this.
```

---

## ✅ Task 75: Chat Interface for Automation

**Description:** API endpoints for creating automations via chat  
**Time:** 4 hours  
**🧪 Command:** `pytest tests/api/test_automation.py -v`

### 🤖 AI AGENT PROMPT:

```markdown
Task 75: Chat Interface for Automation

**PART 1: Database Models**

Create file: api/models/automation.py
```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class AutomationRequest(BaseModel):
    """Request to create automation from natural language"""
    description: str = Field(..., min_length=10)
    user_id: str
    user_email: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Send me daily email with new AI research papers",
                "user_id": "user123",
                "user_email": "user@example.com"
            }
        }

class AutomationResponse(BaseModel):
    """Response after creating automation"""
    automation_id: str
    workflow_id: str
    workflow_name: str
    status: str
    explanation: str
    preview: Dict
    
class AutomationListItem(BaseModel):
    """Single automation in list"""
    automation_id: str
    workflow_id: str
    name: str
    description: str
    active: bool
    created_at: datetime
    last_execution: Optional[datetime] = None
    execution_count: int = 0

class AutomationUpdate(BaseModel):
    """Update automation settings"""
    active: Optional[bool] = None
    description: Optional[str] = None
```

**PART 2: Database Storage**

Create file: automation/storage.py
```python
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import uuid

class AutomationStorage:
    """
    Simple JSON-based storage for user automations
    (Replace with proper database in production)
    """
    
    def __init__(self, storage_path: str = "./data/automations"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save_automation(
        self,
        user_id: str,
        workflow_id: str,
        workflow_name: str,
        description: str,
        workflow_data: Dict
    ) -> str:
        """
        Save user automation
        """
        automation_id = str(uuid.uuid4())
        
        automation = {
            "automation_id": automation_id,
            "user_id": user_id,
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "description": description,
            "workflow_data": workflow_data,
            "active": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_execution": None,
            "execution_count": 0
        }
        
        # Save to file
        file_path = self.storage_path / f"{automation_id}.json"
        with open(file_path, 'w') as f:
            json.dump(automation, f, indent=2)
        
        return automation_id
    
    def get_automation(self, automation_id: str) -> Optional[Dict]:
        """Get automation by ID"""
        file_path = self.storage_path / f"{automation_id}.json"
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def list_user_automations(self, user_id: str) -> List[Dict]:
        """List all automations for a user"""
        automations = []
        
        for file_path in self.storage_path.glob("*.json"):
            with open(file_path, 'r') as f:
                automation = json.load(f)
                if automation['user_id'] == user_id:
                    automations.append(automation)
        
        # Sort by created_at descending
        automations.sort(
            key=lambda x: x['created_at'],
            reverse=True
        )
        
        return automations
    
    def update_automation(
        self,
        automation_id: str,
        updates: Dict
    ) -> bool:
        """Update automation"""
        automation = self.get_automation(automation_id)
        
        if not automation:
            return False
        
        automation.update(updates)
        automation['updated_at'] = datetime.now().isoformat()
        
        file_path = self.storage_path / f"{automation_id}.json"
        with open(file_path, 'w') as f:
            json.dump(automation, f, indent=2)
        
        return True
    
    def delete_automation(self, automation_id: str) -> bool:
        """Delete automation"""
        file_path = self.storage_path / f"{automation_id}.json"
        
        if not file_path.exists():
            return False
        
        file_path.unlink()
        return True
    
    def record_execution(self, automation_id: str):
        """Record workflow execution"""
        automation = self.get_automation(automation_id)
        
        if automation:
            automation['last_execution'] = datetime.now().isoformat()
            automation['execution_count'] += 1
            
            file_path = self.storage_path / f"{automation_id}.json"
            with open(file_path, 'w') as f:
                json.dump(automation, f, indent=2)
```

**PART 3: API Routes**

Create file: api/routes/automation.py
```python
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from api.models.automation import (
    AutomationRequest,
    AutomationResponse,
    AutomationListItem,
    AutomationUpdate
)
from automation.workflow_generator import WorkflowGenerator
from automation.n8n_client import N8nClient
from automation.storage import AutomationStorage
from automation.config import settings
from automation.llm_client import LLMClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/automation", tags=["automation"])

# Initialize services
llm_client = LLMClient()
workflow_generator = WorkflowGenerator(llm_client)
n8n_client = N8nClient(settings.n8n_url, settings.n8n_api_key)
automation_storage = AutomationStorage()

@router.post("/create", response_model=AutomationResponse)
async def create_automation_from_chat(request: AutomationRequest):
    """
    Create automation from natural language description
    
    Example:
    ```json
    {
      "description": "Send me daily email with new AI papers",
      "user_id": "user123",
      "user_email": "user@example.com"
    }
    ```
    """
    try:
        logger.info(f"Creating automation for user {request.user_id}: {request.description}")
        
        # 1. Generate workflow from description
        user_context = {}
        if request.user_email:
            user_context['email'] = request.user_email
        
        workflow = workflow_generator.generate_from_description(
            request.description,
            user_context
        )
        
        # 2. Validate workflow
        if not workflow_generator.validate_workflow(workflow):
            raise HTTPException(
                status_code=400,
                detail="Generated workflow is invalid"
            )
        
        # 3. Create workflow in n8n
        workflow_id = n8n_client.create_workflow(workflow)
        
        # 4. Save to database
        automation_id = automation_storage.save_automation(
            user_id=request.user_id,
            workflow_id=workflow_id,
            workflow_name=workflow['name'],
            description=request.description,
            workflow_data=workflow
        )
        
        # 5. Generate explanation
        explanation = workflow_generator.explain_workflow(workflow)
        
        logger.info(f"Created automation {automation_id} with workflow {workflow_id}")
        
        return AutomationResponse(
            automation_id=automation_id,
            workflow_id=workflow_id,
            workflow_name=workflow['name'],
            status='created',
            explanation=explanation,
            preview=workflow
        )
        
    except Exception as e:
        logger.error(f"Failed to create automation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[AutomationListItem])
async def list_user_automations(user_id: str):
    """
    List all automations for a user
    """
    try:
        automations = automation_storage.list_user_automations(user_id)
        
        return [
            AutomationListItem(
                automation_id=auto['automation_id'],
                workflow_id=auto['workflow_id'],
                name=auto['workflow_name'],
                description=auto['description'],
                active=auto['active'],
                created_at=auto['created_at'],
                last_execution=auto.get('last_execution'),
                execution_count=auto.get('execution_count', 0)
            )
            for auto in automations
        ]
        
    except Exception as e:
        logger.error(f"Failed to list automations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{automation_id}")
async def get_automation(automation_id: str):
    """
    Get automation details
    """
    automation = automation_storage.get_automation(automation_id)
    
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    return automation

@router.patch("/{automation_id}")
async def update_automation(
    automation_id: str,
    updates: AutomationUpdate
):
    """
    Update automation settings
    """
    automation = automation_storage.get_automation(automation_id)
    
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    # Update in storage
    update_data = updates.dict(exclude_unset=True)
    automation_storage.update_automation(automation_id, update_data)
    
    # If activating/deactivating, update in n8n
    if 'active' in update_data:
        workflow_id = automation['workflow_id']
        
        if update_data['active']:
            n8n_client.activate_workflow(workflow_id)
        else:
            n8n_client.deactivate_workflow(workflow_id)
    
    return {"status": "updated"}

@router.post("/{automation_id}/activate")
async def activate_automation(automation_id: str):
    """
    Activate an automation
    """
    automation = automation_storage.get_automation(automation_id)
    
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    workflow_id = automation['workflow_id']
    
    try:
        n8n_client.activate_workflow(workflow_id)
        automation_storage.update_automation(automation_id, {'active': True})
        
        return {"status": "activated"}
        
    except Exception as e:
        logger.error(f"Failed to activate automation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{automation_id}/deactivate")
async def deactivate_automation(automation_id: str):
    """
    Deactivate an automation
    """
    automation = automation_storage.get_automation(automation_id)
    
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    workflow_id = automation['workflow_id']
    
    try:
        n8n_client.deactivate_workflow(workflow_id)
        automation_storage.update_automation(automation_id, {'active': False})
        
        return {"status": "deactivated"}
        
    except Exception as e:
        logger.error(f"Failed to deactivate automation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{automation_id}")
async def delete_automation(automation_id: str):
    """
    Delete an automation
    """
    automation = automation_storage.get_automation(automation_id)
    
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    workflow_id = automation['workflow_id']
    
    try:
        # Delete from n8n
        n8n_client.delete_workflow(workflow_id)
        
        # Delete from storage
        automation_storage.delete_automation(automation_id)
        
        return {"status": "deleted"}
        
    except Exception as e:
        logger.error(f"Failed to delete automation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{automation_id}/test")
async def test_automation(automation_id: str):
    """
    Manually trigger automation for testing
    """
    automation = automation_storage.get_automation(automation_id)
    
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    workflow_id = automation['workflow_id']
    
    try:
        execution_id = n8n_client.execute_workflow(workflow_id)
        
        automation_storage.record_execution(automation_id)
        
        return {
            "status": "executed",
            "execution_id": execution_id
        }
        
    except Exception as e:
        logger.error(f"Failed to test automation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{automation_id}/executions")
async def get_automation_executions(automation_id: str):
    """
    Get execution history for automation
    """
    automation = automation_storage.get_automation(automation_id)
    
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    workflow_id = automation['workflow_id']
    
    try:
        executions = n8n_client.get_executions(workflow_id)
        return executions
        
    except Exception as e:
        logger.error(f"Failed to get executions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**PART 4: Register Routes**

Update api/main.py:
```python
from api.routes import automation

app.include_router(automation.router)
```

**PART 5: Tests**

Create file: tests/api/test_automation.py
```python
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_create_automation():
    """Test creating automation via API"""
    response = client.post(
        "/automation/create",
        json={
            "description": "Send me daily digest of new documents",
            "user_id": "test_user",
            "user_email": "test@example.com"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert 'automation_id' in data
    assert 'workflow_id' in data
    assert 'explanation' in data
    assert data['status'] == 'created'

def test_list_automations():
    """Test listing user automations"""
    response = client.get("/automation/list?user_id=test_user")
    
    assert response.status_code == 200
    automations = response.json()
    
    assert isinstance(automations, list)

def test_get_automation():
    """Test getting automation details"""
    # First create one
    create_response = client.post(
        "/automation/create",
        json={
            "description": "Test automation",
            "user_id": "test_user"
        }
    )
    
    automation_id = create_response.json()['automation_id']
    
    # Then get it
    response = client.get(f"/automation/{automation_id}")
    
    assert response.status_code == 200
    automation = response.json()
    
    assert automation['automation_id'] == automation_id

def test_activate_deactivate():
    """Test activation/deactivation"""
    # Create automation
    create_response = client.post(
        "/automation/create",
        json={
            "description": "Test automation",
            "user_id": "test_user"
        }
    )
    
    automation_id = create_response.json()['automation_id']
    
    # Activate
    response = client.post(f"/automation/{automation_id}/activate")
    assert response.status_code == 200
    
    # Deactivate
    response = client.post(f"/automation/{automation_id}/deactivate")
    assert response.status_code == 200

def test_delete_automation():
    """Test deleting automation"""
    # Create automation
    create_response = client.post(
        "/automation/create",
        json={
            "description": "Test automation",
            "user_id": "test_user"
        }
    )
    
    automation_id = create_response.json()['automation_id']
    
    # Delete
    response = client.delete(f"/automation/{automation_id}")
    assert response.status_code == 200
    
    # Verify deleted
    response = client.get(f"/automation/{automation_id}")
    assert response.status_code == 404
```

**VERIFICATION:**
```bash
pytest tests/api/test_automation.py -v
```

Ready? Implement this.
```

---

Due to length limitations, I'll now create the complete file with all remaining tasks (76-90) included...

Let me create the complete file:
