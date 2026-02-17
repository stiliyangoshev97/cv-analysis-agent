"""Pydantic schemas for notification feature.

This module defines request/response models for notification endpoints.

Classes:
    NotificationSettingsResponse: Current notification settings.
    NotificationSettingsUpdate: Update notification preferences.
    SendTestNotificationRequest: Request to send a test notification.
    NotificationResultResponse: Result of notification dispatch.
    SmtpConfigUpdate: SMTP configuration for BYOK.
    TwilioConfigUpdate: Twilio configuration for BYOK.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


# =============================================================================
# SMTP Configuration (BYOK)
# =============================================================================

class SmtpConfigUpdate(BaseModel):
    """SMTP configuration for email notifications (BYOK).
    
    Allows users to provide their own SMTP credentials.
    
    Attributes:
        host: SMTP server hostname (e.g., smtp.gmail.com).
        port: SMTP server port (default: 587 for TLS).
        username: SMTP authentication username.
        password: SMTP authentication password.
        from_email: Sender email address.
        from_name: Sender display name.
        use_tls: Whether to use STARTTLS.
    """
    host: Optional[str] = Field(default=None, max_length=255)
    port: Optional[int] = Field(default=587, ge=1, le=65535)
    username: Optional[str] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, max_length=500)
    from_email: Optional[str] = Field(default=None, max_length=255)
    from_name: Optional[str] = Field(default="CV Screening Agent", max_length=100)
    use_tls: bool = True
    
    @field_validator("from_email")
    @classmethod
    def validate_from_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format."""
        if v is None or v == "":
            return None
        # Basic email validation
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid email address format")
        return v


class SmtpConfigResponse(BaseModel):
    """SMTP configuration response (credentials masked).
    
    Attributes:
        configured: Whether SMTP is configured.
        host: SMTP server hostname.
        port: SMTP server port.
        from_email: Sender email (masked).
        from_name: Sender display name.
        use_tls: Whether TLS is enabled.
    """
    configured: bool = False
    host: Optional[str] = None
    port: Optional[int] = None
    from_email_hint: Optional[str] = None  # Masked email
    from_name: Optional[str] = None
    use_tls: bool = True


# =============================================================================
# Twilio Configuration (BYOK)
# =============================================================================

class TwilioConfigUpdate(BaseModel):
    """Twilio configuration for WhatsApp notifications (BYOK).
    
    Allows users to provide their own Twilio credentials.
    
    Attributes:
        account_sid: Twilio account SID.
        auth_token: Twilio auth token.
        whatsapp_from: WhatsApp sender number (e.g., +14155238886).
    """
    account_sid: Optional[str] = Field(default=None, max_length=100)
    auth_token: Optional[str] = Field(default=None, max_length=100)
    whatsapp_from: Optional[str] = Field(default=None, max_length=20)
    
    @field_validator("whatsapp_from")
    @classmethod
    def validate_whatsapp_from(cls, v: Optional[str]) -> Optional[str]:
        """Validate WhatsApp number format."""
        if v is None or v == "":
            return None
        # Allow numbers like +1234567890
        cleaned = re.sub(r"[\s\-()]", "", v)
        if not re.match(r"^\+\d{10,15}$", cleaned):
            raise ValueError(
                "Invalid phone number. Use international format: +1234567890"
            )
        return cleaned


class TwilioConfigResponse(BaseModel):
    """Twilio configuration response (credentials masked).
    
    Attributes:
        configured: Whether Twilio is configured.
        account_sid_hint: Last 4 characters of account SID.
        whatsapp_from_hint: WhatsApp sender number (masked).
    """
    configured: bool = False
    account_sid_hint: Optional[str] = None
    whatsapp_from_hint: Optional[str] = None


# =============================================================================
# Notification Settings
# =============================================================================

class NotificationSettingsResponse(BaseModel):
    """Response schema for notification settings.
    
    Attributes:
        email_enabled: Whether email notifications are enabled.
        whatsapp_enabled: Whether WhatsApp notifications are enabled.
        whatsapp_number: WhatsApp number (masked for security).
        threshold_score: Score threshold for notifications.
        smtp_config: SMTP configuration status.
        twilio_config: Twilio configuration status.
    """
    email_enabled: bool
    whatsapp_enabled: bool
    whatsapp_number: Optional[str] = None
    threshold_score: int = Field(ge=0, le=100)
    smtp_config: SmtpConfigResponse = Field(default_factory=SmtpConfigResponse)
    twilio_config: TwilioConfigResponse = Field(default_factory=TwilioConfigResponse)
    
    class Config:
        from_attributes = True


class NotificationSettingsUpdate(BaseModel):
    """Request schema for updating notification settings.
    
    All fields are optional - only provided fields will be updated.
    
    Attributes:
        email_enabled: Enable/disable email notifications.
        whatsapp_enabled: Enable/disable WhatsApp notifications.
        whatsapp_number: WhatsApp number with country code.
        threshold_score: Score threshold (0-100).
        smtp_config: SMTP configuration (BYOK).
        twilio_config: Twilio configuration (BYOK).
    """
    email_enabled: Optional[bool] = None
    whatsapp_enabled: Optional[bool] = None
    whatsapp_number: Optional[str] = None
    threshold_score: Optional[int] = Field(default=None, ge=0, le=100)
    smtp_config: Optional[SmtpConfigUpdate] = None
    twilio_config: Optional[TwilioConfigUpdate] = None
    
    @field_validator("whatsapp_number")
    @classmethod
    def validate_whatsapp_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate WhatsApp number format."""
        if v is None or v == "":
            return None
        # Allow numbers like +1234567890 or +44 123 456 7890
        cleaned = re.sub(r"[\s\-()]", "", v)
        if not re.match(r"^\+\d{10,15}$", cleaned):
            raise ValueError(
                "Invalid phone number. Use international format: +1234567890"
            )
        return cleaned


class SendTestNotificationRequest(BaseModel):
    """Request to send a test notification.
    
    Attributes:
        channel: Notification channel ('email' or 'whatsapp').
    """
    channel: str = Field(pattern="^(email|whatsapp)$")


class NotificationResultResponse(BaseModel):
    """Response from notification dispatch.
    
    Attributes:
        success: Whether the notification was sent.
        channel: Which channel was used.
        message: Status message.
        error: Error message if failed.
    """
    success: bool
    channel: str
    message: str
    error: Optional[str] = None


class CVNotificationData(BaseModel):
    """Data for CV score notification.
    
    Used internally to pass CV data to notification services.
    
    Attributes:
        cv_id: UUID of the CV.
        filename: Original filename.
        candidate_name: Extracted candidate name.
        score: Evaluation score (0-100).
        passed: Whether the CV passed.
        summary: Brief evaluation summary.
    """
    cv_id: str
    filename: str
    candidate_name: Optional[str] = None
    score: int
    passed: bool
    summary: str


# =============================================================================
# Notification History
# =============================================================================

class NotificationHistoryItem(BaseModel):
    """Single notification history entry.
    
    Attributes:
        id: Unique notification identifier.
        cv_id: Related CV identifier (if available).
        type: Notification channel (email/whatsapp).
        status: Delivery status (pending/sent/failed).
        recipient: Email or phone number (masked).
        subject: Email subject (if email).
        message: Notification content preview.
        error_message: Error details if failed.
        cv_score: Score that triggered notification.
        candidate_name: Name of candidate.
        sent_at: When notification was sent.
        created_at: When notification was created.
    """
    id: str
    cv_id: Optional[str] = None
    type: str  # 'email' or 'whatsapp'
    status: str  # 'pending', 'sent', 'failed'
    recipient: str  # Masked for security
    subject: Optional[str] = None
    message: str
    error_message: Optional[str] = None
    cv_score: Optional[int] = None
    candidate_name: Optional[str] = None
    sent_at: Optional[str] = None  # ISO format
    created_at: str  # ISO format
    
    class Config:
        from_attributes = True


class NotificationHistoryListResponse(BaseModel):
    """Paginated list of notification history.
    
    Attributes:
        items: List of notification entries.
        total: Total number of notifications.
        limit: Page size.
        offset: Current offset.
        has_more: Whether more pages exist.
    """
    items: list[NotificationHistoryItem]
    total: int
    limit: int
    offset: int
    has_more: bool


class NotificationHistoryStatsResponse(BaseModel):
    """Statistics about notification history.
    
    Attributes:
        total: Total notifications sent.
        sent: Successfully sent count.
        failed: Failed notification count.
        pending: Pending notification count.
        by_type: Count by notification type.
    """
    total: int
    sent: int
    failed: int
    pending: int
    by_type: dict[str, int]


class ResendNotificationResponse(BaseModel):
    """Response from resending a notification.
    
    Attributes:
        success: Whether resend was successful.
        message: Status message.
        new_status: Updated status of the notification.
    """
    success: bool
    message: str
    new_status: str
