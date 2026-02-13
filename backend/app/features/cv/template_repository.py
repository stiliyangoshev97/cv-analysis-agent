"""Template repository for database operations.

This module provides the TemplateRepository class for performing
database CRUD operations on EvaluationTemplate and TemplateCriterion
entities using SQLAlchemy.

Classes:
    TemplateRepository: Async repository for template database operations.

Example:
    Using the repository::
    
        async with get_db_session() as session:
            repo = TemplateRepository(session)
            template = await repo.get_with_criteria(template_id)
"""

import uuid
from typing import Optional, List

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.template import EvaluationTemplate, TemplateCriterion


class TemplateRepository:
    """Repository for EvaluationTemplate database operations.
    
    Provides async methods for CRUD operations on EvaluationTemplate
    and TemplateCriterion entities.
    
    Attributes:
        session: AsyncSession for database operations.
    
    Example:
        >>> repo = TemplateRepository(session)
        >>> templates = await repo.get_available_for_user(user_id)
        >>> for template in templates:
        ...     print(template.name)
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy AsyncSession for database operations.
        """
        self.session = session
    
    async def create(self, template: EvaluationTemplate) -> EvaluationTemplate:
        """Create a new template in the database.
        
        Args:
            template: EvaluationTemplate entity to persist.
            
        Returns:
            The persisted EvaluationTemplate entity with generated ID.
        """
        self.session.add(template)
        await self.session.commit()
        await self.session.refresh(template)
        return template
    
    async def get_by_id(
        self,
        template_id: uuid.UUID,
        include_criteria: bool = False,
    ) -> Optional[EvaluationTemplate]:
        """Get template by ID.
        
        Args:
            template_id: Template's UUID.
            include_criteria: Whether to eagerly load criteria.
            
        Returns:
            EvaluationTemplate if found, None otherwise.
        """
        query = select(EvaluationTemplate).where(EvaluationTemplate.id == template_id)
        
        if include_criteria:
            query = query.options(selectinload(EvaluationTemplate.criteria))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_with_criteria(
        self,
        template_id: uuid.UUID,
    ) -> Optional[EvaluationTemplate]:
        """Get template with all criteria loaded.
        
        Convenience method for getting a template ready for evaluation.
        
        Args:
            template_id: Template's UUID.
            
        Returns:
            EvaluationTemplate with criteria loaded, None if not found.
        """
        return await self.get_by_id(template_id, include_criteria=True)
    
    async def get_by_name(
        self,
        name: str,
        include_criteria: bool = False,
    ) -> Optional[EvaluationTemplate]:
        """Get template by name.
        
        Args:
            name: Template name to search for.
            include_criteria: Whether to eagerly load criteria.
            
        Returns:
            EvaluationTemplate if found, None otherwise.
        """
        query = select(EvaluationTemplate).where(EvaluationTemplate.name == name)
        
        if include_criteria:
            query = query.options(selectinload(EvaluationTemplate.criteria))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_system_templates(
        self,
        include_criteria: bool = False,
    ) -> List[EvaluationTemplate]:
        """Get all system templates.
        
        Args:
            include_criteria: Whether to eagerly load criteria.
            
        Returns:
            List of system EvaluationTemplate entities.
        """
        query = (
            select(EvaluationTemplate)
            .where(EvaluationTemplate.is_system_template == True)
            .order_by(EvaluationTemplate.name)
        )
        
        if include_criteria:
            query = query.options(selectinload(EvaluationTemplate.criteria))
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_user(
        self,
        user_id: uuid.UUID,
        include_criteria: bool = False,
    ) -> List[EvaluationTemplate]:
        """Get all templates created by a user.
        
        Does not include system templates.
        
        Args:
            user_id: User's UUID.
            include_criteria: Whether to eagerly load criteria.
            
        Returns:
            List of EvaluationTemplate entities created by the user.
        """
        query = (
            select(EvaluationTemplate)
            .where(EvaluationTemplate.user_id == user_id)
            .order_by(EvaluationTemplate.created_at.desc())
        )
        
        if include_criteria:
            query = query.options(selectinload(EvaluationTemplate.criteria))
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_available_for_user(
        self,
        user_id: uuid.UUID,
        include_criteria: bool = False,
    ) -> List[EvaluationTemplate]:
        """Get all templates available to a user.
        
        Includes both system templates and user-created templates.
        
        Args:
            user_id: User's UUID.
            include_criteria: Whether to eagerly load criteria.
            
        Returns:
            List of EvaluationTemplate entities available to the user.
        """
        query = (
            select(EvaluationTemplate)
            .where(
                or_(
                    EvaluationTemplate.is_system_template == True,
                    EvaluationTemplate.user_id == user_id,
                )
            )
            .order_by(
                EvaluationTemplate.is_system_template.desc(),
                EvaluationTemplate.name,
            )
        )
        
        if include_criteria:
            query = query.options(selectinload(EvaluationTemplate.criteria))
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_default_template(
        self,
        include_criteria: bool = True,
    ) -> Optional[EvaluationTemplate]:
        """Get the default system template.
        
        Returns the first system template, typically "AI-First Fintech".
        
        Args:
            include_criteria: Whether to eagerly load criteria.
            
        Returns:
            Default EvaluationTemplate or None if no system templates exist.
        """
        templates = await self.get_system_templates(include_criteria=include_criteria)
        return templates[0] if templates else None
    
    async def update(self, template: EvaluationTemplate) -> EvaluationTemplate:
        """Update template in the database.
        
        Args:
            template: EvaluationTemplate entity with updated fields.
            
        Returns:
            The updated EvaluationTemplate entity.
            
        Raises:
            ValueError: If attempting to update a system template.
        """
        if template.is_system_template:
            raise ValueError("Cannot update system templates")
        
        await self.session.commit()
        await self.session.refresh(template)
        return template
    
    async def delete(self, template: EvaluationTemplate) -> None:
        """Delete template from the database.
        
        Cascades to delete related criteria.
        
        Args:
            template: EvaluationTemplate entity to delete.
            
        Raises:
            ValueError: If attempting to delete a system template.
        """
        if template.is_system_template:
            raise ValueError("Cannot delete system templates")
        
        await self.session.delete(template)
        await self.session.commit()
    
    # --- Criterion Operations ---
    
    async def add_criterion(
        self,
        criterion: TemplateCriterion,
    ) -> TemplateCriterion:
        """Add a criterion to a template.
        
        Args:
            criterion: TemplateCriterion entity to persist.
            
        Returns:
            The persisted TemplateCriterion entity.
        """
        self.session.add(criterion)
        await self.session.commit()
        await self.session.refresh(criterion)
        return criterion
    
    async def get_criteria_by_template(
        self,
        template_id: uuid.UUID,
    ) -> List[TemplateCriterion]:
        """Get all criteria for a template.
        
        Args:
            template_id: Template's UUID.
            
        Returns:
            List of TemplateCriterion entities, ordered by sort_order.
        """
        result = await self.session.execute(
            select(TemplateCriterion)
            .where(TemplateCriterion.template_id == template_id)
            .order_by(TemplateCriterion.sort_order)
        )
        return list(result.scalars().all())
    
    async def get_criterion_by_id(
        self,
        criterion_id: uuid.UUID,
    ) -> Optional[TemplateCriterion]:
        """Get criterion by ID.
        
        Args:
            criterion_id: Criterion's UUID.
            
        Returns:
            TemplateCriterion if found, None otherwise.
        """
        result = await self.session.execute(
            select(TemplateCriterion).where(TemplateCriterion.id == criterion_id)
        )
        return result.scalar_one_or_none()
    
    async def update_criterion(
        self,
        criterion: TemplateCriterion,
    ) -> TemplateCriterion:
        """Update criterion in the database.
        
        Args:
            criterion: TemplateCriterion entity with updated fields.
            
        Returns:
            The updated TemplateCriterion entity.
        """
        await self.session.commit()
        await self.session.refresh(criterion)
        return criterion
    
    async def delete_criterion(
        self,
        criterion: TemplateCriterion,
    ) -> None:
        """Delete criterion from the database.
        
        Args:
            criterion: TemplateCriterion entity to delete.
        """
        await self.session.delete(criterion)
        await self.session.commit()
    
    async def exists(self, template_id: uuid.UUID) -> bool:
        """Check if template exists.
        
        Args:
            template_id: Template's UUID.
            
        Returns:
            True if template exists, False otherwise.
        """
        result = await self.session.execute(
            select(EvaluationTemplate.id).where(EvaluationTemplate.id == template_id)
        )
        return result.scalar_one_or_none() is not None
