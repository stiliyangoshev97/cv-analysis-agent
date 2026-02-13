"""User repository for database operations.

This module provides the UserRepository class for performing
database CRUD operations on User entities using SQLAlchemy.

Classes:
    UserRepository: Async repository for User database operations.

Example:
    Using the repository::
    
        async with get_db_session() as session:
            repo = UserRepository(session)
            user = await repo.get_by_email("user@example.com")
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UserRepository:
    """Repository for User database operations.
    
    Provides async methods for CRUD operations on User entities.
    Uses SQLAlchemy AsyncSession for all database interactions.
    
    Attributes:
        session: AsyncSession for database operations.
    
    Example:
        >>> repo = UserRepository(session)
        >>> user = await repo.get_by_email("test@example.com")
        >>> if user:
        ...     print(user.name)
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy AsyncSession for database operations.
        """
        self.session = session
    
    async def create(self, user: User) -> User:
        """Create a new user in the database.
        
        Args:
            user: User entity to persist.
            
        Returns:
            The persisted User entity with generated ID.
        """
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID.
        
        Args:
            user_id: User's UUID.
            
        Returns:
            User if found, None otherwise.
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address.
        
        Args:
            email: User's email address (case-insensitive).
            
        Returns:
            User if found, None otherwise.
        """
        result = await self.session.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()
    
    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID.
        
        Args:
            google_id: Google's unique user identifier.
            
        Returns:
            User if found, None otherwise.
        """
        result = await self.session.execute(
            select(User).where(User.google_id == google_id)
        )
        return result.scalar_one_or_none()
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if user with email exists.
        
        Args:
            email: Email address to check.
            
        Returns:
            True if user exists, False otherwise.
        """
        result = await self.session.execute(
            select(User.id).where(User.email == email.lower())
        )
        return result.scalar_one_or_none() is not None
    
    async def update(self, user: User) -> User:
        """Update user in the database.
        
        Args:
            user: User entity with updated fields.
            
        Returns:
            The updated User entity.
        """
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def delete(self, user: User) -> None:
        """Delete user from the database.
        
        Args:
            user: User entity to delete.
        """
        await self.session.delete(user)
        await self.session.commit()
