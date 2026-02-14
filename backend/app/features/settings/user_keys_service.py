"""
User API Keys Service

Provides helper functions for retrieving user API keys for use in
CV evaluation, chat, and other AI-powered features.

This module bridges the settings system with the rest of the application,
ensuring that user-provided API keys are used instead of system keys.
"""

import uuid
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.features.settings.settings_repository import SettingsRepository


@dataclass
class UserAPIKeys:
    """Container for a user's API keys.
    
    Attributes:
        openai_key: OpenAI API key (required for embeddings).
        anthropic_key: Anthropic API key (optional, for Claude).
        gemini_key: Google Gemini API key (optional).
        default_provider: User's preferred LLM provider.
        default_model: User's preferred model for their provider.
    """
    openai_key: Optional[str] = None
    anthropic_key: Optional[str] = None
    gemini_key: Optional[str] = None
    default_provider: str = "anthropic"
    default_model: Optional[str] = None
    
    @property
    def has_openai(self) -> bool:
        """Check if OpenAI key is configured (required for embeddings)."""
        return bool(self.openai_key)
    
    @property
    def has_any_llm_key(self) -> bool:
        """Check if any LLM provider key is configured."""
        return bool(self.anthropic_key or self.openai_key or self.gemini_key)
    
    def get_llm_key(self) -> Optional[str]:
        """Get the API key for the user's preferred LLM provider."""
        if self.default_provider == "anthropic":
            return self.anthropic_key
        elif self.default_provider == "openai":
            return self.openai_key
        elif self.default_provider == "gemini":
            return self.gemini_key
        return None


class UserKeysService:
    """Service for retrieving user API keys.
    
    This service is designed to be used by other services (CV, Chat)
    that need to make API calls using the user's keys.
    
    Example:
        ```python
        async with get_db_session() as session:
            key_service = UserKeysService(session)
            keys = await key_service.get_user_keys(user_id)
            
            if not keys.has_openai:
                raise ValueError("OpenAI key required for embeddings")
            
            llm = get_llm(
                provider=keys.default_provider,
                api_key=keys.get_llm_key()
            )
        ```
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize service with database session.
        
        Args:
            session: Async SQLAlchemy session.
        """
        self.repository = SettingsRepository(session)
    
    async def get_user_keys(self, user_id: uuid.UUID) -> UserAPIKeys:
        """Get all API keys for a user.
        
        Args:
            user_id: User's UUID.
            
        Returns:
            UserAPIKeys dataclass with all available keys.
        """
        # Get API keys
        openai_key = await self.repository.get_decrypted_key(user_id, "openai")
        anthropic_key = await self.repository.get_decrypted_key(user_id, "anthropic")
        gemini_key = await self.repository.get_decrypted_key(user_id, "gemini")
        
        # Get user's agent config for preferred provider
        # Uses scorer_provider as the default for CV processing
        config = await self.repository.get_agent_config(user_id)
        
        # Determine default provider from agent config
        # Priority: scorer_provider > chat_provider > first available key
        default_provider = "anthropic"  # fallback
        default_model = None
        
        if config:
            # Use scorer provider as the primary for CV processing
            if config.scorer_provider:
                default_provider = config.scorer_provider
                default_model = config.scorer_model
            elif config.chat_provider:
                default_provider = config.chat_provider
                default_model = config.chat_model
        
        return UserAPIKeys(
            openai_key=openai_key,
            anthropic_key=anthropic_key,
            gemini_key=gemini_key,
            default_provider=default_provider,
            default_model=default_model,
        )
    
    async def validate_keys_for_cv_processing(self, user_id: uuid.UUID) -> UserAPIKeys:
        """Get and validate keys required for CV processing.
        
        CV processing requires:
        1. OpenAI key (for embeddings)
        2. At least one LLM key (for evaluation)
        
        Args:
            user_id: User's UUID.
            
        Returns:
            UserAPIKeys if all required keys are present.
            
        Raises:
            ValueError: If required keys are missing.
        """
        keys = await self.get_user_keys(user_id)
        
        if not keys.has_openai:
            raise ValueError(
                "OpenAI API key is required for CV processing. "
                "Please configure it in Settings → API Keys."
            )
        
        if not keys.has_any_llm_key:
            raise ValueError(
                "An LLM API key is required for CV evaluation. "
                "Please configure OpenAI, Anthropic, or Gemini in Settings → API Keys."
            )
        
        # Check that the preferred provider has a key
        llm_key = keys.get_llm_key()
        if not llm_key:
            # Try to find any available key and switch provider
            if keys.anthropic_key:
                keys.default_provider = "anthropic"
            elif keys.openai_key:
                keys.default_provider = "openai"
            elif keys.gemini_key:
                keys.default_provider = "gemini"
        
        return keys
