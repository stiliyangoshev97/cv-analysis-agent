"""Hiring Profile feature module.

This module provides CRUD operations for user-defined evaluation profiles
(templates) used to score CVs against custom criteria. Users can create
their own profiles or clone system templates as starting points.

Architecture (Controller-Service-Repository Pattern):
    - profile_routes.py: Route definitions (thin)
    - profile_controller.py: HTTP request/response handling
    - profile_service.py: Business logic with authorization
    - profile_schemas.py: Pydantic validation schemas
    - Uses cv/template_repository.py: Database operations (shared)

Features:
    - List system and user-created profiles
    - Create custom evaluation profiles with criteria
    - Clone system templates to create personalized versions
    - Update profile metadata and criteria
    - Delete user-created profiles

Exports:
    profile_router: FastAPI router with profile endpoints.
    ProfileService: Business logic for profile operations.

Example:
    The router is registered in main.py::
    
        from app.features.profile import profile_router
        app.include_router(profile_router, prefix="/api/profiles", tags=["profiles"])
"""

from .profile_routes import router as profile_router
from .profile_service import ProfileService
from .profile_schemas import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
    ProfileSummary,
    ProfileListResponse,
    CriterionCreate,
    CriterionUpdate,
    CriterionResponse,
    CloneProfileRequest,
)

__all__ = [
    # Router
    "profile_router",
    # Services
    "ProfileService",
    # Schemas
    "ProfileCreate",
    "ProfileUpdate",
    "ProfileResponse",
    "ProfileSummary",
    "ProfileListResponse",
    "CriterionCreate",
    "CriterionUpdate",
    "CriterionResponse",
    "CloneProfileRequest",
]
