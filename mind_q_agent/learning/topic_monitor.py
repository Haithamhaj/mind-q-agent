import logging
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from mind_q_agent.tools import YouTubeSearchTool, ArxivSearchTool

logger = logging.getLogger(__name__)

class TopicMonitorService:
    """
    Topic Monitoring System (Task 83).
    Periodically checks for new content on watched topics.
    """
    def __init__(self):
        self.youtube = YouTubeSearchTool()
        self.arxiv = ArxivSearchTool()
        self.watched_topics = {} # In-memory store for MVP. Real app uses DB.

    def add_topic(self, user_id: str, topic: str):
        """Add a topic to watch list"""
        if user_id not in self.watched_topics:
            self.watched_topics[user_id] = set()
        self.watched_topics[user_id].add(topic)
        logger.info(f"User {user_id} is now watching: {topic}")

    def get_topics(self, user_id: str) -> List[str]:
        return list(self.watched_topics.get(user_id, []))

    def remove_topic(self, user_id: str, topic: str):
        if user_id in self.watched_topics:
            self.watched_topics[user_id].discard(topic)

    async def check_updates(self, user_id: str) -> List[Dict[str, Any]]:
        """Check for updates on all watched topics"""
        updates = []
        topics = self.get_topics(user_id)
        
        if not topics:
            return []
            
        logger.info(f"Checking updates for {user_id} on topics: {topics}")
        
        for topic in topics:
            # 1. Check YouTube
            try:
                videos = self.youtube.search(topic, max_results=1)
                if videos:
                    updates.append({
                        "topic": topic,
                        "source": "YouTube",
                        "title": videos[0].get('title'),
                        "url": videos[0].get('url'),
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error checking YouTube for {topic}: {e}")

            # 2. Check ArXiv
            try:
                papers = self.arxiv.search(topic, max_results=1)
                if papers:
                    updates.append({
                        "topic": topic,
                        "source": "ArXiv",
                        "title": papers[0].get('title'),
                        "url": papers[0].get('url'),
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error checking ArXiv for {topic}: {e}")
                
        return updates
