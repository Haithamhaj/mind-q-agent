from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from mind_q_agent.automation.storage import AutomationStorage
from mind_q_agent.automation.n8n_client import N8nClient
from mind_q_agent.api.routers.automation import get_storage, get_n8n_client

router = APIRouter(prefix="/automation/monitoring", tags=["monitoring"])
logger = logging.getLogger(__name__)

@router.get("/dashboard/{user_id}")
async def get_monitoring_dashboard(
    user_id: str,
    storage: AutomationStorage = Depends(get_storage),
    n8n: N8nClient = Depends(get_n8n_client)
):
    """Get comprehensive monitoring dashboard data"""
    # Get user automations
    automations = storage.list_user_automations(user_id)
    
    # Calculate stats
    total_automations = len(automations)
    active_automations = sum(1 for a in automations if a.get('active', False))
    total_executions = sum(a.get('execution_count', 0) for a in automations)
    
    # Get recent executions from n8n for top automations
    recent_executions = []
    # Only check top 5 to avoid API slamming
    for automation in automations[:5]:
        workflow_id = automation['workflow_id']
        try:
            execs = n8n.get_executions(workflow_id, limit=3)
            for exc in execs:
                recent_executions.append({
                    'automation_name': automation['workflow_name'],
                    'execution_id': exc['id'],
                    'status': exc.get('finished', False),
                    'started_at': exc.get('startedAt'),
                    'finished_at': exc.get('stoppedAt')
                })
        except Exception:
            # Ignore n8n errors for individual workflows
            pass
            
    # Sort by recency
    recent_executions.sort(key=lambda x: x.get('started_at', ''), reverse=True)
    
    # Calculate simple success rate based on recent executions
    if recent_executions:
        successful = sum(1 for e in recent_executions if e['status'])
        success_rate = (successful / len(recent_executions)) * 100
    else:
        success_rate = 100 if total_automations > 0 else 0
        
    return {
        'summary': {
            'total_automations': total_automations,
            'active_automations': active_automations,
            'total_executions': total_executions,
            'success_rate': round(success_rate, 1)
        },
        'recent_executions': recent_executions[:10],
        'automations': [
            {
                'id': a['id'],
                'name': a['workflow_name'],
                'active': bool(a['active']),
                'execution_count': a['execution_count'],
                'last_execution': a['last_execution']
            }
            for a in automations
        ]
    }
