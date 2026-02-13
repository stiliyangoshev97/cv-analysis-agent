"""Pydantic schemas for notification feature.

This module defines request/response models for notification endpoints.

Classes:
    NotificationSettingsResponse: Current notification settings.
    NotificationSettingsUpdate: Update notification preferences.
    SendTestNotificationRequest: Request to send a test notification.
    NotificationResultResponse: Result of notification dispatch.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class NotificationSettingsResponse(BaseModel):
    """Response schema for notification settings.
    
    Attributes:
        email_enabled: Whether email notifications are enabled.
        whatsapp_enabled: Whether WhatsApp notifications are enabled.
        whatsapp_number: WhatsApp number (masked for security).
        threshold_score: Score threshold for notifications.
    """
    email_enabled: bool
    whatsapp_enabled: bool
    whatsapp_number: Optional[str] = None
    threshold_score: int = Field(ge=0, le=100)
    
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
    """
    email_enabled: Optional[bool] = None
    whatsapp_enabled: Optional[bool] = None
    whatsapp_number: Optional[str] = None
    threshold_score: Optional[int] = Field(default=None, ge=0, le=100)
    
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
