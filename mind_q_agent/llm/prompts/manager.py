from typing import Dict, Any, Optional
from .templates import SYSTEM_PERSONA, BASIC_CHAT_TEMPLATE, QUERY_REWRITE_TEMPLATE

class PromptManager:
    """
    Centralized manager for LLM prompts to ensure consistency.
    """
    
    def get_system_prompt(self, context: str = "") -> str:
        """
        Returns the main system prompt with context injected.
        """
        if not context:
            # If no context, we might want a slightly different prompt or just empty context
            return SYSTEM_PERSONA.format(context="No specific context provided.")
            
        return SYSTEM_PERSONA.format(context=context)

    def get_basic_chat_prompt(self, question: str) -> str:
        return BASIC_CHAT_TEMPLATE.format(question=question)

    def get_query_rewrite_prompt(self, question: str) -> str:
        return QUERY_REWRITE_TEMPLATE.format(question=question)

prompt_manager = PromptManager()
