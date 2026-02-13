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
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class NotificationSettings(Base, TimestampMixin):
    """User notification preferences.
    
    Stores configuration for email and WhatsApp alerts when
    high-scoring candidates are detected.
    
    Attributes:
        id: Unique settings identifier (UUID).
        user_id: Foreign key to users table.
        email_enabled: Whether to send email notifications.
        whatsapp_enabled: Whether to send WhatsApp notifications.
        whatsapp_number: Phone number for WhatsApp (with country code).
        threshold_score: Minimum score to trigger notification (0-100).
        
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
