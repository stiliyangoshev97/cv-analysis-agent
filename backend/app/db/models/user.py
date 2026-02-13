"""User model for authentication and profile management.

This module defines the User model for storing user accounts,
authentication details, and profile information.

Classes:
    User: SQLAlchemy model for user accounts.

Example:
    Creating a new user::
    
        user = User(
            email="john@example.com",
            password_hash=hash_password("secret"),
            name="John Doe",
            auth_provider="email"
        )
        session.add(user)
        await session.commit()
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.api_key import UserApiKey
    from app.db.models.agent_config import UserAgentConfig
    from app.db.models.template import EvaluationTemplate
    from app.db.models.cv import CV
    from app.db.models.chat import ChatHistory
    from app.db.models.notification import NotificationSettings


class AuthProvider(str):
    """Authentication provider enum values."""
    EMAIL = "email"
    GOOGLE = "google"


class User(Base, TimestampMixin):
    """User account model.
    
    Stores user authentication details, profile information, and
    relationships to other user-owned entities.
    
    Attributes:
        id: Unique user identifier (UUID).
        email: User's email address (unique).
        password_hash: Bcrypt hashed password (null for OAuth users).
        name: User's display name.
        auth_provider: Authentication method used (email/google).
        is_active: Whether the account is active.
        is_onboarded: Whether user completed onboarding (API keys setup).
        
    Relationships:
        api_keys: User's API keys for AI providers.
        agent_config: User's agent configuration.
        templates: User's custom evaluation templates.
        cvs: CVs uploaded by the user.
        chat_history: Chat messages for CV explanations.
        notification_settings: Notification preferences.
    
    Example:
        >>> user = User(
        ...     email="jane@example.com",
        ...     password_hash="$2b$12$...",
        ...     name="Jane Doe",
        ...     auth_provider="email"
        ... )
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,  # Null for OAuth users
    )
    
    # Profile fields
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    
    # Auth metadata
    auth_provider: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="email",
    )
    
    # Account status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_onboarded: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    
    # Relationships
    api_keys: Mapped[List["UserApiKey"]] = relationship(
        "UserApiKey",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    agent_config: Mapped[Optional["UserAgentConfig"]] = relationship(
        "UserAgentConfig",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    templates: Mapped[List["EvaluationTemplate"]] = relationship(
        "EvaluationTemplate",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="EvaluationTemplate.user_id",
    )
    
    cvs: Mapped[List["CV"]] = relationship(
        "CV",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    chat_history: Mapped[List["ChatHistory"]] = relationship(
        "ChatHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    notification_settings: Mapped[Optional["NotificationSettings"]] = relationship(
        "NotificationSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
