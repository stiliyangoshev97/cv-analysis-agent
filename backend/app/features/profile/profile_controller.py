"""Hiring Profile controller for HTTP request handling.

This module provides the ProfileController class for handling HTTP
requests related to evaluation profiles. Controllers handle request
parsing, response formatting, and error handling.

Classes:
    ProfileController: HTTP handlers for profile endpoints.

Example:
    Using the controller in routes::
    
        router.add_api_route(
            "/",
            ProfileController.list_profiles,
            methods=["GET"],
            response_model=ProfileListResponse,
        )
"""

import uuid
import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.db.models.user import User
from app.features.auth.auth_dependencies import get_current_user
from .profile_service import ProfileService
from .profile_schemas import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
    ProfileListResponse,
    CloneProfileRequest,
    CriterionCreate,
    CriterionUpdate,
    CriterionResponse,
)

logger = logging.getLogger(__name__)


class ProfileController:
    """Controller for profile HTTP endpoints.
    
    Handles request validation, calls ProfileService, and formats responses.
    All methods are static as they don't maintain state.
    
    Methods handle:
        - Dependency injection via FastAPI's Depends
        - Authorization via current_user
        - Error handling (404, 403)
        - Response formatting
    
    Example:
        >>> response = await ProfileController.list_profiles(
        ...     db=session,
        ...     current_user=user,
        ... )
    """
    
    # =========================================================================
    # Profile Endpoints
    # =========================================================================
    
    @staticmethod
    async def list_profiles(
        db: Annotated[AsyncSession, Depends(get_async_session)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> ProfileListResponse:
        """Handle GET /api/profiles/ - List all available profiles.
        
        Returns system templates and user-created profiles.
        
        Args:
            db: Database session (injected).
            current_user: Authenticated user (injected).
            
        Returns:
            ProfileListResponse with profile summaries.
        """
        service = ProfileService(db)
        return await service.list_profiles(current_user.id)
    
    @staticmethod
    async def get_profile(
        profile_id: uuid.UUID,
        db: Annotated[AsyncSession, Depends(get_async_session)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> ProfileResponse:
        """Handle GET /api/profiles/{profile_id} - Get profile by ID.
        
        Args:
            profile_id: Profile UUID from path.
            db: Database session (injected).
            current_user: Authenticated user (injected).
            
        Returns:
            ProfileResponse with full criteria.
            
        Raises:
            HTTPException: 404 if profile not found or unauthorized.
        """
        service = ProfileService(db)
        profile = await service.get_profile(profile_id, current_user.id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )
        
        return profile
    
    @staticmethod
    async def create_profile(
        data: ProfileCreate,
        db: Annotated[AsyncSession, Depends(get_async_session)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> ProfileResponse:
        """Handle POST /api/profiles/ - Create a new profile.
        
        Args:
            data: Profile creation data with criteria.
            db: Database session (injected).
            current_user: Authenticated user (injected).
            
        Returns:
            Created ProfileResponse with 201 status.
        """
        service = ProfileService(db)
        return await service.create_profile(current_user.id, data)
    
    @staticmethod
    async def update_profile(
        profile_id: uuid.UUID,
        data: ProfileUpdate,
        db: Annotated[AsyncSession, Depends(get_async_session)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> ProfileResponse:
        """Handle PUT /api/profiles/{profile_id} - Update a profile.
        
        Args:
            profile_id: Profile UUID from path.
            data: Fields to update.
            db: Database session (injected).
            current_user: Authenticated user (injected).
            
        Returns:
            Updated ProfileResponse.
            
        Raises:
            HTTPException: 404 if not found, 403 if system template.
        """
        service = ProfileService(db)
        
        try:
            profile = await service.update_profile(profile_id, current_user.id, data)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )
        
        return profile
    
    @staticmethod
    async def delete_profile(
        profile_id: uuid.UUID,
        db: Annotated[AsyncSession, Depends(get_async_session)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> dict:
        """Handle DELETE /api/profiles/{profile_id} - Delete a profile.
        
        Args:
            profile_id: Profile UUID from path.
            db: Database session (injected).
            current_user: Authenticated user (injected).
            
        Returns:
            Success message dict.
            
        Raises:
            HTTPException: 404 if not found, 403 if system template.
        """
        service = ProfileService(db)
        
        try:
            deleted = await service.delete_profile(profile_id, current_user.id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )
        
        return {"message": "Profile deleted successfully"}
    
    @staticmethod
    async def clone_profile(
        profile_id: uuid.UUID,
        data: CloneProfileRequest,
        db: Annotated[AsyncSession, Depends(get_async_session)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> ProfileResponse:
        """Handle POST /api/profiles/{profile_id}/clone - Clone a profile.
        
        Clone any accessible profile (system or own) to create a custom copy.
        
        Args:
            profile_id: Source profile UUID from path.
            data: Clone request with new name.
            db: Database session (injected).
            current_user: Authenticated user (injected).
            
        Returns:
            Cloned ProfileResponse with 201 status.
            
        Raises:
            HTTPException: 404 if source profile not found.
        """
        service = ProfileService(db)
        profile = await service.clone_profile(
            source_id=profile_id,
            user_id=current_user.id,
            new_name=data.new_name,
            description=data.description,
        )
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source profile not found",
            )
        
        return profile
    
    # =========================================================================
    # Criterion Endpoints
    # =========================================================================
    
    @staticmethod
    async def add_criterion(
        profile_id: uuid.UUID,
        data: CriterionCreate,
        db: Annotated[AsyncSession, Depends(get_async_session)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> CriterionResponse:
        """Handle POST /api/profiles/{profile_id}/criteria - Add criterion.
        
        Args:
            profile_id: Profile UUID from path.
            data: Criterion creation data.
            db: Database session (injected).
            current_user: Authenticated user (injected).
            
        Returns:
            Created CriterionResponse with 201 status.
            
        Raises:
            HTTPException: 404 if profile not found or unauthorized.
        """
        service = ProfileService(db)
        criterion = await service.add_criterion(profile_id, current_user.id, data)
        
        if not criterion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found or cannot be modified",
            )
        
        return criterion
    
    @staticmethod
    async def update_criterion(
        profile_id: uuid.UUID,
        criterion_id: uuid.UUID,
        data: CriterionUpdate,
        db: Annotated[AsyncSession, Depends(get_async_session)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> CriterionResponse:
        """Handle PUT /api/profiles/{profile_id}/criteria/{criterion_id} - Update criterion.
        
        Args:
            profile_id: Profile UUID from path.
            criterion_id: Criterion UUID from path.
            data: Fields to update.
            db: Database session (injected).
            current_user: Authenticated user (injected).
            
        Returns:
            Updated CriterionResponse.
            
        Raises:
            HTTPException: 404 if criterion not found or unauthorized.
        """
        service = ProfileService(db)
        criterion = await service.update_criterion(
            profile_id, criterion_id, current_user.id, data
        )
        
        if not criterion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Criterion not found or cannot be modified",
            )
        
        return criterion
    
    @staticmethod
    async def delete_criterion(
        profile_id: uuid.UUID,
        criterion_id: uuid.UUID,
        db: Annotated[AsyncSession, Depends(get_async_session)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> dict:
        """Handle DELETE /api/profiles/{profile_id}/criteria/{criterion_id} - Delete criterion.
        
        Args:
            profile_id: Profile UUID from path.
            criterion_id: Criterion UUID from path.
            db: Database session (injected).
            current_user: Authenticated user (injected).
            
        Returns:
            Success message dict.
            
        Raises:
            HTTPException: 404 if criterion not found or unauthorized.
        """
        service = ProfileService(db)
        deleted = await service.delete_criterion(
            profile_id, criterion_id, current_user.id
        )
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Criterion not found or cannot be deleted",
            )
        
        return {"message": "Criterion deleted successfully"}
