"""FastAPI dependencies for notification feature.

This module provides dependency injection for notification endpoints.

Functions:
    get_notification_controller: Create NotificationController with dependencies.
    get_notification_service: Create NotificationService with dependencies.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.features.auth.auth_dependencies import get_current_user
from app.db.models.user import User
from .notification_controller import NotificationController
from .notification_service import NotificationService


async def get_notification_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> NotificationService:
    """Create NotificationService with injected dependencies.
    
    Args:
        session: Database session from dependency.
    
    Returns:
        NotificationService instance.
    """
    return NotificationService(session)


async def get_notification_controller(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> NotificationController:
    """Create NotificationController with injected dependencies.
    
    Args:
        session: Database session from dependency.
        current_user: Authenticated user from dependency.
    
    Returns:
        NotificationController instance.
    """
    return NotificationController(session, current_user)
