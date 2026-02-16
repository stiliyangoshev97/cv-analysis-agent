"""Notification Settings model for user alert preferences.

This module defines the NotificationSettings model for storing
user preferences for email and WhatsApp notifications.

Classes:
    NotificationSettings: SQLAlchemy model for notification preferences.

Example:
    Configuring notifications::
    
        settings = NotificationSettings(
            user_id=user.id,
            email_enabled=True,
            whatsapp_enabled=True,
            whatsapp_number="+1234567890",
            threshold_score=80
        )
        session.add(settings)

Note:
    SMTP and Twilio credentials are encrypted using AES-256 (Fernet)
    before storage. Users can provide their own credentials (BYOK)
    instead of relying on server-level configuration.
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Integer, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class NotificationSettings(Base, TimestampMixin):
    """User notification preferences.
    
    Stores configuration for email and WhatsApp alerts when
    high-scoring candidates are detected.
    
    Supports BYOK (Bring Your Own Keys) for SMTP and Twilio credentials,
    allowing users to configure their own notification services.
    
    Attributes:
        id: Unique settings identifier (UUID).
        user_id: Foreign key to users table.
        email_enabled: Whether to send email notifications.
        whatsapp_enabled: Whether to send WhatsApp notifications.
        whatsapp_number: Phone number for WhatsApp (with country code).
        threshold_score: Minimum score to trigger notification (0-100).
        
        # SMTP Configuration (BYOK)
        smtp_host: SMTP server hostname (encrypted).
        smtp_port: SMTP server port.
        smtp_username: SMTP authentication username (encrypted).
        smtp_password: SMTP authentication password (encrypted).
        smtp_from_email: Sender email address (encrypted).
        smtp_from_name: Sender display name.
        smtp_use_tls: Whether to use STARTTLS.
        
        # Twilio Configuration (BYOK)
        twilio_account_sid: Twilio account SID (encrypted).
        twilio_auth_token: Twilio auth token (encrypted).
        twilio_whatsapp_from: WhatsApp sender number (encrypted).
        
    Relationships:
        user: The user who owns these settings.
    
    Example:
        >>> settings = NotificationSettings(
        ...     user_id=user.id,
        ...     email_enabled=True,
        ...     threshold_score=75
        ... )
    
    Note:
        WhatsApp number should include country code (e.g., "+1234567890").
        All sensitive credentials are stored encrypted.
    """
    
    __tablename__ = "notification_settings"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Foreign key to user (one-to-one)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    
    # Email notifications
    email_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    
    # WhatsApp notifications
    whatsapp_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    whatsapp_number: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    
    # Notification threshold (score >= threshold triggers notification)
    threshold_score: Mapped[int] = mapped_column(
        Integer,
        default=80,
        nullable=False,
    )
    
    # =========================================================================
    # SMTP Configuration (BYOK - Bring Your Own Keys)
    # All sensitive fields are encrypted with AES-256
    # =========================================================================
    
    smtp_host: Mapped[Optional[str]] = mapped_column(
        Text,  # Encrypted values can be long
        nullable=True,
        comment="SMTP server hostname (encrypted)",
    )
    
    smtp_port: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=587,
        comment="SMTP server port",
    )
    
    smtp_username: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="SMTP username (encrypted)",
    )
    
    smtp_password: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="SMTP password (encrypted)",
    )
    
    smtp_from_email: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Sender email address (encrypted)",
    )
    
    smtp_from_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default="CV Screening Agent",
        comment="Sender display name",
    )
    
    smtp_use_tls: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether to use STARTTLS",
    )
    
    # =========================================================================
    # Twilio Configuration (BYOK - Bring Your Own Keys)
    # All sensitive fields are encrypted with AES-256
    # =========================================================================
    
    twilio_account_sid: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Twilio account SID (encrypted)",
    )
    
    twilio_auth_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Twilio auth token (encrypted)",
    )
    
    twilio_whatsapp_from: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="WhatsApp sender number (encrypted)",
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notification_settings",
    )
    
    def __repr__(self) -> str:
        channels = []
        if self.email_enabled:
            channels.append("email")
        if self.whatsapp_enabled:
            channels.append("whatsapp")
        return f"<NotificationSettings threshold={self.threshold_score} via {','.join(channels) or 'none'}>"
    
    @property
    def has_smtp_config(self) -> bool:
        """Check if user has configured SMTP credentials."""
        return bool(
            self.smtp_host and
            self.smtp_username and
            self.smtp_password and
            self.smtp_from_email
        )
    
    @property
    def has_twilio_config(self) -> bool:
        """Check if user has configured Twilio credentials."""
        return bool(
            self.twilio_account_sid and
            self.twilio_auth_token and
            self.twilio_whatsapp_from
        )
