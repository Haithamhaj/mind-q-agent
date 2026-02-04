import logging
from typing import List, Dict, Any, Optional
from mind_q_agent.search.engine import SearchEngine
from mind_q_agent.graph.kuzu_graph import KuzuGraphDB
from mind_q_agent.api.settings import settings

logger = logging.getLogger(__name__)

from mind_q_agent.vector.chroma_vector import ChromaVectorDB

class ContextBuilder:
    """
    Builds context for LLM generation by retrieving relevant information
    from Vector Store (Chroma) and Knowledge Graph (Kuzu).
    """

    def __init__(self):
        # Initialize engines
        # Note: In a real app, these might be injected or singletons
        try:
            self.vector_db = ChromaVectorDB(db_path=settings.CHROMA_DB_PATH)
            self.search_engine = SearchEngine(vector_store=self.vector_db)
            
            # For now, we rely only on Vector Search for RAG context
            # GraphDB connection can be added later for structured context
        except Exception as e:
            logger.error(f"Failed to init ContextBuilder dependencies: {e}")
            raise

    def build_system_prompt(self, query: str, max_docs: int = 5) -> str:
        """
        Construct a system prompt with retrieved context.
        """
        try:
            # 1. Vector Search
            results = self.search_engine.search(query, limit=max_docs)
            
            # 2. Format Context
            context_str = "You are Mind-Q, an intelligent personal knowledge agent.\n"
            context_str += "Answer the user's question based strictly on the following context:\n\n"
            
            if not results:
                context_str += "No specific documents found.\n"
            else:
                context_str += "--- RETRIEVED DOCUMENTS ---\n"
                for i, doc in enumerate(results):
                    # content is in doc['content'] or similar based on SearchEngine implementation
                    # Let's assume standard Chroma result structure or SearchEngine wrapper output
                    # The SearchEngine.search returns a list of dicts with 'content', 'metadata' etc.
                    content = doc.get('content', 'No content')[:500] + "..." # Truncate for token limit safety
                    source = doc.get('metadata', {}).get('source', 'Unknown')
                    
                    context_str += f"[Source: {source}]\n{content}\n\n"
            
            context_str += "--- END CONTEXT ---\n"
            context_str += "If the answer is not in the context, say so gracefully. Do not hallucinate."
            
            return context_str
            
        except Exception as e:
            logger.error(f"Error building context: {e}")
            return "You are Mind-Q, an intelligent assistant. Error retrieving context."

