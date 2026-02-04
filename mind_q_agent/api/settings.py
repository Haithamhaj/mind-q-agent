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
    
    class Config:
        env_file = ".env"

settings = Settings()
