"""Database module for CV Screening Agent.

This module provides database connectivity, models, and utilities for
PostgreSQL with pgvector support.

Submodules:
    base: SQLAlchemy Base class and common model mixins.
    session: Async database session management.
    models: SQLAlchemy ORM models for all tables.
    encryption: AES-256 encryption utilities for API keys.
    seed: Database seed data for system templates.

Example:
    Using database session in FastAPI::
    
        from app.db import get_async_session
        from app.db.models import User
        
        @router.get("/users")
        async def get_users(session: AsyncSession = Depends(get_async_session)):
            result = await session.execute(select(User))
            return result.scalars().all()
"""

from app.db.base import Base, TimestampMixin
from app.db.session import get_async_session, get_db_session, async_engine, engine, AsyncSessionLocal

__all__ = [
    "Base",
    "TimestampMixin",
    "get_async_session",
    "get_db_session",
    "async_engine",
    "engine",
    "AsyncSessionLocal",
]
