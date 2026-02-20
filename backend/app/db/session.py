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

import ssl as _ssl
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

settings = get_settings()


def _build_engine_kwargs(database_url: str) -> dict:
    """Build engine kwargs, handling SSL for Neon/cloud PostgreSQL.
    
    SQLAlchemy's asyncpg dialect does not pass query-string SSL params
    (like ?sslmode=require) through to asyncpg. Instead, SSL must be
    provided via connect_args={'ssl': <ssl.SSLContext>}.
    
    This function detects SSL params in the URL, strips them, and
    returns the cleaned URL + appropriate connect_args.
    """
    parsed = urlparse(database_url)
    query_params = parse_qs(parsed.query)
    
    needs_ssl = (
        "sslmode" in query_params
        or "ssl" in query_params
        or ".neon.tech" in (parsed.hostname or "")
    )
    
    # Strip SSL-related query params that asyncpg doesn't understand
    for key in ("sslmode", "ssl", "channel_binding"):
        query_params.pop(key, None)
    
    # Rebuild URL without SSL params
    new_query = urlencode(query_params, doseq=True)
    clean_url = urlunparse(parsed._replace(query=new_query))
    
    kwargs = {"url": clean_url}
    
    if needs_ssl:
        ssl_ctx = _ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = _ssl.CERT_NONE
        kwargs["connect_args"] = {"ssl": ssl_ctx}
    
    return kwargs


_engine_kwargs = _build_engine_kwargs(settings.database_url)

# Create async engine
# Using asyncpg driver for PostgreSQL
async_engine = create_async_engine(
    _engine_kwargs["url"],
    echo=settings.debug,  # Log SQL statements in debug mode
    pool_pre_ping=True,   # Verify connections before using
    pool_size=5,
    max_overflow=10,
    **({k: v for k, v in _engine_kwargs.items() if k != "url"}),
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


# Alias for compatibility
get_db_session = get_async_session

# Export engine for migrations
engine = async_engine
