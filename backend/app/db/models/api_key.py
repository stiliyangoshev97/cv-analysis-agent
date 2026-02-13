"""User API Key model for storing encrypted AI provider keys.

This module defines the UserApiKey model for securely storing
user-provided API keys for various AI providers.

Classes:
    AIProvider: Enum of supported AI providers.
    UserApiKey: SQLAlchemy model for encrypted API keys.

Example:
    Storing an API key::
    
        from app.db.encryption import encrypt_api_key, get_key_hint
        
        api_key = UserApiKey(
            user_id=user.id,
            provider="claude",
            encrypted_key=encrypt_api_key("sk-ant-..."),
            key_hint=get_key_hint("sk-ant-...")
        )
        session.add(api_key)

Security:
    API keys are encrypted using AES-256 (Fernet) before storage.
    Only the last 4 characters are stored as a hint for UI display.
"""

import uuid
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class AIProvider(str, Enum):
    """Supported AI provider identifiers.
    
    Values:
        CLAUDE: Anthropic Claude models.
        OPENAI: OpenAI GPT models.
        GEMINI: Google Gemini models.
        GROQ: Groq inference API.
        OLLAMA: Local Ollama instance.
    """
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"
    GROQ = "groq"
    OLLAMA = "ollama"


class UserApiKey(Base, TimestampMixin):
    """Encrypted API key storage for AI providers.
    
    Stores user-provided API keys encrypted with AES-256. Each user
    can have one key per provider.
    
    Attributes:
        id: Unique key identifier (UUID).
        user_id: Foreign key to users table.
        provider: AI provider identifier (claude/openai/gemini/groq/ollama).
        encrypted_key: AES-256 encrypted API key.
        key_hint: Last 4 characters for UI display (e.g., "...x7Kj").
        is_valid: Whether the key has been validated.
        
    Relationships:
        user: The user who owns this API key.
    
    Example:
        >>> api_key = UserApiKey(
        ...     user_id=user.id,
        ...     provider="claude",
        ...     encrypted_key="gAAAAABh...",
        ...     key_hint="...x7Kj"
        ... )
    
    Note:
        The encrypted_key should be encrypted using app.db.encryption
        utilities before storage.
    """
    
    __tablename__ = "user_api_keys"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", name="uq_user_provider"),
    )
    
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
    
    # Provider identifier
    provider: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    
    # Encrypted API key (AES-256)
    encrypted_key: Mapped[str] = mapped_column(
        String(500),  # Fernet output is ~1.5x input length
        nullable=False,
    )
    
    # Key hint for display (last 4 chars)
    key_hint: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    
    # Validation status
    is_valid: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="api_keys",
    )
    
    def __repr__(self) -> str:
        return f"<UserApiKey {self.provider} for user {self.user_id}>"
