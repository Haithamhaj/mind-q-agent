from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from mind_q_agent.tools import YouTubeSearchTool, ArxivSearchTool

from mind_q_agent.learning.suggestions import SuggestionService
from mind_q_agent.learning.topic_monitor import TopicMonitorService
from mind_q_agent.learning.progress import LearningProgressService
from mind_q_agent.learning.tagging import SmartTaggingService
from mind_q_agent.learning.qa import QAService
from mind_q_agent.learning.research import ResearchAssistant
from pydantic import BaseModel

router = APIRouter(prefix="/smart", tags=["smart-features"])

# Initialize tools
youtube_tool = YouTubeSearchTool()
arxiv_tool = ArxivSearchTool()
suggestion_service = SuggestionService()
monitor_service = TopicMonitorService()
progress_service = LearningProgressService()
tagging_service = SmartTaggingService()
qa_service = QAService()
research_assistant = ResearchAssistant()

# --- Learning Progress ---
class GoalRequest(BaseModel):
    title: str
    user_id: str = "user1"

class TagRequest(BaseModel):
    text: str

class QARequest(BaseModel):
    question: str

class ResearchRequest(BaseModel):
    topic: str
    depth: str = "brief" # brief or deep

@router.post("/research/generate")
async def generate_report(req: ResearchRequest):
    """Generate a research report"""
    return await research_assistant.generate_report(req.topic, req.depth)

@router.post("/qa/ask")
async def ask_question(req: QARequest):
    """Ask a question (RAG + Web)"""
    return await qa_service.answer_question(req.question)

@router.post("/tags/generate")
async def generate_tags(req: TagRequest):
    """Auto-generate tags for text"""
    return await tagging_service.generate_tags(req.text)

@router.get("/tags/suggest")
async def suggest_tags(q: str):
    """Autocomplete tag suggestions"""
    return await tagging_service.suggest_tags(q)

@router.get("/tags/hierarchy")
async def get_tag_hierarchy(tag: str):
    """Get tag hierarchy"""
    return await tagging_service.get_hierarchy(tag)

@router.post("/learning/goals")
async def add_goal(req: GoalRequest):
    """Add learning goal"""
    goal_id = progress_service.add_goal(req.user_id, req.title)
    return {"status": "added", "id": goal_id}

@router.get("/learning/goals")
async def get_goals(user_id: str = "user1"):
    """Get learning goals"""
    return progress_service.get_goals(user_id)

@router.get("/learning/mastery")
async def get_mastery(user_id: str = "user1"):
    """Get concept mastery"""
    return progress_service.get_mastery(user_id)

# --- Monitoring ---
@router.post("/monitor/add")
async def add_watched_topic(topic: str, user_id: str = "user1"):
    """Star/Watch a topic"""
    monitor_service.add_topic(user_id, topic)
    return {"status": "added", "topic": topic}

@router.get("/monitor/list")
async def list_watched_topics(user_id: str = "user1"):
    """List watched topics"""
    return monitor_service.get_topics(user_id)

@router.post("/monitor/check")
async def check_updates(user_id: str = "user1"):
    """Trigger update check"""
    return await monitor_service.check_updates(user_id)

# --- Search & Suggestions ---
@router.get("/search/youtube")
async def search_youtube(q: str, max_results: int = 5):

    """Search YouTube videos"""
    return youtube_tool.search(q, max_results)

@router.get("/search/arxiv")
async def search_arxiv(q: str, max_results: int = 5):
    """Search ArXiv papers"""
    return arxiv_tool.search(q, max_results)

@router.get("/suggestions")
async def get_proactive_suggestions(user_id: str = "user1", limit: int = 5):
    """Get proactive suggestions based on user activity"""
    return await suggestion_service.get_suggestions(user_id, limit)

@router.get("/search/suggestions")
async def get_search_suggestions(q: str):
    """Get smart search suggestions (mock for now)"""
    return [
        f"{q} tutorial",
        f"{q} advanced concepts",
        f"{q} whitepaper",
        f"latest research on {q}"
    ]
