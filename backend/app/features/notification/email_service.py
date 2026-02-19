"""Email notification service using SMTP.

This module provides async email sending functionality using aiosmtplib.
Uses BYOK (Bring Your Own Keys) - users must provide their own SMTP credentials.

Classes:
    EmailService: Service for sending email notifications.

Example:
    # Using user-provided credentials (BYOK)
    service = EmailService(
        host="smtp.gmail.com",
        port=587,
        username="user@gmail.com",
        password="app-password",
        from_email="user@gmail.com"
    )
    await service.send_cv_notification(
        to_email="recipient@example.com",
        cv_data=cv_notification_data
    )
"""

import logging
import ssl
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

# Try to import certifi for proper certificate handling on macOS
try:
    import certifi
    CERTIFI_AVAILABLE = True
except ImportError:
    CERTIFI_AVAILABLE = False

from .notification_schemas import CVNotificationData

logger = logging.getLogger(__name__)


@dataclass
class EmailResult:
    """Result of email send operation.
    
    Attributes:
        success: Whether email was sent successfully.
        message_id: SMTP message ID if successful.
        error: Error message if failed.
    """
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class SmtpCredentials:
    """SMTP credentials for email service.
    
    Attributes:
        host: SMTP server hostname.
        port: SMTP server port.
        username: SMTP authentication username.
        password: SMTP authentication password.
        from_email: Sender email address.
        from_name: Sender display name.
        use_tls: Whether to use STARTTLS.
    """
    host: str
    port: int
    username: str
    password: str
    from_email: str
    from_name: str = "CV Screening Agent"
    use_tls: bool = True


class EmailService:
    """Service for sending email notifications.
    
    Uses aiosmtplib for async SMTP communication.
    Supports TLS and configurable SMTP settings.
    
    Can be initialized with:
    - No arguments: Uses server-level configuration from environment
    - SmtpCredentials: Uses user-provided credentials (BYOK)
    - Individual parameters: Uses provided values
    
    Attributes:
        host: SMTP server hostname.
        port: SMTP server port.
        username: SMTP authentication username.
        password: SMTP authentication password.
        from_email: Sender email address.
        from_name: Sender display name.
        use_tls: Whether to use STARTTLS.
    
    Example:
        >>> # Server config
        >>> service = EmailService()
        >>> 
        >>> # BYOK with credentials object
        >>> creds = SmtpCredentials(host="smtp.gmail.com", ...)
        >>> service = EmailService(credentials=creds)
        >>> 
        >>> # BYOK with individual params
        >>> service = EmailService(
        ...     host="smtp.gmail.com",
        ...     username="user@gmail.com",
        ...     password="secret"
        ... )
    """
    
    def __init__(
        self,
        credentials: Optional[SmtpCredentials] = None,
        *,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        use_tls: Optional[bool] = None,
    ) -> None:
        """Initialize email service.
        
        BYOK Only - users must provide their own SMTP credentials.
        No server-level fallback.
        """
        if credentials:
            self.host = credentials.host
            self.port = credentials.port
            self.username = credentials.username
            self.password = credentials.password
            self.from_email = credentials.from_email
            self.from_name = credentials.from_name
            self.use_tls = credentials.use_tls
        else:
            # Individual parameters (BYOK) or empty (not configured)
            self.host = host
            self.port = port or 587
            self.username = username
            self.password = password
            self.from_email = from_email
            self.from_name = from_name or "CV Screening Agent"
            self.use_tls = use_tls if use_tls is not None else True
    
    @classmethod
    def from_user_config(cls, config: dict) -> "EmailService":
        """Create EmailService from user configuration dict.
        
        Args:
            config: Dict with SMTP configuration.
        
        Returns:
            EmailService instance.
        """
        return cls(
            host=config.get("host"),
            port=config.get("port"),
            username=config.get("username"),
            password=config.get("password"),
            from_email=config.get("from_email"),
            from_name=config.get("from_name"),
            use_tls=config.get("use_tls", True),
        )
    
    @property
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(
            self.host and
            self.username and
            self.password and
            self.from_email
        )
    
    def _create_cv_notification_html(self, cv_data: CVNotificationData) -> str:
        """Create HTML email body for CV notification.
        
        Args:
            cv_data: CV notification data.
        
        Returns:
            HTML string for email body.
        """
        status_color = "#22c55e" if cv_data.passed else "#ef4444"
        status_text = "PASSED" if cv_data.passed else "DID NOT PASS"
        candidate = cv_data.candidate_name or "Unknown Candidate"
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9fafb;">
    <div style="background-color: white; border-radius: 12px; padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <h1 style="color: #111827; font-size: 24px; margin-bottom: 8px;">
            🎯 High-Scoring CV Detected
        </h1>
        <p style="color: #6b7280; margin-bottom: 24px;">
            A new CV has been evaluated and meets your notification threshold.
        </p>
        
        <div style="background-color: #f3f4f6; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
            <h2 style="color: #111827; font-size: 18px; margin: 0 0 12px 0;">
                {candidate}
            </h2>
            <p style="color: #6b7280; font-size: 14px; margin: 0 0 8px 0;">
                📄 {cv_data.filename}
            </p>
            <div style="display: flex; align-items: center; gap: 12px; margin-top: 16px;">
                <span style="font-size: 32px; font-weight: bold; color: #111827;">
                    {cv_data.score}%
                </span>
                <span style="background-color: {status_color}; color: white; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 600;">
                    {status_text}
                </span>
            </div>
        </div>
        
        <div style="margin-bottom: 24px;">
            <h3 style="color: #111827; font-size: 14px; font-weight: 600; margin-bottom: 8px;">
                Summary
            </h3>
            <p style="color: #4b5563; font-size: 14px; line-height: 1.6; margin: 0;">
                {cv_data.summary}
            </p>
        </div>
        
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">
        
        <p style="color: #9ca3af; font-size: 12px; text-align: center; margin: 0;">
            Sent by CV Screening Agent • 
            <a href="#" style="color: #6366f1;">Manage notification settings</a>
        </p>
    </div>
</body>
</html>
"""
    
    def _create_cv_notification_text(self, cv_data: CVNotificationData) -> str:
        """Create plain text email body for CV notification.
        
        Args:
            cv_data: CV notification data.
        
        Returns:
            Plain text string for email body.
        """
        status_text = "PASSED" if cv_data.passed else "DID NOT PASS"
        candidate = cv_data.candidate_name or "Unknown Candidate"
        
        return f"""
🎯 High-Scoring CV Detected

A new CV has been evaluated and meets your notification threshold.

Candidate: {candidate}
File: {cv_data.filename}
Score: {cv_data.score}%
Status: {status_text}

Summary:
{cv_data.summary}

---
Sent by CV Screening Agent
"""
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> EmailResult:
        """Send an email.
        
        Args:
            to_email: Recipient email address.
            subject: Email subject.
            html_body: HTML email body.
            text_body: Plain text fallback (optional).
        
        Returns:
            EmailResult with success status.
        """
        if not self.is_configured:
            logger.warning("Email service not configured")
            return EmailResult(
                success=False,
                error="Email service not configured. Set SMTP_* environment variables."
            )
        
        try:
            import aiosmtplib
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            
            # Add text and HTML parts
            if text_body:
                msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            
            # Send email
            logger.info(f"Sending email to {to_email}: {subject}")
            
            # Create SSL context for STARTTLS
            # Use certifi for proper certificate handling on macOS
            tls_context = None
            if self.use_tls:
                tls_context = ssl.create_default_context()
                if CERTIFI_AVAILABLE:
                    tls_context.load_verify_locations(certifi.where())
            
            async with aiosmtplib.SMTP(
                hostname=self.host,
                port=self.port,
                use_tls=False,
                start_tls=self.use_tls,
                tls_context=tls_context,
            ) as smtp:
                await smtp.login(self.username, self.password)
                result = await smtp.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return EmailResult(success=True, message_id=str(result))
            
        except ImportError:
            logger.error("aiosmtplib not installed")
            return EmailResult(
                success=False,
                error="aiosmtplib not installed. Run: pip install aiosmtplib"
            )
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return EmailResult(success=False, error=str(e))
    
    async def send_cv_notification(
        self,
        to_email: str,
        cv_data: CVNotificationData,
    ) -> EmailResult:
        """Send CV notification email.
        
        Args:
            to_email: Recipient email address.
            cv_data: CV notification data.
        
        Returns:
            EmailResult with success status.
        """
        candidate = cv_data.candidate_name or "a candidate"
        subject = f"🎯 High-Scoring CV: {candidate} scored {cv_data.score}%"
        
        html_body = self._create_cv_notification_html(cv_data)
        text_body = self._create_cv_notification_text(cv_data)
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )
    
    async def send_test_email(self, to_email: str) -> EmailResult:
        """Send a test email to verify configuration.
        
        Args:
            to_email: Recipient email address.
        
        Returns:
            EmailResult with success status.
        """
        subject = "🧪 CV Screening Agent - Test Email"
        html_body = """
<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: white; border-radius: 12px; padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <h1 style="color: #111827; font-size: 24px;">✅ Email Configuration Working!</h1>
        <p style="color: #6b7280;">
            This is a test email from CV Screening Agent.
            If you received this, your email notifications are properly configured.
        </p>
    </div>
</body>
</html>
"""
        text_body = "✅ Email Configuration Working!\n\nThis is a test email from CV Screening Agent."
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )
