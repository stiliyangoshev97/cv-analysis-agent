"""CV repository for database operations.

This module provides the CVRepository class for performing
database CRUD operations on CV entities using SQLAlchemy.

Classes:
    CVRepository: Async repository for CV database operations.

Example:
    Using the repository::
    
        async with get_db_session() as session:
            repo = CVRepository(session)
            cvs = await repo.get_by_user(user_id)
"""

import uuid
from typing import Optional, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.cv import CV, CVStatus


class CVRepository:
    """Repository for CV database operations.
    
    Provides async methods for CRUD operations on CV entities.
    Uses SQLAlchemy AsyncSession for all database interactions.
    
    Attributes:
        session: AsyncSession for database operations.
    
    Example:
        >>> repo = CVRepository(session)
        >>> cv = await repo.get_by_id(cv_id)
        >>> if cv:
        ...     print(cv.filename)
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy AsyncSession for database operations.
        """
        self.session = session
    
    async def create(self, cv: CV) -> CV:
        """Create a new CV in the database.
        
        Args:
            cv: CV entity to persist.
            
        Returns:
            The persisted CV entity with generated ID.
        """
        self.session.add(cv)
        await self.session.commit()
        await self.session.refresh(cv)
        return cv
    
    async def get_by_id(
        self,
        cv_id: uuid.UUID,
        include_evaluations: bool = False,
        include_embeddings: bool = False,
    ) -> Optional[CV]:
        """Get CV by ID.
        
        Args:
            cv_id: CV's UUID.
            include_evaluations: Whether to eagerly load evaluations.
            include_embeddings: Whether to eagerly load embeddings.
            
        Returns:
            CV if found, None otherwise.
        """
        query = select(CV).where(CV.id == cv_id)
        
        if include_evaluations:
            query = query.options(selectinload(CV.evaluations))
        if include_embeddings:
            query = query.options(selectinload(CV.embeddings))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_user(
        self,
        user_id: uuid.UUID,
        include_evaluations: bool = False,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[CV]:
        """Get all CVs for a user.
        
        Args:
            user_id: User's UUID.
            include_evaluations: Whether to eagerly load evaluations.
            limit: Maximum number of CVs to return.
            offset: Number of CVs to skip (for pagination).
            
        Returns:
            List of CV entities, ordered by upload date (newest first).
        """
        query = (
            select(CV)
            .where(CV.user_id == user_id)
            .order_by(CV.uploaded_at.desc())
            .offset(offset)
        )
        
        if include_evaluations:
            query = query.options(selectinload(CV.evaluations))
        if limit is not None:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_by_user(self, user_id: uuid.UUID) -> int:
        """Count CVs for a user.
        
        Args:
            user_id: User's UUID.
            
        Returns:
            Number of CVs uploaded by the user.
        """
        from sqlalchemy import func
        
        result = await self.session.execute(
            select(func.count(CV.id)).where(CV.user_id == user_id)
        )
        return result.scalar() or 0
    
    async def update_status(
        self,
        cv_id: uuid.UUID,
        status: CVStatus,
    ) -> Optional[CV]:
        """Update CV processing status.
        
        Args:
            cv_id: CV's UUID.
            status: New status value.
            
        Returns:
            Updated CV if found, None otherwise.
        """
        await self.session.execute(
            update(CV).where(CV.id == cv_id).values(status=status.value)
        )
        await self.session.commit()
        return await self.get_by_id(cv_id)
    
    async def update_candidate_name(
        self,
        cv_id: uuid.UUID,
        candidate_name: str,
    ) -> Optional[CV]:
        """Update extracted candidate name.
        
        Args:
            cv_id: CV's UUID.
            candidate_name: Extracted candidate name.
            
        Returns:
            Updated CV if found, None otherwise.
        """
        await self.session.execute(
            update(CV).where(CV.id == cv_id).values(candidate_name=candidate_name)
        )
        await self.session.commit()
        return await self.get_by_id(cv_id)
    
    async def update(self, cv: CV) -> CV:
        """Update CV in the database.
        
        Args:
            cv: CV entity with updated fields.
            
        Returns:
            The updated CV entity.
        """
        await self.session.commit()
        await self.session.refresh(cv)
        return cv
    
    async def delete(self, cv: CV) -> None:
        """Delete CV from the database.
        
        Cascades to delete related evaluations, embeddings, and chat history.
        
        Args:
            cv: CV entity to delete.
        """
        await self.session.delete(cv)
        await self.session.commit()
    
    async def delete_by_id(self, cv_id: uuid.UUID) -> bool:
        """Delete CV by ID.
        
        Args:
            cv_id: CV's UUID.
            
        Returns:
            True if deleted, False if not found.
        """
        cv = await self.get_by_id(cv_id)
        if cv:
            await self.delete(cv)
            return True
        return False
    
    async def exists(self, cv_id: uuid.UUID) -> bool:
        """Check if CV exists.
        
        Args:
            cv_id: CV's UUID.
            
        Returns:
            True if CV exists, False otherwise.
        """
        result = await self.session.execute(
            select(CV.id).where(CV.id == cv_id)
        )
        return result.scalar_one_or_none() is not None
    
    async def get_by_status(
        self,
        status: CVStatus,
        limit: int = 100,
    ) -> List[CV]:
        """Get CVs by processing status.
        
        Useful for batch processing or retrying failed CVs.
        
        Args:
            status: Status to filter by.
            limit: Maximum number of CVs to return.
            
        Returns:
            List of CVs with the specified status.
        """
        result = await self.session.execute(
            select(CV)
            .where(CV.status == status.value)
            .order_by(CV.uploaded_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
