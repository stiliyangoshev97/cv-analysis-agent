"""SQLAlchemy Base class and common model mixins.

This module provides the declarative base for all SQLAlchemy models
and common mixins for timestamp fields.

Classes:
    TimestampMixin: Adds created_at and updated_at columns.
    Base: SQLAlchemy declarative base for all models.

Example:
    Creating a model with timestamps::
    
        from app.db.base import Base, TimestampMixin
        
        class User(Base, TimestampMixin):
            __tablename__ = "users"
            id = Column(UUID, primary_key=True)
            email = Column(String, unique=True)
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative base class.
    
    All ORM models should inherit from this base class. It provides
    common configuration and type annotation support.
    
    Example:
        >>> class User(Base):
        ...     __tablename__ = "users"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
    """
    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamp columns.
    
    Automatically sets created_at on insert and updated_at on every update.
    Uses server-side defaults for consistency.
    
    Attributes:
        created_at: Timestamp when the record was created.
        updated_at: Timestamp when the record was last updated.
    
    Example:
        >>> class User(Base, TimestampMixin):
        ...     __tablename__ = "users"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
