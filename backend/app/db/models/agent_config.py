"""User Agent Configuration model for AI provider assignments.

This module defines the UserAgentConfig model for storing user
preferences on which AI provider to use for each agent type.

Classes:
    UserAgentConfig: SQLAlchemy model for agent-to-provider mapping.

Example:
    Setting agent configuration::
    
        config = UserAgentConfig(
            user_id=user.id,
            parser_provider="gemini",
            parser_model="gemini-2.0-flash",
            scorer_provider="claude",
            scorer_model="claude-sonnet-4-20250514",
            chat_provider="openai",
            chat_model="gpt-4o",
            embeddings_provider="openai",
            embeddings_model="text-embedding-3-small"
        )
        session.add(config)
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User


# Default configurations for each agent
DEFAULT_AGENT_CONFIG = {
    "parser_provider": "gemini",
    "parser_model": "gemini-2.0-flash",
    "scorer_provider": "claude",
    "scorer_model": "claude-sonnet-4-20250514",
    "chat_provider": "claude",
    "chat_model": "claude-sonnet-4-20250514",
    "embeddings_provider": "openai",
    "embeddings_model": "text-embedding-3-small",
}


class UserAgentConfig(Base, TimestampMixin):
    """Agent-to-provider configuration for a user.
    
    Stores which AI provider and model each agent should use.
    Each user has one configuration record.
    
    Attributes:
        id: Unique configuration identifier (UUID).
        user_id: Foreign key to users table.
        parser_provider: Provider for Parser Agent.
        parser_model: Model for Parser Agent.
        scorer_provider: Provider for Scorer Agent.
        scorer_model: Model for Scorer Agent.
        chat_provider: Provider for Chat Agent.
        chat_model: Model for Chat Agent.
        embeddings_provider: Provider for embeddings generation.
        embeddings_model: Model for embeddings generation.
        
    Relationships:
        user: The user who owns this configuration.
    
    Example:
        >>> config = UserAgentConfig(
        ...     user_id=user.id,
        ...     scorer_provider="claude",
        ...     scorer_model="claude-sonnet-4-20250514"
        ... )
    
    Note:
        Default values are used if specific agents are not configured.
    """
    
    __tablename__ = "user_agent_configs"
    
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
    
    # Parser Agent configuration
    parser_provider: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        default=DEFAULT_AGENT_CONFIG["parser_provider"],
    )
    parser_model: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default=DEFAULT_AGENT_CONFIG["parser_model"],
    )
    
    # Scorer Agent configuration
    scorer_provider: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        default=DEFAULT_AGENT_CONFIG["scorer_provider"],
    )
    scorer_model: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default=DEFAULT_AGENT_CONFIG["scorer_model"],
    )
    
    # Chat Agent configuration
    chat_provider: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        default=DEFAULT_AGENT_CONFIG["chat_provider"],
    )
    chat_model: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default=DEFAULT_AGENT_CONFIG["chat_model"],
    )
    
    # Embeddings configuration
    embeddings_provider: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        default=DEFAULT_AGENT_CONFIG["embeddings_provider"],
    )
    embeddings_model: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default=DEFAULT_AGENT_CONFIG["embeddings_model"],
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="agent_config",
    )
    
    def __repr__(self) -> str:
        return f"<UserAgentConfig for user {self.user_id}>"
