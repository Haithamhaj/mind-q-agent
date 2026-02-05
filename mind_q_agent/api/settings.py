from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    API_TITLE: str = "Mind-Q Agent API"
    API_VERSION: str = "0.4.0"
    API_prefix: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database
    KUZU_DB_PATH: str = os.getenv("KUZU_DB_PATH", "./data/mind_q_db")
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")

    # LLM - LlamaCpp
    LLAMACPP_MODEL_PATH: str = os.getenv("LLAMACPP_MODEL_PATH", "./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    LLAMACPP_N_CTX: int = int(os.getenv("LLAMACPP_N_CTX", 2048))
    LLAMACPP_N_GPU_LAYERS: int = int(os.getenv("LLAMACPP_N_GPU_LAYERS", -1))
    
    class Config:
        env_file = ".env"

settings = Settings()
