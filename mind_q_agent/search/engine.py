import logging
from typing import List, Dict, Any, Optional

from mind_q_agent.vector.chroma_vector import ChromaVectorDB

logger = logging.getLogger(__name__)

class SearchEngine:
    """
    Search Engine component for Semantic Search.
    Wraps the Vector Store interaction and formats results.
    """

    def __init__(self, vector_store: ChromaVectorDB):
        """
        Initialize Search Engine.
        
        Args:
            vector_store: Initialized ChromaVectorDB instance.
        """
        self.vector_store = vector_store

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search for a query.
        
        Args:
            query: The search query string.
            limit: Maximum number of results to return (default 5).
            
        Returns:
            List of result dictionaries containing:
            - id: Document ID (Hash)
            - text: Document/Chunk text
            - score: Similarity score (distance)
            - metadata: File metadata
        """
        if not query or not query.strip():
            return []

        try:
            results = self.vector_store.query_similar(query, n_results=limit)
            
            # ChromaDB query_similar already formats result as:
            # [{'id': id, 'document': text, 'metadata': dict, 'distance': float}, ...]
            # We can perform additional formatting or filtering here if needed.
            
            formatted_results = []
            for res in results:
                formatted_results.append({
                    "id": res.get("id"),
                    "text": res.get("document"),
                    "score": res.get("distance"), # Lower is better in Chroma usually (L2)
                    "metadata": res.get("metadata", {})
                })
            
            return formatted_results

        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return []
