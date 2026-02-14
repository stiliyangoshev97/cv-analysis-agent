"""Hiring Profile feature route definitions.

This module defines the FastAPI routes for evaluation profile CRUD.
Routes are thin - they only wire dependencies and delegate to controllers.

Rate Limits:
    - All profile endpoints: 100/minute (standard authenticated)

Routes:
    GET    /api/profiles/                          - List all profiles
    GET    /api/profiles/{id}                      - Get profile with criteria
    POST   /api/profiles/                          - Create new profile
    PUT    /api/profiles/{id}                      - Update profile metadata
    DELETE /api/profiles/{id}                      - Delete user profile
    POST   /api/profiles/{id}/clone                - Clone a profile
    POST   /api/profiles/{id}/criteria             - Add criterion
    PUT    /api/profiles/{id}/criteria/{cid}       - Update criterion
    DELETE /api/profiles/{id}/criteria/{cid}       - Delete criterion

Example:
    The router is registered in main.py::
    
        from app.features.profile import profile_router
        app.include_router(profile_router, prefix="/api/profiles", tags=["profiles"])
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.db.models.user import User
from app.features.auth.auth_dependencies import get_current_user
from app.core.rate_limit import limiter, RATE_LIMIT_DEFAULT
from .profile_controller import ProfileController
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

router = APIRouter(tags=["Profiles"])


# =============================================================================
# Profile CRUD Routes
# =============================================================================

@router.get(
    "/",
    response_model=ProfileListResponse,
    summary="List profiles",
    description="""
    List all evaluation profiles available to the user.
    
    Returns:
    - **System templates**: Built-in profiles available to all users
    - **User profiles**: Custom profiles created by the current user
    
    Each profile summary includes criteria count for quick overview.
    """,
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def list_profiles(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProfileListResponse:
    """List all profiles."""
    return await ProfileController.list_profiles(db=db, current_user=current_user)


@router.get(
    "/{profile_id}",
    response_model=ProfileResponse,
    summary="Get profile",
    description="""
    Get a profile by ID with all evaluation criteria.
    
    Returns full profile details including:
    - Profile metadata (name, passing_score, etc.)
    - Complete list of evaluation criteria with scoring rules
    
    **Authorization**: Can view system templates or own profiles only.
    """,
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_profile(
    request: Request,
    profile_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProfileResponse:
    """Get profile by ID."""
    return await ProfileController.get_profile(
        profile_id=profile_id, db=db, current_user=current_user
    )


@router.post(
    "/",
    response_model=ProfileResponse,
    status_code=201,
    summary="Create profile",
    description="""
    Create a new evaluation profile with criteria.
    
    **Required**: At least one criterion must be provided.
    
    The profile will be owned by the current user and can be
    modified or deleted later. System templates cannot be created
    via this endpoint.
    """,
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def create_profile(
    request: Request,
    data: ProfileCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProfileResponse:
    """Create new profile."""
    return await ProfileController.create_profile(
        data=data, db=db, current_user=current_user
    )


@router.put(
    "/{profile_id}",
    response_model=ProfileResponse,
    summary="Update profile",
    description="""
    Update profile metadata (name, description, passing_score).
    
    **Note**: This endpoint updates profile-level settings only.
    To update individual criteria, use the criterion endpoints.
    
    **Authorization**: Can only update own profiles, not system templates.
    """,
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def update_profile(
    request: Request,
    profile_id: uuid.UUID,
    data: ProfileUpdate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProfileResponse:
    """Update profile."""
    return await ProfileController.update_profile(
        profile_id=profile_id, data=data, db=db, current_user=current_user
    )


@router.delete(
    "/{profile_id}",
    summary="Delete profile",
    description="""
    Delete a user-created profile.
    
    **Warning**: This action is irreversible. All associated
    criteria will also be deleted.
    
    **Authorization**: Can only delete own profiles.
    System templates cannot be deleted.
    """,
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def delete_profile(
    request: Request,
    profile_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Delete profile."""
    return await ProfileController.delete_profile(
        profile_id=profile_id, db=db, current_user=current_user
    )


@router.post(
    "/{profile_id}/clone",
    response_model=ProfileResponse,
    status_code=201,
    summary="Clone profile",
    description="""
    Clone a profile to create a custom copy.
    
    **Use cases**:
    - Clone a system template to customize it
    - Duplicate your own profile with a new name
    
    The cloned profile will be owned by the current user
    and can be freely modified.
    """,
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def clone_profile(
    request: Request,
    profile_id: uuid.UUID,
    data: CloneProfileRequest,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProfileResponse:
    """Clone profile."""
    return await ProfileController.clone_profile(
        profile_id=profile_id, data=data, db=db, current_user=current_user
    )


# =============================================================================
# Criterion CRUD Routes
# =============================================================================

@router.post(
    "/{profile_id}/criteria",
    response_model=CriterionResponse,
    status_code=201,
    summary="Add criterion",
    description="""
    Add a new evaluation criterion to a profile.
    
    Each criterion defines:
    - Name and description
    - Maximum points (weight)
    - Keywords for AI recognition
    - Evaluation guidelines
    
    **Authorization**: Can only add to own profiles.
    """,
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def add_criterion(
    request: Request,
    profile_id: uuid.UUID,
    data: CriterionCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CriterionResponse:
    """Add criterion to profile."""
    return await ProfileController.add_criterion(
        profile_id=profile_id, data=data, db=db, current_user=current_user
    )


@router.put(
    "/{profile_id}/criteria/{criterion_id}",
    response_model=CriterionResponse,
    summary="Update criterion",
    description="""
    Update a criterion in a profile.
    
    Partial updates are supported - only provide fields to change.
    
    **Authorization**: Can only update criteria in own profiles.
    """,
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def update_criterion(
    request: Request,
    profile_id: uuid.UUID,
    criterion_id: uuid.UUID,
    data: CriterionUpdate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CriterionResponse:
    """Update criterion."""
    return await ProfileController.update_criterion(
        profile_id=profile_id,
        criterion_id=criterion_id,
        data=data,
        db=db,
        current_user=current_user,
    )


@router.delete(
    "/{profile_id}/criteria/{criterion_id}",
    summary="Delete criterion",
    description="""
    Delete a criterion from a profile.
    
    **Warning**: This action is irreversible.
    
    **Authorization**: Can only delete criteria from own profiles.
    """,
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def delete_criterion(
    request: Request,
    profile_id: uuid.UUID,
    criterion_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Delete criterion from profile."""
    return await ProfileController.delete_criterion(
        profile_id=profile_id, criterion_id=criterion_id, db=db, current_user=current_user
    )
