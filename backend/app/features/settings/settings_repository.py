"""
Settings Repository

Database operations for user API keys and agent configurations.
"""

import uuid
from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserApiKey, UserAgentConfig
from app.db.encryption import encrypt_api_key, decrypt_api_key, get_key_hint


class SettingsRepository:
    """Repository for user settings database operations.
    
    Handles CRUD operations for UserApiKey and UserAgentConfig.
    API keys are encrypted before storage using AES-256.
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
    
    # =========================================================================
    # API KEY OPERATIONS
    # =========================================================================
    
    async def get_api_keys(self, user_id: uuid.UUID) -> list[UserApiKey]:
        """Get all API keys for a user.
        
        Args:
            user_id: User's UUID.
            
        Returns:
            List of UserApiKey records.
        """
        result = await self.session.execute(
            select(UserApiKey).where(UserApiKey.user_id == user_id)
        )
        return list(result.scalars().all())
    
    async def get_api_key(
        self,
        user_id: uuid.UUID,
        provider: str
    ) -> Optional[UserApiKey]:
        """Get a specific API key by provider.
        
        Args:
            user_id: User's UUID.
            provider: AI provider name (openai, anthropic, gemini).
            
        Returns:
            UserApiKey if found, None otherwise.
        """
        result = await self.session.execute(
            select(UserApiKey).where(
                UserApiKey.user_id == user_id,
                UserApiKey.provider == provider
            )
        )
        return result.scalar_one_or_none()
    
    async def set_api_key(
        self,
        user_id: uuid.UUID,
        provider: str,
        api_key: str,
        is_valid: bool = True
    ) -> UserApiKey:
        """Set or update an API key for a provider.
        
        Args:
            user_id: User's UUID.
            provider: AI provider name.
            api_key: Plain text API key (will be encrypted).
            is_valid: Whether the key has been validated.
            
        Returns:
            Created or updated UserApiKey record.
        """
        # Check if key exists
        existing = await self.get_api_key(user_id, provider)
        
        encrypted = encrypt_api_key(api_key)
        hint = get_key_hint(api_key)
        
        if existing:
            # Update existing
            existing.encrypted_key = encrypted
            existing.key_hint = hint
            existing.is_valid = is_valid
            await self.session.commit()
            await self.session.refresh(existing)
            return existing
        else:
            # Create new
            new_key = UserApiKey(
                user_id=user_id,
                provider=provider,
                encrypted_key=encrypted,
                key_hint=hint,
                is_valid=is_valid
            )
            self.session.add(new_key)
            await self.session.commit()
            await self.session.refresh(new_key)
            return new_key
    
    async def delete_api_key(self, user_id: uuid.UUID, provider: str) -> bool:
        """Delete an API key.
        
        Args:
            user_id: User's UUID.
            provider: AI provider name.
            
        Returns:
            True if deleted, False if not found.
        """
        result = await self.session.execute(
            delete(UserApiKey).where(
                UserApiKey.user_id == user_id,
                UserApiKey.provider == provider
            )
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_decrypted_key(
        self,
        user_id: uuid.UUID,
        provider: str
    ) -> Optional[str]:
        """Get decrypted API key for a provider.
        
        Args:
            user_id: User's UUID.
            provider: AI provider name.
            
        Returns:
            Decrypted API key if found, None otherwise.
        """
        key_record = await self.get_api_key(user_id, provider)
        if key_record:
            return decrypt_api_key(key_record.encrypted_key)
        return None
    
    # =========================================================================
    # AGENT CONFIG OPERATIONS
    # =========================================================================
    
    async def get_agent_config(
        self,
        user_id: uuid.UUID
    ) -> Optional[UserAgentConfig]:
        """Get user's agent configuration.
        
        Args:
            user_id: User's UUID.
            
        Returns:
            UserAgentConfig if found, None otherwise.
        """
        result = await self.session.execute(
            select(UserAgentConfig).where(UserAgentConfig.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create_agent_config(
        self,
        user_id: uuid.UUID
    ) -> UserAgentConfig:
        """Get or create user's agent configuration.
        
        Args:
            user_id: User's UUID.
            
        Returns:
            Existing or new UserAgentConfig.
        """
        existing = await self.get_agent_config(user_id)
        if existing:
            return existing
        
        # Create with defaults
        config = UserAgentConfig(user_id=user_id)
        self.session.add(config)
        await self.session.commit()
        await self.session.refresh(config)
        return config
    
    async def update_agent_config(
        self,
        user_id: uuid.UUID,
        **kwargs
    ) -> UserAgentConfig:
        """Update user's agent configuration.
        
        Args:
            user_id: User's UUID.
            **kwargs: Fields to update.
            
        Returns:
            Updated UserAgentConfig.
        """
        config = await self.get_or_create_agent_config(user_id)
        
        # Update only provided fields
        for key, value in kwargs.items():
            if hasattr(config, key) and value is not None:
                setattr(config, key, value)
        
        await self.session.commit()
        await self.session.refresh(config)
        return config
