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
            context_str = ""
            if results:
                for i, doc in enumerate(results):
                    content = doc.get('content', 'No content')[:500] + "..." # Truncate for token limit safety
                    source = doc.get('metadata', {}).get('source', 'Unknown')
                    context_str += f"[Source: {source}]\n{content}\n\n"
            else:
                context_str = "No specific documents found."
            
            # 3. Get Prompt from Manager
            from mind_q_agent.llm.prompts.manager import prompt_manager
            system_prompt = prompt_manager.get_system_prompt(context=context_str)
            
            return system_prompt
            
        except Exception as e:
            logger.error(f"Error building context: {e}")
            from mind_q_agent.llm.prompts.manager import prompt_manager
            return prompt_manager.get_system_prompt(context="Error retrieving context.")

