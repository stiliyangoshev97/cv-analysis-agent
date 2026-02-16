"""Controller for notification endpoints.

This module handles HTTP request/response logic for notification settings.
Supports BYOK (Bring Your Own Keys) for SMTP and Twilio credentials.

Classes:
    NotificationController: HTTP handlers for notification endpoints.

Example:
    controller = NotificationController(session, current_user)
    settings = await controller.get_settings()
"""

import logging
import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from .notification_service import NotificationService
from .notification_repository import NotificationRepository
from .notification_schemas import (
    NotificationSettingsResponse,
    NotificationSettingsUpdate,
    NotificationResultResponse,
    SmtpConfigResponse,
    TwilioConfigResponse,
)

logger = logging.getLogger(__name__)


class NotificationController:
    """Controller for notification HTTP handlers.
    
    Handles request validation, calls the service layer,
    and formats HTTP responses.
    
    Attributes:
        session: AsyncSession for database operations.
        current_user: The authenticated user.
        service: NotificationService instance.
        repo: NotificationRepository instance.
    
    Example:
        >>> controller = NotificationController(session, user)
        >>> settings = await controller.get_settings()
    """
    
    def __init__(
        self,
        session: AsyncSession,
        current_user: User,
    ) -> None:
        """Initialize controller.
        
        Args:
            session: SQLAlchemy AsyncSession.
            current_user: Authenticated user.
        """
        self.session = session
        self.current_user = current_user
        self.service = NotificationService(session)
        self.repo = NotificationRepository(session)
    
    def _build_settings_response(self, settings) -> NotificationSettingsResponse:
        """Build NotificationSettingsResponse with config hints.
        
        Args:
            settings: NotificationSettings model instance.
        
        Returns:
            NotificationSettingsResponse with masked credentials.
        """
        # Mask WhatsApp number for security (show last 4 digits)
        masked_number = None
        if settings.whatsapp_number:
            masked_number = f"***{settings.whatsapp_number[-4:]}"
        
        # Get SMTP config hints
        smtp_hints = self.repo.get_smtp_config_hints(settings)
        smtp_config = SmtpConfigResponse(
            configured=smtp_hints.get("configured", False),
            host=smtp_hints.get("host"),
            port=smtp_hints.get("port"),
            from_email_hint=smtp_hints.get("from_email_hint"),
            from_name=smtp_hints.get("from_name"),
            use_tls=smtp_hints.get("use_tls", True),
        )
        
        # Get Twilio config hints
        twilio_hints = self.repo.get_twilio_config_hints(settings)
        twilio_config = TwilioConfigResponse(
            configured=twilio_hints.get("configured", False),
            account_sid_hint=twilio_hints.get("account_sid_hint"),
            whatsapp_from_hint=twilio_hints.get("whatsapp_from_hint"),
        )
        
        return NotificationSettingsResponse(
            email_enabled=settings.email_enabled,
            whatsapp_enabled=settings.whatsapp_enabled,
            whatsapp_number=masked_number,
            threshold_score=settings.threshold_score,
            smtp_config=smtp_config,
            twilio_config=twilio_config,
        )
    
    async def get_settings(self) -> NotificationSettingsResponse:
        """Get current user's notification settings.
        
        Returns:
            NotificationSettingsResponse with current settings.
        """
        settings = await self.service.get_settings(self.current_user.id)
        return self._build_settings_response(settings)
    
    async def update_settings(
        self,
        update_data: NotificationSettingsUpdate,
    ) -> NotificationSettingsResponse:
        """Update notification settings.
        
        Args:
            update_data: Fields to update.
        
        Returns:
            NotificationSettingsResponse with updated settings.
        """
        # Convert SMTP/Twilio config to dicts if provided
        smtp_config = None
        if update_data.smtp_config:
            smtp_config = {
                "host": update_data.smtp_config.host,
                "port": update_data.smtp_config.port,
                "username": update_data.smtp_config.username,
                "password": update_data.smtp_config.password,
                "from_email": update_data.smtp_config.from_email,
                "from_name": update_data.smtp_config.from_name,
                "use_tls": update_data.smtp_config.use_tls,
            }
        
        twilio_config = None
        if update_data.twilio_config:
            twilio_config = {
                "account_sid": update_data.twilio_config.account_sid,
                "auth_token": update_data.twilio_config.auth_token,
                "whatsapp_from": update_data.twilio_config.whatsapp_from,
            }
        
        settings = await self.service.update_settings(
            user_id=self.current_user.id,
            email_enabled=update_data.email_enabled,
            whatsapp_enabled=update_data.whatsapp_enabled,
            whatsapp_number=update_data.whatsapp_number,
            threshold_score=update_data.threshold_score,
            smtp_config=smtp_config,
            twilio_config=twilio_config,
        )
        
        await self.session.commit()
        
        logger.info(f"Updated notification settings for user: {self.current_user.id}")
        
        return self._build_settings_response(settings)
    
    async def send_test_notification(
        self,
        channel: str,
    ) -> NotificationResultResponse:
        """Send a test notification.
        
        Args:
            channel: Channel to test ('email' or 'whatsapp').
        
        Returns:
            NotificationResultResponse with result.
        
        Raises:
            HTTPException: If channel is invalid.
        """
        if channel not in ("email", "whatsapp"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid channel: {channel}. Use 'email' or 'whatsapp'.",
            )
        
        result = await self.service.send_test_notification(
            user_id=self.current_user.id,
            channel=channel,
            user_email=self.current_user.email,
        )
        
        return NotificationResultResponse(
            success=result["success"],
            channel=channel,
            message=result.get("message", ""),
            error=result.get("error") if not result["success"] else None,
        )
    
    async def get_service_status(self) -> dict:
        """Get notification service configuration status.
        
        Returns status for both BYOK and server configurations.
        
        Returns:
            Dict with service availability.
        """
        return await self.service.get_service_status(self.current_user.id)
    
    async def clear_smtp_config(self) -> dict:
        """Clear user's SMTP configuration.
        
        Returns:
            Dict with success status.
        """
        return await self.service.clear_smtp_config(self.current_user.id)
    
    async def clear_twilio_config(self) -> dict:
        """Clear user's Twilio configuration.
        
        Returns:
            Dict with success status.
        """
        return await self.service.clear_twilio_config(self.current_user.id)
