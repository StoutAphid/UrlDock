from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "UrlDock"
    debug: bool = True
    
    database_url: str = "sqlite:///./urldock.db"
    chroma_db_path: str = "./chroma_db"
    
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:latest"
    
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    fetcher_timeout: int = 30
    fetcher_user_agent: str = "UrlDock/1.0 (+https://github.com/StoutAphid/UrlDock)"
    
    max_content_length: int = 50000
    summary_max_sentences: int = 4
    max_tags: int = 4
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()