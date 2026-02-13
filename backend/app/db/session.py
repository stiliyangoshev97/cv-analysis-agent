"""Async database session management.

This module provides async database connectivity using SQLAlchemy 2.0
async engine and session factories.

Functions:
    get_async_session: FastAPI dependency for database sessions.

Variables:
    async_engine: Async SQLAlchemy engine instance.
    AsyncSessionLocal: Async session factory.

Example:
    Using in FastAPI endpoint::
    
        from app.db import get_async_session
        
        @router.get("/users/{id}")
        async def get_user(
            id: UUID,
            session: AsyncSession = Depends(get_async_session)
        ):
            user = await session.get(User, id)
            return user

Note:
    Database URL should be set in DATABASE_URL environment variable.
    Format: postgresql+asyncpg://user:pass@host:port/dbname
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

settings = get_settings()

# Create async engine
# Using asyncpg driver for PostgreSQL
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL statements in debug mode
    pool_pre_ping=True,   # Verify connections before using
    pool_size=5,
    max_overflow=10,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an async database session.
    
    Creates a new session for each request and automatically closes it
    after the request completes. Uses async context manager for proper
    cleanup.
    
    Yields:
        AsyncSession: SQLAlchemy async session for database operations.
    
    Example:
        >>> @router.get("/items")
        ... async def get_items(session: AsyncSession = Depends(get_async_session)):
        ...     result = await session.execute(select(Item))
        ...     return result.scalars().all()
    
    Note:
        Session is automatically rolled back on exceptions and closed
        after the request completes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
