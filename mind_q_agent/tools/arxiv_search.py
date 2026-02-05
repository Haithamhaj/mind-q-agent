import urllib.request
import feedparser
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ArxivSearchTool:
    """Tool for searching ArXiv papers"""
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search ArXiv API"""
        try:
            # ArXiv API
            base_url = 'http://export.arxiv.org/api/query?'
            # Simple query construction
            search_query = f'search_query=all:{query}&start=0&max_results={max_results}'
            
            response = urllib.request.urlopen(base_url + search_query).read()
            feed = feedparser.parse(response)
            
            results = []
            for entry in feed.entries:
                results.append({
                    "title": entry.title,
                    "url": entry.id,
                    "summary": entry.summary,
                    "authors": [author.name for author in entry.authors],
                    "published": entry.published
                })
            
            return results
            
        except Exception as e:
            logger.error(f"ArXiv search failed: {e}")
            return []
