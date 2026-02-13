"""Controller for notification endpoints.

This module handles HTTP request/response logic for notification settings.

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
from .notification_schemas import (
    NotificationSettingsResponse,
    NotificationSettingsUpdate,
    NotificationResultResponse,
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
    
    async def get_settings(self) -> NotificationSettingsResponse:
        """Get current user's notification settings.
        
        Returns:
            NotificationSettingsResponse with current settings.
        """
        settings = await self.service.get_settings(self.current_user.id)
        
        # Mask WhatsApp number for security (show last 4 digits)
        masked_number = None
        if settings.whatsapp_number:
            masked_number = f"***{settings.whatsapp_number[-4:]}"
        
        return NotificationSettingsResponse(
            email_enabled=settings.email_enabled,
            whatsapp_enabled=settings.whatsapp_enabled,
            whatsapp_number=masked_number,
            threshold_score=settings.threshold_score,
        )
    
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
        settings = await self.service.update_settings(
            user_id=self.current_user.id,
            email_enabled=update_data.email_enabled,
            whatsapp_enabled=update_data.whatsapp_enabled,
            whatsapp_number=update_data.whatsapp_number,
            threshold_score=update_data.threshold_score,
        )
        
        await self.session.commit()
        
        logger.info(f"Updated notification settings for user: {self.current_user.id}")
        
        # Mask WhatsApp number
        masked_number = None
        if settings.whatsapp_number:
            masked_number = f"***{settings.whatsapp_number[-4:]}"
        
        return NotificationSettingsResponse(
            email_enabled=settings.email_enabled,
            whatsapp_enabled=settings.whatsapp_enabled,
            whatsapp_number=masked_number,
            threshold_score=settings.threshold_score,
        )
    
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
        
        Returns:
            Dict with service availability.
        """
        from .email_service import EmailService
        from .whatsapp_service import WhatsAppService
        
        email_service = EmailService()
        whatsapp_service = WhatsAppService()
        
        return {
            "email": {
                "configured": email_service.is_configured,
                "host": email_service.host if email_service.is_configured else None,
            },
            "whatsapp": {
                "configured": whatsapp_service.is_configured,
            },
        }
