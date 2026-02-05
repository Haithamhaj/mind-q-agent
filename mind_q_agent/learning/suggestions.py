import logging
import random
from typing import List, Dict, Any
from mind_q_agent.learning.tracker import ConceptTracker
from mind_q_agent.tools import YouTubeSearchTool, ArxivSearchTool

logger = logging.getLogger(__name__)

class SuggestionService:
    """
    Proactive Suggestions Engine (Task 82).
    Analyzes active concepts and suggests external content or automations.
    """
    def __init__(self):
        # We would inject dependencies here in a real app
        self.tracker = ConceptTracker() # Assuming this connects to DB
        self.youtube = YouTubeSearchTool()
        self.arxiv = ArxivSearchTool()

    async def get_suggestions(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get proactive suggestions for the user"""
        suggestions = []
        
        try:
            # 1. Get currently active/top concepts for the user
            # For MVP, we'll mock or query the graph if connected.
            # Let's assume we get a list of concept strings.
            active_concepts = self._get_active_concepts(user_id)
            
            if not active_concepts:
                # Default fallback if no history
                active_concepts = ["Artificial Intelligence", "Python Automation"]

            # 2. Generate suggestions based on these concepts
            for concept in active_concepts[:3]: # Top 3 concepts
                # 50% chance to suggest video, 30% paper, 20% automation
                choice = random.random()
                
                if choice < 0.5:
                    # Suggest Video
                    videos = self.youtube.search(concept, max_results=1)
                    if videos:
                        video = videos[0]
                        suggestions.append({
                            "type": "video",
                            "title": f"Watch: {video.get('title')}",
                            "description": f"Since you're interested in {concept}...",
                            "link": video.get('url'),
                            "metadata": video
                        })
                elif choice < 0.8:
                    # Suggest Paper
                    papers = self.arxiv.search(concept, max_results=1)
                    if papers:
                        paper = papers[0]
                        suggestions.append({
                            "type": "paper",
                            "title": f"Read: {paper.get('title')}",
                            "description": f"New research on {concept}",
                            "link": paper.get('url'),
                            "metadata": paper
                        })
                else:
                    # Suggest Automation
                    suggestions.append({
                        "type": "automation",
                        "title": f"Automate {concept} Monitoring",
                        "description": "Create a daily digest workflow for this topic?",
                        "action": "create_workflow",
                        "payload": {"prompt": f"Create a daily digest for {concept}"}
                    })

            # Shuffle and limit
            random.shuffle(suggestions)
            return suggestions[:limit]

        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            return []

    def _get_active_concepts(self, user_id: str) -> List[str]:
        """Mock active concepts retrieval"""
        # In real impl, query Neo4j/Kuzu for top activation nodes
        return ["Generative AI", "FastAPI", "React Hooks"]
