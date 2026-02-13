"""Chat repository for database operations.

This module provides the ChatRepository class for performing
database CRUD operations on ChatHistory entities using SQLAlchemy.

Classes:
    ChatRepository: Async repository for chat history database operations.

Example:
    Using the repository::
    
        async with get_db_session() as session:
            repo = ChatRepository(session)
            history = await repo.get_conversation(user_id, cv_id)
"""

import uuid
from typing import Optional, List

from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.chat import ChatHistory, ChatRole


class ChatRepository:
    """Repository for ChatHistory database operations.
    
    Provides async methods for CRUD operations on ChatHistory entities.
    Used for RAG conversation persistence.
    
    Attributes:
        session: AsyncSession for database operations.
    
    Example:
        >>> repo = ChatRepository(session)
        >>> messages = await repo.get_conversation(user_id, cv_id)
        >>> for msg in messages:
        ...     print(f"{msg.role}: {msg.message[:50]}...")
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy AsyncSession for database operations.
        """
        self.session = session
    
    async def add_message(
        self,
        user_id: uuid.UUID,
        cv_id: uuid.UUID,
        role: ChatRole,
        message: str,
    ) -> ChatHistory:
        """Add a message to the conversation.
        
        Args:
            user_id: User's UUID.
            cv_id: CV's UUID.
            role: Message sender role (user/assistant/system).
            message: Message content.
            
        Returns:
            The persisted ChatHistory entity.
        """
        chat_message = ChatHistory(
            user_id=user_id,
            cv_id=cv_id,
            role=role.value,
            message=message,
        )
        self.session.add(chat_message)
        await self.session.commit()
        await self.session.refresh(chat_message)
        return chat_message
    
    async def add_user_message(
        self,
        user_id: uuid.UUID,
        cv_id: uuid.UUID,
        message: str,
    ) -> ChatHistory:
        """Add a user message to the conversation.
        
        Convenience method for adding user messages.
        
        Args:
            user_id: User's UUID.
            cv_id: CV's UUID.
            message: Message content.
            
        Returns:
            The persisted ChatHistory entity.
        """
        return await self.add_message(user_id, cv_id, ChatRole.USER, message)
    
    async def add_assistant_message(
        self,
        user_id: uuid.UUID,
        cv_id: uuid.UUID,
        message: str,
    ) -> ChatHistory:
        """Add an assistant message to the conversation.
        
        Convenience method for adding AI responses.
        
        Args:
            user_id: User's UUID.
            cv_id: CV's UUID.
            message: Message content.
            
        Returns:
            The persisted ChatHistory entity.
        """
        return await self.add_message(user_id, cv_id, ChatRole.ASSISTANT, message)
    
    async def get_conversation(
        self,
        user_id: uuid.UUID,
        cv_id: uuid.UUID,
        limit: Optional[int] = None,
    ) -> List[ChatHistory]:
        """Get conversation history for a CV.
        
        Args:
            user_id: User's UUID.
            cv_id: CV's UUID.
            limit: Maximum number of messages to return (most recent).
            
        Returns:
            List of ChatHistory entities, ordered by creation time (oldest first).
        """
        query = (
            select(ChatHistory)
            .where(
                and_(
                    ChatHistory.user_id == user_id,
                    ChatHistory.cv_id == cv_id,
                )
            )
            .order_by(ChatHistory.created_at.asc())
        )
        
        if limit is not None:
            # Get the last N messages by using a subquery
            subquery = (
                select(ChatHistory.id)
                .where(
                    and_(
                        ChatHistory.user_id == user_id,
                        ChatHistory.cv_id == cv_id,
                    )
                )
                .order_by(ChatHistory.created_at.desc())
                .limit(limit)
            )
            query = (
                select(ChatHistory)
                .where(ChatHistory.id.in_(subquery))
                .order_by(ChatHistory.created_at.asc())
            )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_recent_messages(
        self,
        user_id: uuid.UUID,
        cv_id: uuid.UUID,
        count: int = 10,
    ) -> List[ChatHistory]:
        """Get the most recent messages from a conversation.
        
        Useful for RAG context window management.
        
        Args:
            user_id: User's UUID.
            cv_id: CV's UUID.
            count: Number of recent messages to retrieve.
            
        Returns:
            List of ChatHistory entities, ordered by creation time (oldest first).
        """
        return await self.get_conversation(user_id, cv_id, limit=count)
    
    async def count_messages(
        self,
        user_id: uuid.UUID,
        cv_id: uuid.UUID,
    ) -> int:
        """Count messages in a conversation.
        
        Args:
            user_id: User's UUID.
            cv_id: CV's UUID.
            
        Returns:
            Number of messages in the conversation.
        """
        from sqlalchemy import func
        
        result = await self.session.execute(
            select(func.count(ChatHistory.id)).where(
                and_(
                    ChatHistory.user_id == user_id,
                    ChatHistory.cv_id == cv_id,
                )
            )
        )
        return result.scalar() or 0
    
    async def clear_conversation(
        self,
        user_id: uuid.UUID,
        cv_id: uuid.UUID,
    ) -> int:
        """Clear all messages in a conversation.
        
        Args:
            user_id: User's UUID.
            cv_id: CV's UUID.
            
        Returns:
            Number of messages deleted.
        """
        result = await self.session.execute(
            delete(ChatHistory).where(
                and_(
                    ChatHistory.user_id == user_id,
                    ChatHistory.cv_id == cv_id,
                )
            )
        )
        await self.session.commit()
        return result.rowcount or 0
    
    async def get_by_id(
        self,
        message_id: uuid.UUID,
    ) -> Optional[ChatHistory]:
        """Get message by ID.
        
        Args:
            message_id: Message's UUID.
            
        Returns:
            ChatHistory if found, None otherwise.
        """
        result = await self.session.execute(
            select(ChatHistory).where(ChatHistory.id == message_id)
        )
        return result.scalar_one_or_none()
    
    async def delete_message(
        self,
        message: ChatHistory,
    ) -> None:
        """Delete a single message.
        
        Args:
            message: ChatHistory entity to delete.
        """
        await self.session.delete(message)
        await self.session.commit()
    
    async def get_all_conversations_for_user(
        self,
        user_id: uuid.UUID,
    ) -> List[uuid.UUID]:
        """Get all CV IDs with conversations for a user.
        
        Useful for listing CVs with chat history.
        
        Args:
            user_id: User's UUID.
            
        Returns:
            List of CV UUIDs that have conversation history.
        """
        from sqlalchemy import distinct
        
        result = await self.session.execute(
            select(distinct(ChatHistory.cv_id)).where(
                ChatHistory.user_id == user_id
            )
        )
        return list(result.scalars().all())
    
    async def get_conversations_summary(
        self,
        user_id: uuid.UUID,
    ) -> List[dict]:
        """Get summary of all conversations for a user.
        
        Returns CV IDs with message counts.
        
        Args:
            user_id: User's UUID.
            
        Returns:
            List of dicts with cv_id and message_count.
        """
        from sqlalchemy import func
        
        result = await self.session.execute(
            select(
                ChatHistory.cv_id,
                func.count(ChatHistory.id).label("message_count"),
                func.max(ChatHistory.created_at).label("last_message_at"),
            )
            .where(ChatHistory.user_id == user_id)
            .group_by(ChatHistory.cv_id)
            .order_by(func.max(ChatHistory.created_at).desc())
        )
        
        return [
            {
                "cv_id": row.cv_id,
                "message_count": row.message_count,
                "last_message_at": row.last_message_at,
            }
            for row in result.all()
        ]
