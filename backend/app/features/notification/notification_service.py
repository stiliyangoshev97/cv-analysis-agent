"""Notification service for orchestrating alerts.

This module provides the main service for sending notifications
based on user preferences and CV evaluation results.

Supports BYOK (Bring Your Own Keys) for SMTP and Twilio credentials,
allowing users to configure their own notification services.

Classes:
    NotificationService: Orchestration service for notifications.

Example:
    service = NotificationService(session)
    await service.dispatch_cv_notification(
        user_id=user_id,
        cv_data=cv_notification_data
    )
"""

import logging
import uuid
from dataclasses import dataclass
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.db.models.notification import NotificationSettings
from .notification_repository import NotificationRepository
from .notification_schemas import CVNotificationData
from .email_service import EmailService, EmailResult
from .whatsapp_service import WhatsAppService, WhatsAppResult

logger = logging.getLogger(__name__)


@dataclass
class NotificationDispatchResult:
    """Result of notification dispatch operation.
    
    Attributes:
        should_notify: Whether notification was triggered.
        score: CV score.
        threshold: User's threshold setting.
        email_sent: Whether email was sent.
        email_result: Email send result if attempted.
        whatsapp_sent: Whether WhatsApp was sent.
        whatsapp_result: WhatsApp send result if attempted.
        channels_attempted: List of channels that were attempted.
        errors: List of error messages.
    """
    should_notify: bool
    score: int
    threshold: int
    email_sent: bool = False
    email_result: Optional[EmailResult] = None
    whatsapp_sent: bool = False
    whatsapp_result: Optional[WhatsAppResult] = None
    channels_attempted: List[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.channels_attempted is None:
            self.channels_attempted = []
        if self.errors is None:
            self.errors = []
    
    @property
    def success(self) -> bool:
        """Check if at least one notification was sent successfully."""
        return self.email_sent or self.whatsapp_sent
    
    @property
    def partial_success(self) -> bool:
        """Check if some but not all notifications succeeded."""
        attempted = len(self.channels_attempted)
        succeeded = sum([self.email_sent, self.whatsapp_sent])
        return 0 < succeeded < attempted


class NotificationService:
    """Orchestration service for notifications.
    
    Coordinates email and WhatsApp notifications based on user
    preferences and CV evaluation results.
    
    Uses BYOK (Bring Your Own Keys) - users must provide their own
    SMTP/Twilio credentials via the Settings UI.
    
    Attributes:
        session: AsyncSession for database operations.
        repo: NotificationRepository instance.
    
    Example:
        >>> service = NotificationService(session)
        >>> result = await service.dispatch_cv_notification(
        ...     user_id=user_id,
        ...     cv_data=cv_data
        ... )
        >>> if result.success:
        ...     print("Notifications sent!")
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with database session.
        
        Args:
            session: SQLAlchemy AsyncSession.
        """
        self.session = session
        self.repo = NotificationRepository(session)
    
    def _get_email_service(
        self,
        settings: NotificationSettings,
    ) -> EmailService:
        """Get EmailService using user's BYOK credentials.
        
        Args:
            settings: User's notification settings.
        
        Returns:
            EmailService instance (may be unconfigured if no BYOK credentials).
        """
        # Check if user has BYOK SMTP config
        if settings.has_smtp_config:
            smtp_config = self.repo.get_decrypted_smtp_config(settings)
            if smtp_config:
                logger.debug("Using user's SMTP configuration (BYOK)")
                return EmailService.from_user_config(smtp_config)
        
        # Return unconfigured service
        logger.debug("No SMTP configuration found")
        return EmailService()
    
    def _get_whatsapp_service(
        self,
        settings: NotificationSettings,
    ) -> WhatsAppService:
        """Get WhatsAppService using user's BYOK credentials.
        
        Args:
            settings: User's notification settings.
        
        Returns:
            WhatsAppService instance (may be unconfigured if no BYOK credentials).
        """
        # Check if user has BYOK Twilio config
        if settings.has_twilio_config:
            twilio_config = self.repo.get_decrypted_twilio_config(settings)
            if twilio_config:
                logger.debug("Using user's Twilio configuration (BYOK)")
                return WhatsAppService.from_user_config(twilio_config)
        
        # Return unconfigured service
        logger.debug("No Twilio configuration found")
        return WhatsAppService()
    
    async def get_settings(
        self,
        user_id: uuid.UUID,
    ):
        """Get notification settings for a user.
        
        Args:
            user_id: UUID of the user.
        
        Returns:
            NotificationSettings instance.
        """
        return await self.repo.get_or_create(user_id)
    
    async def update_settings(
        self,
        user_id: uuid.UUID,
        email_enabled: Optional[bool] = None,
        whatsapp_enabled: Optional[bool] = None,
        whatsapp_number: Optional[str] = None,
        threshold_score: Optional[int] = None,
        smtp_config: Optional[dict] = None,
        twilio_config: Optional[dict] = None,
    ):
        """Update notification settings for a user.
        
        Args:
            user_id: UUID of the user.
            email_enabled: Enable/disable email.
            whatsapp_enabled: Enable/disable WhatsApp.
            whatsapp_number: WhatsApp phone number.
            threshold_score: Notification threshold.
            smtp_config: SMTP configuration (BYOK).
            twilio_config: Twilio configuration (BYOK).
        
        Returns:
            Updated NotificationSettings.
        """
        settings = await self.repo.get_or_create(user_id)
        
        if email_enabled is not None:
            settings.email_enabled = email_enabled
        if whatsapp_enabled is not None:
            settings.whatsapp_enabled = whatsapp_enabled
        if whatsapp_number is not None:
            settings.whatsapp_number = whatsapp_number
        if threshold_score is not None:
            settings.threshold_score = threshold_score
        
        # Update SMTP config (BYOK)
        if smtp_config is not None:
            await self.repo.update_smtp_config(
                settings,
                host=smtp_config.get("host"),
                port=smtp_config.get("port"),
                username=smtp_config.get("username"),
                password=smtp_config.get("password"),
                from_email=smtp_config.get("from_email"),
                from_name=smtp_config.get("from_name"),
                use_tls=smtp_config.get("use_tls"),
            )
        
        # Update Twilio config (BYOK)
        if twilio_config is not None:
            await self.repo.update_twilio_config(
                settings,
                account_sid=twilio_config.get("account_sid"),
                auth_token=twilio_config.get("auth_token"),
                whatsapp_from=twilio_config.get("whatsapp_from"),
            )
        
        return await self.repo.update(settings)
    
    async def check_threshold(
        self,
        user_id: uuid.UUID,
        score: int,
    ) -> tuple[bool, int]:
        """Check if score meets user's notification threshold.
        
        Args:
            user_id: UUID of the user.
            score: CV score (0-100).
        
        Returns:
            Tuple of (should_notify, threshold).
        """
        settings = await self.repo.get_or_create(user_id)
        should_notify = score >= settings.threshold_score
        return should_notify, settings.threshold_score
    
    async def dispatch_cv_notification(
        self,
        user_id: uuid.UUID,
        cv_data: CVNotificationData,
        user_email: Optional[str] = None,
    ) -> NotificationDispatchResult:
        """Dispatch CV notification to enabled channels.
        
        Checks threshold and sends notifications to all enabled
        channels (email and/or WhatsApp). Uses BYOK credentials
        configured by the user in Settings > Notifications.
        
        Args:
            user_id: UUID of the user.
            cv_data: CV notification data.
            user_email: User's email (optional, will be fetched if not provided).
        
        Returns:
            NotificationDispatchResult with detailed status.
        """
        # Get settings
        settings = await self.repo.get_or_create(user_id)
        
        # Check threshold
        should_notify = cv_data.score >= settings.threshold_score
        
        result = NotificationDispatchResult(
            should_notify=should_notify,
            score=cv_data.score,
            threshold=settings.threshold_score,
        )
        
        if not should_notify:
            logger.debug(
                f"Score {cv_data.score} below threshold {settings.threshold_score}, "
                f"skipping notification"
            )
            return result
        
        logger.info(
            f"Dispatching notification for CV {cv_data.cv_id}: "
            f"score={cv_data.score}, threshold={settings.threshold_score}"
        )
        
        # Get user email if needed
        if settings.email_enabled and not user_email:
            from sqlalchemy import select
            user_result = await self.session.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                user_email = user.email
        
        # Send email notification
        if settings.email_enabled:
            result.channels_attempted.append("email")
            email_service = self._get_email_service(settings)
            
            if not user_email:
                result.errors.append("User email not found")
            elif not email_service.is_configured:
                result.errors.append("Email service not configured (configure SMTP in Settings)")
            else:
                email_result = await email_service.send_cv_notification(
                    to_email=user_email,
                    cv_data=cv_data,
                )
                result.email_result = email_result
                result.email_sent = email_result.success
                if not email_result.success:
                    result.errors.append(f"Email: {email_result.error}")
        
        # Send WhatsApp notification
        if settings.whatsapp_enabled:
            result.channels_attempted.append("whatsapp")
            whatsapp_service = self._get_whatsapp_service(settings)
            
            if not settings.whatsapp_number:
                result.errors.append("WhatsApp number not configured")
            elif not whatsapp_service.is_configured:
                result.errors.append("WhatsApp service not configured (configure Twilio in Settings)")
            else:
                whatsapp_result = await whatsapp_service.send_cv_notification(
                    to_number=settings.whatsapp_number,
                    cv_data=cv_data,
                )
                result.whatsapp_result = whatsapp_result
                result.whatsapp_sent = whatsapp_result.success
                if not whatsapp_result.success:
                    result.errors.append(f"WhatsApp: {whatsapp_result.error}")
        
        # Log result
        if result.success:
            logger.info(
                f"Notification sent for CV {cv_data.cv_id}: "
                f"email={result.email_sent}, whatsapp={result.whatsapp_sent}"
            )
        elif result.channels_attempted:
            logger.warning(
                f"Notification failed for CV {cv_data.cv_id}: {result.errors}"
            )
        
        return result
    
    async def send_test_notification(
        self,
        user_id: uuid.UUID,
        channel: str,
        user_email: Optional[str] = None,
    ) -> dict:
        """Send a test notification.
        
        Uses BYOK credentials configured in Settings > Notifications.
        
        Args:
            user_id: UUID of the user.
            channel: Channel to test ('email' or 'whatsapp').
            user_email: User's email (for email channel).
        
        Returns:
            Dict with success status and message.
        """
        settings = await self.repo.get_or_create(user_id)
        
        if channel == "email":
            if not user_email:
                # Fetch from database
                from sqlalchemy import select
                user_result = await self.session.execute(
                    select(User).where(User.id == user_id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    user_email = user.email
            
            if not user_email:
                return {"success": False, "error": "User email not found"}
            
            email_service = self._get_email_service(settings)
            if not email_service.is_configured:
                return {"success": False, "error": "Email service not configured. Configure SMTP credentials in Settings > Notifications."}
            
            result = await email_service.send_test_email(user_email)
            return {
                "success": result.success,
                "message": "Test email sent" if result.success else result.error,
            }
        
        elif channel == "whatsapp":
            if not settings.whatsapp_number:
                return {"success": False, "error": "WhatsApp number not configured"}
            
            whatsapp_service = self._get_whatsapp_service(settings)
            if not whatsapp_service.is_configured:
                return {"success": False, "error": "WhatsApp service not configured. Configure Twilio credentials in Settings > Notifications."}
            
            result = await whatsapp_service.send_test_message(
                settings.whatsapp_number
            )
            return {
                "success": result.success,
                "message": "Test WhatsApp sent" if result.success else result.error,
            }
        
        else:
            return {"success": False, "error": f"Unknown channel: {channel}"}
    
    async def get_service_status(
        self,
        user_id: uuid.UUID,
    ) -> dict:
        """Get notification service configuration status.
        
        Returns whether email/WhatsApp are configured via BYOK.
        
        Args:
            user_id: UUID of the user.
        
        Returns:
            Dict with configuration status.
        """
        settings = await self.repo.get_or_create(user_id)
        
        # Check if user has BYOK config
        has_user_smtp = settings.has_smtp_config
        has_user_twilio = settings.has_twilio_config
        
        return {
            "email_configured": has_user_smtp,
            "whatsapp_configured": has_user_twilio,
            "email_source": "user" if has_user_smtp else "none",
            "whatsapp_source": "user" if has_user_twilio else "none",
            "email_service": "SMTP (BYOK)" if has_user_smtp else "Not Configured",
            "whatsapp_service": "Twilio (BYOK)" if has_user_twilio else "Not Configured",
        }
    
    async def clear_smtp_config(self, user_id: uuid.UUID) -> dict:
        """Clear user's SMTP configuration.
        
        Args:
            user_id: UUID of the user.
        
        Returns:
            Dict with success status.
        """
        settings = await self.repo.get_or_create(user_id)
        await self.repo.clear_smtp_config(settings)
        return {"success": True, "message": "SMTP configuration cleared"}
    
    async def clear_twilio_config(self, user_id: uuid.UUID) -> dict:
        """Clear user's Twilio configuration.
        
        Args:
            user_id: UUID of the user.
        
        Returns:
            Dict with success status.
        """
        settings = await self.repo.get_or_create(user_id)
        await self.repo.clear_twilio_config(settings)
        return {"success": True, "message": "Twilio configuration cleared"}
