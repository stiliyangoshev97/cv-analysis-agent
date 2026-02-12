"""
Configuration module for the CV Screening Agent.
Loads environment variables and provides app settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Anthropic API Configuration
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"
    
    # App Configuration
    app_name: str = "CV Screening Agent"
    debug: bool = False
    
    # File Upload Configuration
    max_file_size_mb: int = 10
    allowed_extensions: list[str] = [".pdf"]
    
    # JWT Authentication
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Google OAuth (optional)
    google_client_id: str = ""
    google_client_secret: str = ""
    
    # Frontend URL for OAuth redirects
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid re-reading .env on every call.
    """
    return Settings()
