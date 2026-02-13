"""Chat feature dependencies for FastAPI.

This module provides FastAPI dependencies specific to the chat feature.
Dependencies are used for dependency injection in route handlers.

Dependencies:
    get_chat_service: Inject ChatService instance with database session.

Example:
    Using dependencies in routes::
    
        from .chat_dependencies import get_chat_service
        
        @router.post("/{cv_id}")
        async def ask_question(
            cv_id: UUID,
            request: ChatMessageRequest,
            chat_service: ChatService = Depends(get_chat_service)
        ):
            return await chat_service.ask(...)
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from .chat_service import ChatService


async def get_chat_service(
    session: AsyncSession = Depends(get_db_session),
) -> ChatService:
    """Dependency to inject ChatService with database session.
    
    Creates a new ChatService instance for each request with the
    request-scoped database session.
    
    Args:
        session: SQLAlchemy async session (injected).
    
    Returns:
        ChatService instance with database access.
    
    Example:
        >>> @router.post("/{cv_id}")
        ... async def ask_question(
        ...     chat_service: ChatService = Depends(get_chat_service)
        ... ):
        ...     return await chat_service.ask(...)
    """
    return ChatService(session)
