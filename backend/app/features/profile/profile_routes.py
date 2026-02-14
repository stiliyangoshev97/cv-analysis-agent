"""Hiring Profile feature route definitions.

This module defines the FastAPI routes for evaluation profile CRUD.
Routes are thin - they only wire dependencies and delegate to controllers.

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

from fastapi import APIRouter

from .profile_controller import ProfileController
from .profile_schemas import (
    ProfileResponse,
    ProfileListResponse,
    CriterionResponse,
)

router = APIRouter(tags=["Profiles"])


# =============================================================================
# Profile CRUD Routes
# =============================================================================

router.add_api_route(
    "/",
    ProfileController.list_profiles,
    methods=["GET"],
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

router.add_api_route(
    "/{profile_id}",
    ProfileController.get_profile,
    methods=["GET"],
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

router.add_api_route(
    "/",
    ProfileController.create_profile,
    methods=["POST"],
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

router.add_api_route(
    "/{profile_id}",
    ProfileController.update_profile,
    methods=["PUT"],
    response_model=ProfileResponse,
    summary="Update profile",
    description="""
    Update profile metadata (name, description, passing_score).
    
    **Note**: This endpoint updates profile-level settings only.
    To update individual criteria, use the criterion endpoints.
    
    **Authorization**: Can only update own profiles, not system templates.
    """,
)

router.add_api_route(
    "/{profile_id}",
    ProfileController.delete_profile,
    methods=["DELETE"],
    summary="Delete profile",
    description="""
    Delete a user-created profile.
    
    **Warning**: This action is irreversible. All associated
    criteria will also be deleted.
    
    **Authorization**: Can only delete own profiles.
    System templates cannot be deleted.
    """,
)

router.add_api_route(
    "/{profile_id}/clone",
    ProfileController.clone_profile,
    methods=["POST"],
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


# =============================================================================
# Criterion CRUD Routes
# =============================================================================

router.add_api_route(
    "/{profile_id}/criteria",
    ProfileController.add_criterion,
    methods=["POST"],
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

router.add_api_route(
    "/{profile_id}/criteria/{criterion_id}",
    ProfileController.update_criterion,
    methods=["PUT"],
    response_model=CriterionResponse,
    summary="Update criterion",
    description="""
    Update a criterion in a profile.
    
    Partial updates are supported - only provide fields to change.
    
    **Authorization**: Can only update criteria in own profiles.
    """,
)

router.add_api_route(
    "/{profile_id}/criteria/{criterion_id}",
    ProfileController.delete_criterion,
    methods=["DELETE"],
    summary="Delete criterion",
    description="""
    Delete a criterion from a profile.
    
    **Warning**: This action is irreversible.
    
    **Authorization**: Can only delete criteria from own profiles.
    """,
)
