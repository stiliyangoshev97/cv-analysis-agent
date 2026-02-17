"""Repository for notification history database operations.

This module provides database operations for the NotificationHistory model.

Classes:
    NotificationHistoryRepository: CRUD operations for notification history.

Example:
    repo = NotificationHistoryRepository(session)
    history = await repo.create(
        user_id=user_id,
        cv_id=cv_id,
        type=NotificationType.EMAIL,
        recipient="user@example.com",
        message="High-scoring candidate detected"
    )
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.notification_history import (
    NotificationHistory,
    NotificationType,
    NotificationStatus,
)

logger = logging.getLogger(__name__)


class NotificationHistoryRepository:
    """Repository for notification history operations.
    
    Provides CRUD operations for tracking notification delivery.
    
    Attributes:
        session: AsyncSession for database operations.
    
    Example:
        >>> repo = NotificationHistoryRepository(session)
        >>> history = await repo.create(
        ...     user_id=user.id,
        ...     type=NotificationType.EMAIL,
        ...     recipient="user@example.com",
        ...     message="Candidate scored 85%"
        ... )
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy AsyncSession.
        """
        self.session = session
    
    async def create(
        self,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        recipient: str,
        message: str,
        cv_id: Optional[uuid.UUID] = None,
        subject: Optional[str] = None,
        cv_score: Optional[int] = None,
        candidate_name: Optional[str] = None,
        status: NotificationStatus = NotificationStatus.PENDING,
    ) -> NotificationHistory:
        """Create a new notification history entry.
        
        Args:
            user_id: UUID of the user.
            notification_type: Type of notification (email/whatsapp).
            recipient: Email or phone number.
            message: Notification content.
            cv_id: Optional UUID of the related CV.
            subject: Optional email subject.
            cv_score: Optional score that triggered notification.
            candidate_name: Optional candidate name.
            status: Initial status (default: pending).
        
        Returns:
            Created NotificationHistory instance.
        """
        history = NotificationHistory(
            user_id=user_id,
            cv_id=cv_id,
            type=notification_type,
            status=status,
            recipient=recipient,
            subject=subject,
            message=message,
            cv_score=cv_score,
            candidate_name=candidate_name,
        )
        
        self.session.add(history)
        await self.session.flush()
        await self.session.refresh(history)
        
        logger.info(
            f"Created notification history: id={history.id}, "
            f"type={notification_type.value}, recipient={recipient[:20]}..."
        )
        
        return history
    
    async def get_by_id(
        self,
        history_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[NotificationHistory]:
        """Get notification history entry by ID.
        
        Args:
            history_id: UUID of the notification.
            user_id: UUID of the user (for security).
        
        Returns:
            NotificationHistory if found and owned by user, None otherwise.
        """
        result = await self.session.execute(
            select(NotificationHistory).where(
                and_(
                    NotificationHistory.id == history_id,
                    NotificationHistory.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_user(
        self,
        user_id: uuid.UUID,
        notification_type: Optional[NotificationType] = None,
        status: Optional[NotificationStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[NotificationHistory], int]:
        """Get notification history for a user with filtering.
        
        Args:
            user_id: UUID of the user.
            notification_type: Optional filter by type.
            status: Optional filter by status.
            limit: Maximum number of results.
            offset: Number of results to skip.
        
        Returns:
            Tuple of (list of notifications, total count).
        """
        # Build base query
        base_query = select(NotificationHistory).where(
            NotificationHistory.user_id == user_id
        )
        
        # Apply filters
        if notification_type:
            base_query = base_query.where(
                NotificationHistory.type == notification_type
            )
        if status:
            base_query = base_query.where(
                NotificationHistory.status == status
            )
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0
        
        # Get paginated results
        query = base_query.order_by(
            desc(NotificationHistory.created_at)
        ).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        notifications = list(result.scalars().all())
        
        return notifications, total
    
    async def get_failed(
        self,
        user_id: uuid.UUID,
        limit: int = 20,
    ) -> List[NotificationHistory]:
        """Get failed notifications for a user.
        
        Args:
            user_id: UUID of the user.
            limit: Maximum number of results.
        
        Returns:
            List of failed notifications.
        """
        result = await self.session.execute(
            select(NotificationHistory).where(
                and_(
                    NotificationHistory.user_id == user_id,
                    NotificationHistory.status == NotificationStatus.FAILED,
                )
            ).order_by(
                desc(NotificationHistory.created_at)
            ).limit(limit)
        )
        return list(result.scalars().all())
    
    async def update_status(
        self,
        history_id: uuid.UUID,
        status: NotificationStatus,
        error_message: Optional[str] = None,
        sent_at: Optional[datetime] = None,
    ) -> Optional[NotificationHistory]:
        """Update notification status.
        
        Args:
            history_id: UUID of the notification.
            status: New status.
            error_message: Error message if failed.
            sent_at: Timestamp when sent (auto-set for SENT status).
        
        Returns:
            Updated NotificationHistory or None if not found.
        """
        result = await self.session.execute(
            select(NotificationHistory).where(
                NotificationHistory.id == history_id
            )
        )
        history = result.scalar_one_or_none()
        
        if not history:
            return None
        
        history.status = status
        history.error_message = error_message
        
        if status == NotificationStatus.SENT and sent_at is None:
            history.sent_at = datetime.now(timezone.utc)
        elif sent_at:
            history.sent_at = sent_at
        
        await self.session.flush()
        await self.session.refresh(history)
        
        logger.info(f"Updated notification {history_id} status to {status.value}")
        
        return history
    
    async def delete(
        self,
        history_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete a notification history entry.
        
        Args:
            history_id: UUID of the notification.
            user_id: UUID of the user (for security).
        
        Returns:
            True if deleted, False if not found.
        """
        result = await self.session.execute(
            select(NotificationHistory).where(
                and_(
                    NotificationHistory.id == history_id,
                    NotificationHistory.user_id == user_id,
                )
            )
        )
        history = result.scalar_one_or_none()
        
        if not history:
            return False
        
        await self.session.delete(history)
        await self.session.flush()
        
        logger.info(f"Deleted notification history: id={history_id}")
        
        return True
    
    async def get_stats(
        self,
        user_id: uuid.UUID,
    ) -> dict:
        """Get notification statistics for a user.
        
        Args:
            user_id: UUID of the user.
        
        Returns:
            Dictionary with stats (total, sent, failed, by type).
        """
        # Total count
        total_result = await self.session.execute(
            select(func.count()).where(
                NotificationHistory.user_id == user_id
            )
        )
        total = total_result.scalar() or 0
        
        # By status
        sent_result = await self.session.execute(
            select(func.count()).where(
                and_(
                    NotificationHistory.user_id == user_id,
                    NotificationHistory.status == NotificationStatus.SENT,
                )
            )
        )
        sent = sent_result.scalar() or 0
        
        failed_result = await self.session.execute(
            select(func.count()).where(
                and_(
                    NotificationHistory.user_id == user_id,
                    NotificationHistory.status == NotificationStatus.FAILED,
                )
            )
        )
        failed = failed_result.scalar() or 0
        
        # By type
        email_result = await self.session.execute(
            select(func.count()).where(
                and_(
                    NotificationHistory.user_id == user_id,
                    NotificationHistory.type == NotificationType.EMAIL,
                )
            )
        )
        email_count = email_result.scalar() or 0
        
        whatsapp_result = await self.session.execute(
            select(func.count()).where(
                and_(
                    NotificationHistory.user_id == user_id,
                    NotificationHistory.type == NotificationType.WHATSAPP,
                )
            )
        )
        whatsapp_count = whatsapp_result.scalar() or 0
        
        return {
            "total": total,
            "sent": sent,
            "failed": failed,
            "pending": total - sent - failed,
            "by_type": {
                "email": email_count,
                "whatsapp": whatsapp_count,
            },
        }
