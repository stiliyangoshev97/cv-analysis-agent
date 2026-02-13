"""WhatsApp notification service using Twilio.

This module provides WhatsApp messaging functionality using the Twilio API.

Classes:
    WhatsAppService: Service for sending WhatsApp notifications.

Example:
    service = WhatsAppService()
    await service.send_cv_notification(
        to_number="+1234567890",
        cv_data=cv_notification_data
    )

Note:
    Requires Twilio account with WhatsApp Business API enabled.
    Set TWILIO_* environment variables.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from app.config import get_settings
from .notification_schemas import CVNotificationData

logger = logging.getLogger(__name__)


@dataclass
class WhatsAppResult:
    """Result of WhatsApp send operation.
    
    Attributes:
        success: Whether message was sent successfully.
        message_sid: Twilio message SID if successful.
        error: Error message if failed.
    """
    success: bool
    message_sid: Optional[str] = None
    error: Optional[str] = None


class WhatsAppService:
    """Service for sending WhatsApp notifications via Twilio.
    
    Uses Twilio's WhatsApp Business API to send messages.
    Messages are sent asynchronously using a thread executor.
    
    Attributes:
        account_sid: Twilio account SID.
        auth_token: Twilio auth token.
        from_number: WhatsApp sender number (e.g., "whatsapp:+14155238886").
    
    Example:
        >>> service = WhatsAppService()
        >>> result = await service.send_cv_notification(
        ...     to_number="+1234567890",
        ...     cv_data=cv_data
        ... )
        >>> if result.success:
        ...     print(f"Message sent: {result.message_sid}")
    
    Note:
        WhatsApp Business API requires approved templates for some messages.
        For notifications, ensure your template is approved.
    """
    
    def __init__(self) -> None:
        """Initialize WhatsApp service with settings."""
        settings = get_settings()
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.from_number = settings.twilio_whatsapp_from
    
    @property
    def is_configured(self) -> bool:
        """Check if WhatsApp service is properly configured."""
        return bool(
            self.account_sid and
            self.auth_token and
            self.from_number
        )
    
    def _format_whatsapp_number(self, number: str) -> str:
        """Format phone number for WhatsApp.
        
        Args:
            number: Phone number (e.g., "+1234567890").
        
        Returns:
            WhatsApp-formatted number (e.g., "whatsapp:+1234567890").
        """
        # Remove any existing whatsapp: prefix
        clean = number.replace("whatsapp:", "").strip()
        return f"whatsapp:{clean}"
    
    def _create_cv_notification_message(self, cv_data: CVNotificationData) -> str:
        """Create WhatsApp message for CV notification.
        
        Args:
            cv_data: CV notification data.
        
        Returns:
            Formatted message string.
        """
        status_emoji = "✅" if cv_data.passed else "❌"
        status_text = "PASSED" if cv_data.passed else "DID NOT PASS"
        candidate = cv_data.candidate_name or "Unknown"
        
        return f"""🎯 *High-Scoring CV Alert*

*Candidate:* {candidate}
*File:* {cv_data.filename}
*Score:* {cv_data.score}%
*Status:* {status_emoji} {status_text}

*Summary:*
{cv_data.summary[:500]}{"..." if len(cv_data.summary) > 500 else ""}

_Sent by CV Screening Agent_"""
    
    async def send_message(
        self,
        to_number: str,
        message: str,
    ) -> WhatsAppResult:
        """Send a WhatsApp message.
        
        Args:
            to_number: Recipient phone number.
            message: Message text.
        
        Returns:
            WhatsAppResult with success status.
        """
        if not self.is_configured:
            logger.warning("WhatsApp service not configured")
            return WhatsAppResult(
                success=False,
                error="WhatsApp service not configured. Set TWILIO_* environment variables."
            )
        
        try:
            from twilio.rest import Client
            import asyncio
            
            # Format numbers
            to_whatsapp = self._format_whatsapp_number(to_number)
            from_whatsapp = self._format_whatsapp_number(self.from_number)
            
            logger.info(f"Sending WhatsApp message to {to_number}")
            
            # Twilio client is synchronous, run in executor
            def send_sync():
                client = Client(self.account_sid, self.auth_token)
                return client.messages.create(
                    body=message,
                    from_=from_whatsapp,
                    to=to_whatsapp,
                )
            
            loop = asyncio.get_event_loop()
            twilio_message = await loop.run_in_executor(None, send_sync)
            
            logger.info(f"WhatsApp message sent: {twilio_message.sid}")
            return WhatsAppResult(
                success=True,
                message_sid=twilio_message.sid,
            )
            
        except ImportError:
            logger.error("twilio not installed")
            return WhatsAppResult(
                success=False,
                error="twilio not installed. Run: pip install twilio"
            )
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            return WhatsAppResult(success=False, error=str(e))
    
    async def send_cv_notification(
        self,
        to_number: str,
        cv_data: CVNotificationData,
    ) -> WhatsAppResult:
        """Send CV notification via WhatsApp.
        
        Args:
            to_number: Recipient phone number.
            cv_data: CV notification data.
        
        Returns:
            WhatsAppResult with success status.
        """
        message = self._create_cv_notification_message(cv_data)
        return await self.send_message(to_number, message)
    
    async def send_test_message(self, to_number: str) -> WhatsAppResult:
        """Send a test WhatsApp message to verify configuration.
        
        Args:
            to_number: Recipient phone number.
        
        Returns:
            WhatsAppResult with success status.
        """
        message = """🧪 *CV Screening Agent - Test Message*

✅ WhatsApp notifications are properly configured!

If you received this message, your WhatsApp notifications are working correctly."""
        
        return await self.send_message(to_number, message)
