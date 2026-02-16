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
from app.db.encryption import encrypt_api_key, decrypt_api_key, get_key_hint

logger = logging.getLogger(__name__)


def _mask_email(email: str) -> str:
    """Mask an email address for display.
    
    Args:
        email: Email address to mask.
    
    Returns:
        Masked email (e.g., "u***@example.com").
    """
    if not email or "@" not in email:
        return "***"
    local, domain = email.rsplit("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "***"
    else:
        masked_local = local[0] + "***" + local[-1]
    return f"{masked_local}@{domain}"


def _mask_phone(phone: str) -> str:
    """Mask a phone number for display.
    
    Args:
        phone: Phone number to mask.
    
    Returns:
        Masked number (e.g., "+1***7890").
    """
    if not phone or len(phone) < 8:
        return "***"
    return phone[:3] + "***" + phone[-4:]


class NotificationRepository:
    """Repository for notification settings operations.
    
    Provides CRUD operations for user notification preferences.
    Handles encryption/decryption of sensitive credentials.
    
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
    
    # =========================================================================
    # SMTP Configuration (BYOK)
    # =========================================================================
    
    async def update_smtp_config(
        self,
        settings: NotificationSettings,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        use_tls: Optional[bool] = None,
    ) -> NotificationSettings:
        """Update SMTP configuration with encryption.
        
        Args:
            settings: NotificationSettings instance to update.
            host: SMTP server hostname.
            port: SMTP server port.
            username: SMTP username (will be encrypted).
            password: SMTP password (will be encrypted).
            from_email: Sender email (will be encrypted).
            from_name: Sender display name.
            use_tls: Whether to use TLS.
        
        Returns:
            Updated NotificationSettings.
        """
        if host is not None:
            settings.smtp_host = encrypt_api_key(host) if host else None
        if port is not None:
            settings.smtp_port = port
        if username is not None:
            settings.smtp_username = encrypt_api_key(username) if username else None
        if password is not None:
            settings.smtp_password = encrypt_api_key(password) if password else None
        if from_email is not None:
            settings.smtp_from_email = encrypt_api_key(from_email) if from_email else None
        if from_name is not None:
            settings.smtp_from_name = from_name
        if use_tls is not None:
            settings.smtp_use_tls = use_tls
        
        return await self.update(settings)
    
    def get_decrypted_smtp_config(
        self,
        settings: NotificationSettings,
    ) -> dict:
        """Get decrypted SMTP configuration.
        
        Args:
            settings: NotificationSettings instance.
        
        Returns:
            Dict with decrypted SMTP credentials.
        """
        if not settings.has_smtp_config:
            return {}
        
        try:
            return {
                "host": decrypt_api_key(settings.smtp_host) if settings.smtp_host else None,
                "port": settings.smtp_port,
                "username": decrypt_api_key(settings.smtp_username) if settings.smtp_username else None,
                "password": decrypt_api_key(settings.smtp_password) if settings.smtp_password else None,
                "from_email": decrypt_api_key(settings.smtp_from_email) if settings.smtp_from_email else None,
                "from_name": settings.smtp_from_name,
                "use_tls": settings.smtp_use_tls,
            }
        except Exception as e:
            logger.error(f"Failed to decrypt SMTP config: {e}")
            return {}
    
    def get_smtp_config_hints(
        self,
        settings: NotificationSettings,
    ) -> dict:
        """Get SMTP configuration with masked credentials.
        
        Args:
            settings: NotificationSettings instance.
        
        Returns:
            Dict with masked SMTP info for display.
        """
        if not settings.has_smtp_config:
            return {
                "configured": False,
                "host": None,
                "port": None,
                "from_email_hint": None,
                "from_name": None,
                "use_tls": True,
            }
        
        try:
            from_email = decrypt_api_key(settings.smtp_from_email) if settings.smtp_from_email else None
            host = decrypt_api_key(settings.smtp_host) if settings.smtp_host else None
            
            return {
                "configured": True,
                "host": host,
                "port": settings.smtp_port,
                "from_email_hint": _mask_email(from_email) if from_email else None,
                "from_name": settings.smtp_from_name,
                "use_tls": settings.smtp_use_tls,
            }
        except Exception as e:
            logger.error(f"Failed to get SMTP hints: {e}")
            return {"configured": False}
    
    # =========================================================================
    # Twilio Configuration (BYOK)
    # =========================================================================
    
    async def update_twilio_config(
        self,
        settings: NotificationSettings,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        whatsapp_from: Optional[str] = None,
    ) -> NotificationSettings:
        """Update Twilio configuration with encryption.
        
        Args:
            settings: NotificationSettings instance to update.
            account_sid: Twilio account SID (will be encrypted).
            auth_token: Twilio auth token (will be encrypted).
            whatsapp_from: WhatsApp sender number (will be encrypted).
        
        Returns:
            Updated NotificationSettings.
        """
        if account_sid is not None:
            settings.twilio_account_sid = encrypt_api_key(account_sid) if account_sid else None
        if auth_token is not None:
            settings.twilio_auth_token = encrypt_api_key(auth_token) if auth_token else None
        if whatsapp_from is not None:
            settings.twilio_whatsapp_from = encrypt_api_key(whatsapp_from) if whatsapp_from else None
        
        return await self.update(settings)
    
    def get_decrypted_twilio_config(
        self,
        settings: NotificationSettings,
    ) -> dict:
        """Get decrypted Twilio configuration.
        
        Args:
            settings: NotificationSettings instance.
        
        Returns:
            Dict with decrypted Twilio credentials.
        """
        if not settings.has_twilio_config:
            return {}
        
        try:
            return {
                "account_sid": decrypt_api_key(settings.twilio_account_sid) if settings.twilio_account_sid else None,
                "auth_token": decrypt_api_key(settings.twilio_auth_token) if settings.twilio_auth_token else None,
                "whatsapp_from": decrypt_api_key(settings.twilio_whatsapp_from) if settings.twilio_whatsapp_from else None,
            }
        except Exception as e:
            logger.error(f"Failed to decrypt Twilio config: {e}")
            return {}
    
    def get_twilio_config_hints(
        self,
        settings: NotificationSettings,
    ) -> dict:
        """Get Twilio configuration with masked credentials.
        
        Args:
            settings: NotificationSettings instance.
        
        Returns:
            Dict with masked Twilio info for display.
        """
        if not settings.has_twilio_config:
            return {
                "configured": False,
                "account_sid_hint": None,
                "whatsapp_from_hint": None,
            }
        
        try:
            account_sid = decrypt_api_key(settings.twilio_account_sid) if settings.twilio_account_sid else None
            whatsapp_from = decrypt_api_key(settings.twilio_whatsapp_from) if settings.twilio_whatsapp_from else None
            
            return {
                "configured": True,
                "account_sid_hint": get_key_hint(account_sid) if account_sid else None,
                "whatsapp_from_hint": _mask_phone(whatsapp_from) if whatsapp_from else None,
            }
        except Exception as e:
            logger.error(f"Failed to get Twilio hints: {e}")
            return {"configured": False}
    
    async def clear_smtp_config(
        self,
        settings: NotificationSettings,
    ) -> NotificationSettings:
        """Clear SMTP configuration.
        
        Args:
            settings: NotificationSettings instance.
        
        Returns:
            Updated NotificationSettings.
        """
        settings.smtp_host = None
        settings.smtp_port = 587
        settings.smtp_username = None
        settings.smtp_password = None
        settings.smtp_from_email = None
        settings.smtp_from_name = "CV Screening Agent"
        settings.smtp_use_tls = True
        return await self.update(settings)
    
    async def clear_twilio_config(
        self,
        settings: NotificationSettings,
    ) -> NotificationSettings:
        """Clear Twilio configuration.
        
        Args:
            settings: NotificationSettings instance.
        
        Returns:
            Updated NotificationSettings.
        """
        settings.twilio_account_sid = None
        settings.twilio_auth_token = None
        settings.twilio_whatsapp_from = None
        return await self.update(settings)
