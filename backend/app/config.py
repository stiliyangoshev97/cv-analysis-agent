"""Application configuration module.

This module provides centralized configuration management using Pydantic
Settings. All configuration is loaded from environment variables with
fallback defaults.

Classes:
    Settings: Pydantic BaseSettings model with all app configuration.

Functions:
    get_settings: Get cached settings instance (singleton pattern).

Example:
    Using settings in application code::
    
        from app.config import get_settings
        
        settings = get_settings()
        print(f"App: {settings.app_name}")
        print(f"Debug: {settings.debug}")

Environment Variables:
    ANTHROPIC_API_KEY: API key for Claude AI (required for CV evaluation)
    CLAUDE_MODEL: Model to use (default: claude-sonnet-4-20250514)
    DEBUG: Enable debug mode (default: false)
    JWT_SECRET_KEY: Secret for signing JWTs (CHANGE IN PRODUCTION!)
    JWT_ALGORITHM: JWT signing algorithm (default: HS256)
    ACCESS_TOKEN_EXPIRE_MINUTES: Access token TTL (default: 30)
    REFRESH_TOKEN_EXPIRE_DAYS: Refresh token TTL (default: 7)
    GOOGLE_CLIENT_ID: Google OAuth client ID (optional)
    GOOGLE_CLIENT_SECRET: Google OAuth client secret (optional)
    FRONTEND_URL: Frontend URL for CORS and OAuth redirects

Note:
    Create a .env file in the backend directory with your configuration.
    See .env.example for a template.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    Uses Pydantic BaseSettings for automatic environment variable loading
    with type validation and default values.
    
    Attributes:
        anthropic_api_key: Anthropic API key for Claude AI access.
        claude_model: Claude model identifier for CV evaluation.
        app_name: Application display name.
        debug: Enable debug logging and error details.
        max_file_size_mb: Maximum allowed PDF upload size in MB.
        allowed_extensions: List of allowed file extensions.
        jwt_secret_key: Secret key for JWT signing (MUST change in prod).
        jwt_algorithm: JWT signing algorithm.
        access_token_expire_minutes: Access token lifetime in minutes.
        refresh_token_expire_days: Refresh token lifetime in days.
        google_client_id: Google OAuth 2.0 client ID.
        google_client_secret: Google OAuth 2.0 client secret.
        frontend_url: Frontend URL for CORS and OAuth redirects.
    
    Example:
        >>> settings = Settings()
        >>> settings.app_name
        'CV Screening Agent'
        >>> settings.access_token_expire_minutes
        30
    
    Note:
        The jwt_secret_key default is intentionally insecure.
        Always override it in production via environment variable.
    """
    
    # DEPRECATED: Legacy API key config (users now provide their own via Settings page)
    # These are kept for backwards compatibility but should not be used
    # anthropic_api_key: str = ""  # REMOVED - use user_api_keys table
    # claude_model: str = ""  # REMOVED - use user_agent_config table
    
    # App Configuration
    app_name: str = "CV Screening Agent"
    debug: bool = False
    
    # Database Configuration
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cv_screening_agent"
    
    # Encryption key for API keys (32 bytes, base64 encoded)
    # Generate with: python -c "import secrets; import base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
    encryption_key: str = ""
    
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
    
    # CORS allowed origins (comma-separated)
    cors_origins: str = "http://localhost:5173"
    
    # ==========================================================================
    # DEPRECATED: Server-level notification config removed
    # ==========================================================================
    # Email (SMTP) and WhatsApp (Twilio) credentials are now managed per-user
    # via BYOK (Bring Your Own Keys) in Settings > Notifications.
    # Users configure their own credentials which are stored encrypted in DB.
    # See: NotificationSettings model, notification_repository.py

    class Config:
        """Pydantic Settings configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings instance.
    
    Uses lru_cache to create a singleton, avoiding repeated .env file
    reads on every settings access.
    
    Returns:
        Settings instance with configuration loaded from environment.
    
    Example:
        >>> settings = get_settings()
        >>> settings.app_name
        'CV Screening Agent'
    
    Note:
        To reload settings (e.g., in tests), call get_settings.cache_clear()
    """
    return Settings()
