from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, AsyncGenerator
from fastapi.responses import StreamingResponse

import logging
from mind_q_agent.rag.context import ContextBuilder
from mind_q_agent.llm.config import ModelConfig
from mind_q_agent.llm.providers.ollama import OllamaProvider

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

logger = logging.getLogger(__name__)

# Request Model
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "llama3" # Default model
    provider: Optional[str] = "ollama"
    temperature: Optional[float] = 0.7
    stream: bool = False

# Response Model (non-streaming)
class ChatResponse(BaseModel):
    response: str
    context_used: bool = True
    sources: List[str] = []

# Dependency (Singleton-like)
class ChatService:
    def __init__(self):
        self.context_builder = ContextBuilder()
        
    async def get_response(self, req: ChatRequest):
        # 1. Build Context
        system_prompt = self.context_builder.build_system_prompt(req.message)
        
        # 2. Init Provider
        # In prod, we'd reuse providers or have a factory
        config = ModelConfig(
            provider=req.provider,
            model_name=req.model,
            temperature=req.temperature
        )
        
        if req.provider == "ollama":
            provider = OllamaProvider(config)
        else:
            # Fallback or error
            raise ValueError(f"Provider {req.provider} not supported yet")
            
        try:
            if req.stream:
                return provider.stream(req.message, system_prompt=system_prompt)
            else:
                response_text = await provider.generate(req.message, system_prompt=system_prompt)
                return ChatResponse(response=response_text)
        finally:
             if not req.stream:
                 await provider.close()

# Initialize Service
try:
    chat_service = ChatService()
except Exception as e:
    logger.error(f"Failed to init ChatService: {e}")
    chat_service = None

@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Chat with Mind-Q (RAG enabled).
    """
    if not chat_service:
        raise HTTPException(status_code=500, detail="Chat service not initialized")
        
    try:
        # For non-streaming, we return JSON
        if not req.stream:
            return await chat_service.get_response(req)
        
        # For streaming, we need a StreamingResponse
        else:
            # We need to manage the provider lifecycle differently for streaming
            # Re-creating provider logic here for simplicity of generator
            
            async def event_generator():
                # 1. Context
                system_prompt = chat_service.context_builder.build_system_prompt(req.message)
                
                # 2. Provider
                config = ModelConfig(
                    provider=req.provider,
                    model_name=req.model,
                    temperature=req.temperature
                )
                provider = OllamaProvider(config)
                
                try:
                    async for chunk in provider.stream(req.message, system_prompt=system_prompt):
                        yield chunk
                finally:
                    await provider.close()

            return StreamingResponse(event_generator(), media_type="text/plain")

    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
