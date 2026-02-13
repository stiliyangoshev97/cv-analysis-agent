"""Repository for notification settings database operations.

This module provides database operations for the NotificationSettings model.

Classes:
    NotificationRepository: CRUD operations for notification settings.

Example:
    repo = NotificationRepository(session)
    settings = await repo.get_by_user_id(user_id)
    if not settings:
        settings = await repo.create(user_id)
"""

import logging
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.notification import NotificationSettings

logger = logging.getLogger(__name__)


class NotificationRepository:
    """Repository for notification settings operations.
    
    Provides CRUD operations for user notification preferences.
    
    Attributes:
        session: AsyncSession for database operations.
    
    Example:
        >>> repo = NotificationRepository(session)
        >>> settings = await repo.get_or_create(user_id)
        >>> settings.email_enabled = True
        >>> await repo.update(settings)
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy AsyncSession.
        """
        self.session = session
    
    async def get_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> Optional[NotificationSettings]:
        """Get notification settings for a user.
        
        Args:
            user_id: UUID of the user.
        
        Returns:
            NotificationSettings if found, None otherwise.
        """
        result = await self.session.execute(
            select(NotificationSettings).where(
                NotificationSettings.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        user_id: uuid.UUID,
        email_enabled: bool = False,
        whatsapp_enabled: bool = False,
        whatsapp_number: Optional[str] = None,
        threshold_score: int = 80,
    ) -> NotificationSettings:
        """Create notification settings for a user.
        
        Args:
            user_id: UUID of the user.
            email_enabled: Enable email notifications.
            whatsapp_enabled: Enable WhatsApp notifications.
            whatsapp_number: WhatsApp phone number.
            threshold_score: Score threshold for notifications.
        
        Returns:
            Created NotificationSettings instance.
        """
        settings = NotificationSettings(
            user_id=user_id,
            email_enabled=email_enabled,
            whatsapp_enabled=whatsapp_enabled,
            whatsapp_number=whatsapp_number,
            threshold_score=threshold_score,
        )
        self.session.add(settings)
        await self.session.flush()
        await self.session.refresh(settings)
        logger.info(f"Created notification settings for user: {user_id}")
        return settings
    
    async def get_or_create(
        self,
        user_id: uuid.UUID,
    ) -> NotificationSettings:
        """Get or create notification settings for a user.
        
        Args:
            user_id: UUID of the user.
        
        Returns:
            Existing or newly created NotificationSettings.
        """
        settings = await self.get_by_user_id(user_id)
        if not settings:
            settings = await self.create(user_id)
        return settings
    
    async def update(
        self,
        settings: NotificationSettings,
    ) -> NotificationSettings:
        """Update notification settings.
        
        Args:
            settings: The settings instance to update.
        
        Returns:
            Updated NotificationSettings instance.
        """
        self.session.add(settings)
        await self.session.flush()
        await self.session.refresh(settings)
        logger.debug(f"Updated notification settings: {settings.id}")
        return settings
    
    async def delete(
        self,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete notification settings for a user.
        
        Args:
            user_id: UUID of the user.
        
        Returns:
            True if deleted, False if not found.
        """
        settings = await self.get_by_user_id(user_id)
        if settings:
            await self.session.delete(settings)
            await self.session.flush()
            logger.info(f"Deleted notification settings for user: {user_id}")
            return True
        return False
