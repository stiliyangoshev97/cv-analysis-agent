"""Chat History model for conversational CV explanations.

This module defines the ChatHistory model for storing conversation
messages between users and the AI about CV evaluations.

Classes:
    ChatRole: Enum of message sender roles.
    ChatHistory: SQLAlchemy model for chat messages.

Example:
    Storing a chat exchange::
    
        # User asks a question
        user_msg = ChatHistory(
            user_id=user.id,
            cv_id=cv.id,
            role="user",
            message="Why did this candidate fail the fintech criteria?"
        )
        session.add(user_msg)
        
        # AI responds
        ai_msg = ChatHistory(
            user_id=user.id,
            cv_id=cv.id,
            role="assistant",
            message="The candidate failed because..."
        )
        session.add(ai_msg)
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.cv import CV


class ChatRole(str, Enum):
    """Message sender role values.
    
    Values:
        USER: Message from the user.
        ASSISTANT: Message from the AI assistant.
        SYSTEM: System message (context, instructions).
    """
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatHistory(Base):
    """Chat message history for CV explanations.
    
    Stores the conversation between a user and the AI about
    a specific CV evaluation. Used for the "Why?" feature.
    
    Attributes:
        id: Unique message identifier (UUID).
        user_id: Foreign key to users table.
        cv_id: Foreign key to cvs table.
        role: Message sender (user/assistant/system).
        message: Message content.
        created_at: Message timestamp.
        
    Relationships:
        user: The user in this conversation.
        cv: The CV being discussed.
    
    Example:
        >>> message = ChatHistory(
        ...     user_id=user.id,
        ...     cv_id=cv.id,
        ...     role="user",
        ...     message="Explain the technical skills score"
        ... )
    """
    
    __tablename__ = "chat_history"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cv_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cvs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Message content
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="chat_history",
    )
    cv: Mapped["CV"] = relationship(
        "CV",
        back_populates="chat_history",
    )
    
    def __repr__(self) -> str:
        return f"<ChatHistory {self.role}: {self.message[:30]}...>"
