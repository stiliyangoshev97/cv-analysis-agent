"""NotificationHistory model for tracking sent notifications.

This module defines the NotificationHistory model for storing
a history of all notifications sent to users.

Classes:
    NotificationType: Enum for notification channel types.
    NotificationStatus: Enum for notification delivery status.
    NotificationHistory: SQLAlchemy model for notification history.

Example:
    Logging a notification::
    
        history = NotificationHistory(
            user_id=user.id,
            cv_id=cv.id,
            type=NotificationType.EMAIL,
            status=NotificationStatus.SENT,
            recipient="user@example.com",
            subject="High-Scoring Candidate",
            message="Candidate John Doe scored 85%",
            cv_score=85,
            candidate_name="John Doe"
        )
        session.add(history)
"""

import uuid
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Integer, Text, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.cv import CV


class NotificationType(str, enum.Enum):
    """Type of notification channel.
    
    Attributes:
        EMAIL: Email notification via SMTP.
        WHATSAPP: WhatsApp notification via Twilio.
    """
    EMAIL = "email"
    WHATSAPP = "whatsapp"


class NotificationStatus(str, enum.Enum):
    """Status of notification delivery.
    
    Attributes:
        PENDING: Notification queued but not yet sent.
        SENT: Notification successfully delivered.
        FAILED: Notification delivery failed.
    """
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class NotificationHistory(Base, TimestampMixin):
    """History of sent notifications.
    
    Tracks all notifications sent to users, including success/failure
    status and error messages for debugging.
    
    Attributes:
        id: Unique notification identifier (UUID).
        user_id: Foreign key to users table.
        cv_id: Foreign key to cvs table (nullable).
        type: Notification channel (email/whatsapp).
        status: Delivery status (pending/sent/failed).
        recipient: Email address or phone number.
        subject: Email subject (null for WhatsApp).
        message: Notification content.
        error_message: Error details if failed.
        cv_score: Score that triggered the notification.
        candidate_name: Name of the candidate.
        sent_at: Timestamp when notification was sent.
        
    Relationships:
        user: The user who received the notification.
        cv: The CV that triggered the notification.
    
    Example:
        >>> history = NotificationHistory(
        ...     user_id=user.id,
        ...     cv_id=cv.id,
        ...     type=NotificationType.EMAIL,
        ...     status=NotificationStatus.SENT,
        ...     recipient="user@example.com",
        ...     cv_score=85,
        ...     candidate_name="John Doe"
        ... )
    """
    
    __tablename__ = "notification_history"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Foreign key to user
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Foreign key to CV (nullable - CV might be deleted)
    cv_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cvs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Notification type (email or whatsapp)
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType),
        nullable=False,
        index=True,
    )
    
    # Delivery status
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus),
        nullable=False,
        default=NotificationStatus.PENDING,
        index=True,
    )
    
    # Recipient (email address or phone number)
    recipient: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    
    # Email subject (null for WhatsApp)
    subject: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    
    # Notification message content
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    # Error message if failed
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # CV score that triggered the notification
    cv_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    
    # Candidate name for context
    candidate_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    
    # When the notification was actually sent
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notification_history",
        lazy="selectin",
    )
    
    cv: Mapped[Optional["CV"]] = relationship(
        "CV",
        back_populates="notification_history",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<NotificationHistory(id={self.id}, type={self.type.value}, "
            f"status={self.status.value}, recipient={self.recipient[:20]}...)>"
        )
