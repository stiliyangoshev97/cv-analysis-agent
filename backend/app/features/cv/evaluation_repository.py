"""Evaluation repository for database operations.

This module provides the EvaluationRepository class for performing
database CRUD operations on CVEvaluation entities using SQLAlchemy.

Classes:
    EvaluationRepository: Async repository for evaluation database operations.

Example:
    Using the repository::
    
        async with get_db_session() as session:
            repo = EvaluationRepository(session)
            evaluations = await repo.get_by_cv(cv_id)
"""

import uuid
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.cv import CVEvaluation


class EvaluationRepository:
    """Repository for CVEvaluation database operations.
    
    Provides async methods for CRUD operations on CVEvaluation entities.
    Uses SQLAlchemy AsyncSession for all database interactions.
    
    Attributes:
        session: AsyncSession for database operations.
    
    Example:
        >>> repo = EvaluationRepository(session)
        >>> evaluation = await repo.get_by_id(evaluation_id)
        >>> if evaluation:
        ...     print(f"Score: {evaluation.score}")
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy AsyncSession for database operations.
        """
        self.session = session
    
    async def create(self, evaluation: CVEvaluation) -> CVEvaluation:
        """Create a new evaluation in the database.
        
        Args:
            evaluation: CVEvaluation entity to persist.
            
        Returns:
            The persisted CVEvaluation entity with generated ID.
        """
        self.session.add(evaluation)
        await self.session.commit()
        await self.session.refresh(evaluation)
        return evaluation
    
    async def get_by_id(
        self,
        evaluation_id: uuid.UUID,
        include_cv: bool = False,
        include_template: bool = False,
    ) -> Optional[CVEvaluation]:
        """Get evaluation by ID.
        
        Args:
            evaluation_id: Evaluation's UUID.
            include_cv: Whether to eagerly load the CV.
            include_template: Whether to eagerly load the template.
            
        Returns:
            CVEvaluation if found, None otherwise.
        """
        query = select(CVEvaluation).where(CVEvaluation.id == evaluation_id)
        
        if include_cv:
            query = query.options(selectinload(CVEvaluation.cv))
        if include_template:
            query = query.options(selectinload(CVEvaluation.template))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_cv(
        self,
        cv_id: uuid.UUID,
        include_template: bool = False,
    ) -> List[CVEvaluation]:
        """Get all evaluations for a CV.
        
        Args:
            cv_id: CV's UUID.
            include_template: Whether to eagerly load templates.
            
        Returns:
            List of CVEvaluation entities, ordered by evaluation date (newest first).
        """
        query = (
            select(CVEvaluation)
            .where(CVEvaluation.cv_id == cv_id)
            .order_by(CVEvaluation.evaluated_at.desc())
        )
        
        if include_template:
            query = query.options(selectinload(CVEvaluation.template))
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_latest_by_cv(
        self,
        cv_id: uuid.UUID,
        include_template: bool = False,
    ) -> Optional[CVEvaluation]:
        """Get the most recent evaluation for a CV.
        
        Args:
            cv_id: CV's UUID.
            include_template: Whether to eagerly load the template.
            
        Returns:
            Most recent CVEvaluation if exists, None otherwise.
        """
        query = (
            select(CVEvaluation)
            .where(CVEvaluation.cv_id == cv_id)
            .order_by(CVEvaluation.evaluated_at.desc())
            .limit(1)
        )
        
        if include_template:
            query = query.options(selectinload(CVEvaluation.template))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_template(
        self,
        template_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[CVEvaluation]:
        """Get all evaluations using a template.
        
        Args:
            template_id: Template's UUID.
            limit: Maximum number of evaluations to return.
            offset: Number of evaluations to skip (for pagination).
            
        Returns:
            List of CVEvaluation entities using the template.
        """
        result = await self.session.execute(
            select(CVEvaluation)
            .where(CVEvaluation.template_id == template_id)
            .order_by(CVEvaluation.evaluated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    async def get_by_status(
        self,
        status: str,
        limit: int = 100,
    ) -> List[CVEvaluation]:
        """Get evaluations by pass/fail status.
        
        Args:
            status: "pass" or "fail".
            limit: Maximum number of evaluations to return.
            
        Returns:
            List of CVEvaluation entities with the specified status.
        """
        result = await self.session.execute(
            select(CVEvaluation)
            .where(CVEvaluation.status == status)
            .order_by(CVEvaluation.evaluated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_by_cv(self, cv_id: uuid.UUID) -> int:
        """Count evaluations for a CV.
        
        Args:
            cv_id: CV's UUID.
            
        Returns:
            Number of evaluations for the CV.
        """
        from sqlalchemy import func
        
        result = await self.session.execute(
            select(func.count(CVEvaluation.id)).where(CVEvaluation.cv_id == cv_id)
        )
        return result.scalar() or 0
    
    async def delete(self, evaluation: CVEvaluation) -> None:
        """Delete evaluation from the database.
        
        Args:
            evaluation: CVEvaluation entity to delete.
        """
        await self.session.delete(evaluation)
        await self.session.commit()
    
    async def delete_by_cv(self, cv_id: uuid.UUID) -> int:
        """Delete all evaluations for a CV.
        
        Args:
            cv_id: CV's UUID.
            
        Returns:
            Number of evaluations deleted.
        """
        from sqlalchemy import delete
        
        result = await self.session.execute(
            delete(CVEvaluation).where(CVEvaluation.cv_id == cv_id)
        )
        await self.session.commit()
        return result.rowcount or 0
