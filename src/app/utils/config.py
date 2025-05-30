"""
Configuration settings for the application
"""
import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    app_name: str = "AI Document Analysis"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Security
    secret_key: str = "development_secret_key_change_in_production"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///data/chat_history.db"
    
    # OpenAI Settings (will be set via UI)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.7
    
    # Performance Settings
    max_document_size: int = 1024 * 1024  # 1MB
    max_chunk_size: int = 4000  # tokens
    query_timeout: int = 30  # seconds
    
    # Rate Limiting
    rate_limit_requests: int = 10
    rate_limit_window: int = 60  # seconds
    
    # CORS Settings
    cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # Redis Settings (optional)
    redis_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
