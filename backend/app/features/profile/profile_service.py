"""Hiring Profile service for business logic.

This module provides the ProfileService class for managing
evaluation profiles (templates) with proper authorization checks.

The service:
1. Wraps TemplateRepository with authorization
2. Distinguishes system templates (read-only) from user templates
3. Provides CRUD operations for profiles and criteria
4. Supports cloning templates as starting points

Classes:
    ProfileService: Business logic for profile operations.

Example:
    Using the service::
    
        service = ProfileService(session)
        
        # List all available profiles
        profiles = await service.list_profiles(user_id)
        
        # Clone a system template
        my_profile = await service.clone_profile(
            source_id=system_template_id,
            user_id=user_id,
            new_name="My Custom Profile",
        )
"""

import uuid
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.template import EvaluationTemplate, TemplateCriterion
from app.features.cv.template_repository import TemplateRepository
from .profile_schemas import (
    ProfileCreate,
    ProfileUpdate,
    CriterionCreate,
    CriterionUpdate,
    ProfileResponse,
    ProfileSummary,
    ProfileListResponse,
    CriterionResponse,
)

logger = logging.getLogger(__name__)


class ProfileService:
    """Business logic service for hiring profiles.
    
    Provides CRUD operations for evaluation profiles (templates) with
    authorization checks. System templates are read-only; users can
    create their own or clone system templates.
    
    Attributes:
        session: AsyncSession for database operations.
        repo: TemplateRepository for database access.
    
    Authorization Rules:
        - System templates: Anyone can read, no one can modify
        - User templates: Only owner can read/modify
        - Clone: Can clone system templates or own templates
    
    Example:
        >>> service = ProfileService(session)
        >>> profiles = await service.list_profiles(user_id)
        >>> profile = await service.create_profile(user_id, ProfileCreate(...))
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with database session.
        
        Args:
            session: SQLAlchemy AsyncSession for database operations.
        """
        self.session = session
        self.repo = TemplateRepository(session)
    
    # =========================================================================
    # Profile CRUD
    # =========================================================================
    
    async def list_profiles(self, user_id: uuid.UUID) -> ProfileListResponse:
        """List all profiles available to a user.
        
        Returns both system templates (available to all) and
        user-created profiles (private to the user).
        
        Args:
            user_id: Current user's UUID.
            
        Returns:
            ProfileListResponse with profile summaries.
        
        Example:
            >>> response = await service.list_profiles(user_id)
            >>> for profile in response.profiles:
            ...     print(f"{profile.name}: {profile.criteria_count} criteria")
        """
        templates = await self.repo.get_available_for_user(
            user_id, 
            include_criteria=True
        )
        
        profiles = [
            ProfileSummary(
                id=t.id,
                name=t.name,
                description=t.description,
                is_system_template=t.is_system_template,
                passing_score=t.passing_score,
                criteria_count=len(t.criteria),
            )
            for t in templates
        ]
        
        return ProfileListResponse(profiles=profiles, total=len(profiles))
    
    async def get_profile(
        self, 
        profile_id: uuid.UUID, 
        user_id: uuid.UUID,
    ) -> Optional[ProfileResponse]:
        """Get a profile by ID with authorization check.
        
        Args:
            profile_id: Profile UUID to retrieve.
            user_id: Current user's UUID for authorization.
            
        Returns:
            ProfileResponse if found and authorized, None otherwise.
        
        Example:
            >>> profile = await service.get_profile(profile_id, user_id)
            >>> if profile:
            ...     print(f"{profile.name} has {len(profile.criteria)} criteria")
        """
        template = await self.repo.get_with_criteria(profile_id)
        
        if not template:
            return None
        
        # Authorization: system templates are public, user templates are private
        if not template.is_system_template and template.user_id != user_id:
            return None
        
        return self._to_profile_response(template)
    
    async def create_profile(
        self, 
        user_id: uuid.UUID, 
        data: ProfileCreate,
    ) -> ProfileResponse:
        """Create a new profile with criteria.
        
        Creates a user-owned profile (not a system template).
        
        Args:
            user_id: Current user's UUID (will own the profile).
            data: Profile creation data with criteria.
            
        Returns:
            Created ProfileResponse with all criteria.
        
        Example:
            >>> profile = await service.create_profile(
            ...     user_id,
            ...     ProfileCreate(
            ...         name="Backend Developer",
            ...         passing_score=70,
            ...         criteria=[CriterionCreate(name="Python", max_points=20)],
            ...     )
            ... )
        """
        # Create template entity
        template = EvaluationTemplate(
            user_id=user_id,
            name=data.name,
            description=data.description,
            is_system_template=False,
            passing_score=data.passing_score,
            minimum_criteria_met=data.minimum_criteria_met,
        )
        
        # Add criteria entities
        for idx, criterion_data in enumerate(data.criteria):
            criterion = TemplateCriterion(
                name=criterion_data.name,
                description=criterion_data.description,
                max_points=criterion_data.max_points,
                keywords=criterion_data.keywords,
                evaluation_guidelines=criterion_data.evaluation_guidelines,
                is_required=criterion_data.is_required,
                sort_order=criterion_data.sort_order or idx,
            )
            template.criteria.append(criterion)
        
        # Persist to database
        created = await self.repo.create(template)
        
        # Reload with criteria for response
        template = await self.repo.get_with_criteria(created.id)
        
        logger.info(f"Created profile '{data.name}' for user {user_id}")
        
        return self._to_profile_response(template)
    
    async def update_profile(
        self,
        profile_id: uuid.UUID,
        user_id: uuid.UUID,
        data: ProfileUpdate,
    ) -> Optional[ProfileResponse]:
        """Update a profile's metadata.
        
        Only updates profile fields, not criteria. Use criterion
        methods to update individual criteria.
        
        Args:
            profile_id: Profile UUID to update.
            user_id: Current user's UUID for authorization.
            data: Fields to update (partial update).
            
        Returns:
            Updated ProfileResponse or None if not found/unauthorized.
            
        Raises:
            ValueError: If attempting to update a system template.
        
        Example:
            >>> profile = await service.update_profile(
            ...     profile_id,
            ...     user_id,
            ...     ProfileUpdate(passing_score=75),
            ... )
        """
        template = await self.repo.get_with_criteria(profile_id)
        
        if not template:
            return None
        
        # Cannot modify system templates
        if template.is_system_template:
            raise ValueError("Cannot update system templates")
        
        # Must be owner
        if template.user_id != user_id:
            return None
        
        # Apply partial update
        if data.name is not None:
            template.name = data.name
        if data.description is not None:
            template.description = data.description
        if data.passing_score is not None:
            template.passing_score = data.passing_score
        if data.minimum_criteria_met is not None:
            template.minimum_criteria_met = data.minimum_criteria_met
        
        await self.repo.update(template)
        
        # Reload with criteria for response (refresh doesn't load relationships)
        template = await self.repo.get_with_criteria(profile_id)
        
        logger.info(f"Updated profile {profile_id}")
        
        return self._to_profile_response(template)
    
    async def delete_profile(
        self,
        profile_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete a user-owned profile.
        
        Args:
            profile_id: Profile UUID to delete.
            user_id: Current user's UUID for authorization.
            
        Returns:
            True if deleted, False if not found/unauthorized.
            
        Raises:
            ValueError: If attempting to delete a system template.
        
        Example:
            >>> deleted = await service.delete_profile(profile_id, user_id)
            >>> if deleted:
            ...     print("Profile deleted")
        """
        template = await self.repo.get_by_id(profile_id)
        
        if not template:
            return False
        
        if template.is_system_template:
            raise ValueError("Cannot delete system templates")
        
        if template.user_id != user_id:
            return False
        
        await self.repo.delete(template)
        
        logger.info(f"Deleted profile {profile_id}")
        
        return True
    
    async def clone_profile(
        self,
        source_id: uuid.UUID,
        user_id: uuid.UUID,
        new_name: str,
        description: Optional[str] = None,
    ) -> Optional[ProfileResponse]:
        """Clone a profile to create a custom copy.
        
        Users can clone system templates or their own profiles.
        The clone is always a user-owned profile.
        
        Args:
            source_id: Source profile UUID to clone.
            user_id: Current user's UUID (will own the clone).
            new_name: Name for the cloned profile.
            description: Optional new description (uses source if None).
            
        Returns:
            Cloned ProfileResponse or None if source not found/unauthorized.
        
        Example:
            >>> cloned = await service.clone_profile(
            ...     source_id=system_template_id,
            ...     user_id=user_id,
            ...     new_name="My Custom Profile",
            ... )
        """
        source = await self.repo.get_with_criteria(source_id)
        
        if not source:
            return None
        
        # Authorization: can clone system templates or own profiles
        if not source.is_system_template and source.user_id != user_id:
            return None
        
        # Create new template (always user-owned)
        template = EvaluationTemplate(
            user_id=user_id,
            name=new_name,
            description=description or source.description,
            is_system_template=False,
            passing_score=source.passing_score,
            minimum_criteria_met=source.minimum_criteria_met,
        )
        
        # Clone all criteria
        for criterion in source.criteria:
            new_criterion = TemplateCriterion(
                name=criterion.name,
                description=criterion.description,
                max_points=criterion.max_points,
                keywords=criterion.keywords,
                evaluation_guidelines=criterion.evaluation_guidelines,
                is_required=criterion.is_required,
                sort_order=criterion.sort_order,
            )
            template.criteria.append(new_criterion)
        
        created = await self.repo.create(template)
        template = await self.repo.get_with_criteria(created.id)
        
        logger.info(f"Cloned profile {source_id} to '{new_name}' for user {user_id}")
        
        return self._to_profile_response(template)
    
    # =========================================================================
    # Criterion CRUD
    # =========================================================================
    
    async def add_criterion(
        self,
        profile_id: uuid.UUID,
        user_id: uuid.UUID,
        data: CriterionCreate,
    ) -> Optional[CriterionResponse]:
        """Add a criterion to a profile.
        
        Args:
            profile_id: Profile UUID to add criterion to.
            user_id: Current user's UUID for authorization.
            data: Criterion creation data.
            
        Returns:
            Created CriterionResponse or None if profile not found/unauthorized.
        
        Example:
            >>> criterion = await service.add_criterion(
            ...     profile_id,
            ...     user_id,
            ...     CriterionCreate(name="Docker", max_points=10),
            ... )
        """
        template = await self.repo.get_by_id(profile_id)
        
        if not template or template.is_system_template or template.user_id != user_id:
            return None
        
        criterion = TemplateCriterion(
            template_id=profile_id,
            name=data.name,
            description=data.description,
            max_points=data.max_points,
            keywords=data.keywords,
            evaluation_guidelines=data.evaluation_guidelines,
            is_required=data.is_required,
            sort_order=data.sort_order,
        )
        
        created = await self.repo.add_criterion(criterion)
        
        return CriterionResponse(
            id=created.id,
            template_id=created.template_id,
            name=created.name,
            description=created.description,
            max_points=created.max_points,
            keywords=created.keywords or [],
            evaluation_guidelines=created.evaluation_guidelines,
            is_required=created.is_required,
            sort_order=created.sort_order,
        )
    
    async def update_criterion(
        self,
        profile_id: uuid.UUID,
        criterion_id: uuid.UUID,
        user_id: uuid.UUID,
        data: CriterionUpdate,
    ) -> Optional[CriterionResponse]:
        """Update a criterion in a profile.
        
        Args:
            profile_id: Parent profile UUID for authorization.
            criterion_id: Criterion UUID to update.
            user_id: Current user's UUID for authorization.
            data: Fields to update (partial update).
            
        Returns:
            Updated CriterionResponse or None if not found/unauthorized.
        
        Example:
            >>> criterion = await service.update_criterion(
            ...     profile_id,
            ...     criterion_id,
            ...     user_id,
            ...     CriterionUpdate(max_points=25),
            ... )
        """
        template = await self.repo.get_by_id(profile_id)
        
        if not template or template.is_system_template or template.user_id != user_id:
            return None
        
        criterion = await self.repo.get_criterion_by_id(criterion_id)
        
        if not criterion or criterion.template_id != profile_id:
            return None
        
        # Apply partial update
        if data.name is not None:
            criterion.name = data.name
        if data.description is not None:
            criterion.description = data.description
        if data.max_points is not None:
            criterion.max_points = data.max_points
        if data.keywords is not None:
            criterion.keywords = data.keywords
        if data.evaluation_guidelines is not None:
            criterion.evaluation_guidelines = data.evaluation_guidelines
        if data.is_required is not None:
            criterion.is_required = data.is_required
        if data.sort_order is not None:
            criterion.sort_order = data.sort_order
        
        await self.repo.update_criterion(criterion)
        
        return CriterionResponse(
            id=criterion.id,
            template_id=criterion.template_id,
            name=criterion.name,
            description=criterion.description,
            max_points=criterion.max_points,
            keywords=criterion.keywords or [],
            evaluation_guidelines=criterion.evaluation_guidelines,
            is_required=criterion.is_required,
            sort_order=criterion.sort_order,
        )
    
    async def delete_criterion(
        self,
        profile_id: uuid.UUID,
        criterion_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete a criterion from a profile.
        
        Args:
            profile_id: Parent profile UUID for authorization.
            criterion_id: Criterion UUID to delete.
            user_id: Current user's UUID for authorization.
            
        Returns:
            True if deleted, False if not found/unauthorized.
        
        Example:
            >>> deleted = await service.delete_criterion(
            ...     profile_id, criterion_id, user_id
            ... )
        """
        template = await self.repo.get_by_id(profile_id)
        
        if not template or template.is_system_template or template.user_id != user_id:
            return False
        
        criterion = await self.repo.get_criterion_by_id(criterion_id)
        
        if not criterion or criterion.template_id != profile_id:
            return False
        
        await self.repo.delete_criterion(criterion)
        
        return True
    
    # =========================================================================
    # Helpers
    # =========================================================================
    
    def _to_profile_response(self, template: EvaluationTemplate) -> ProfileResponse:
        """Convert template entity to ProfileResponse schema.
        
        Args:
            template: EvaluationTemplate entity with criteria loaded.
            
        Returns:
            ProfileResponse with all fields populated.
        """
        return ProfileResponse(
            id=template.id,
            user_id=template.user_id,
            name=template.name,
            description=template.description,
            is_system_template=template.is_system_template,
            passing_score=template.passing_score,
            minimum_criteria_met=template.minimum_criteria_met,
            criteria=[
                CriterionResponse(
                    id=c.id,
                    template_id=c.template_id,
                    name=c.name,
                    description=c.description,
                    max_points=c.max_points,
                    keywords=c.keywords or [],
                    evaluation_guidelines=c.evaluation_guidelines,
                    is_required=c.is_required,
                    sort_order=c.sort_order,
                )
                for c in template.criteria
            ],
        )
