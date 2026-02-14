"""Hiring Profile feature Pydantic schemas.

This module defines request and response models for the profile endpoints.
All schemas use Pydantic for validation and serialization.

Schemas:
    CriterionCreate: Request body for creating a criterion.
    CriterionUpdate: Request body for updating a criterion.
    CriterionResponse: Single criterion in a response.
    ProfileCreate: Request body for creating a profile with criteria.
    ProfileUpdate: Request body for updating profile metadata.
    ProfileSummary: Abbreviated profile for list views.
    ProfileResponse: Full profile with criteria for detail views.
    ProfileListResponse: Paginated list of profiles.
    CloneProfileRequest: Request body for cloning a profile.

Example:
    Creating a profile::
    
        from .profile_schemas import ProfileCreate, CriterionCreate
        
        profile = ProfileCreate(
            name="Backend Developer",
            passing_score=70,
            criteria=[
                CriterionCreate(name="Python", max_points=20),
                CriterionCreate(name="SQL", max_points=15),
            ]
        )
"""

import uuid
from typing import Optional
from pydantic import BaseModel, Field


# =============================================================================
# Criterion Schemas
# =============================================================================

class CriterionBase(BaseModel):
    """Base schema for criterion fields.
    
    Attributes:
        name: Criterion name (e.g., "Python Experience").
        description: Detailed description of what to evaluate.
        max_points: Maximum points for this criterion (1-100).
        keywords: AI hints for recognizing this skill.
        evaluation_guidelines: Instructions for scoring.
        is_required: Whether this criterion must be met to pass.
        sort_order: Display order in the profile.
    
    Example:
        >>> criterion = CriterionBase(
        ...     name="Python Experience",
        ...     description="Evaluate proficiency in Python programming",
        ...     max_points=20,
        ...     keywords=["python", "django", "fastapi"],
        ...     is_required=True,
        ... )
    """
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Criterion name"
    )
    description: Optional[str] = Field(
        None, 
        description="Detailed description for evaluation"
    )
    max_points: int = Field(
        ..., 
        ge=1, 
        le=100, 
        description="Maximum points for this criterion (1-100)"
    )
    keywords: Optional[list[str]] = Field(
        default_factory=list, 
        description="Keywords for AI to identify this skill"
    )
    evaluation_guidelines: Optional[str] = Field(
        None, 
        description="Detailed instructions for scoring"
    )
    is_required: bool = Field(
        False, 
        description="Whether criterion must be met to pass"
    )
    sort_order: int = Field(
        0, 
        ge=0, 
        description="Display order (0 = first)"
    )


class CriterionCreate(CriterionBase):
    """Request body for creating a new criterion.
    
    Inherits all fields from CriterionBase.
    Used when creating a profile or adding criteria.
    
    Example:
        >>> criterion = CriterionCreate(
        ...     name="Python",
        ...     max_points=20,
        ...     is_required=True,
        ... )
    """
    pass


class CriterionUpdate(BaseModel):
    """Request body for updating a criterion.
    
    All fields are optional - only provided fields are updated.
    
    Attributes:
        name: New criterion name.
        description: New description.
        max_points: New max points.
        keywords: New keyword list.
        evaluation_guidelines: New guidelines.
        is_required: New required status.
        sort_order: New display order.
    
    Example:
        >>> update = CriterionUpdate(max_points=25)
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    max_points: Optional[int] = Field(None, ge=1, le=100)
    keywords: Optional[list[str]] = None
    evaluation_guidelines: Optional[str] = None
    is_required: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)


class CriterionResponse(CriterionBase):
    """Single criterion in API responses.
    
    Attributes:
        id: Unique criterion identifier.
        template_id: Parent profile/template UUID.
        (plus all CriterionBase fields)
    
    Example:
        >>> # Returned from API
        >>> print(criterion.id, criterion.name, criterion.max_points)
    """
    id: uuid.UUID = Field(description="Criterion UUID")
    template_id: uuid.UUID = Field(description="Parent profile UUID")

    model_config = {"from_attributes": True}


# =============================================================================
# Profile (Template) Schemas
# =============================================================================

class ProfileBase(BaseModel):
    """Base schema for profile fields.
    
    Attributes:
        name: Profile name (e.g., "Senior Backend Developer").
        description: Description of the ideal candidate.
        passing_score: Minimum total score to pass (0-100).
        minimum_criteria_met: Minimum number of criteria to meet.
    
    Example:
        >>> profile = ProfileBase(
        ...     name="Backend Developer",
        ...     description="Ideal candidate for backend role",
        ...     passing_score=70,
        ...     minimum_criteria_met=3,
        ... )
    """
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Profile name"
    )
    description: Optional[str] = Field(
        None, 
        description="Profile description"
    )
    passing_score: int = Field(
        60, 
        ge=0, 
        le=100, 
        description="Minimum score to pass (0-100)"
    )
    minimum_criteria_met: int = Field(
        3, 
        ge=0, 
        description="Minimum number of criteria that must be met"
    )


class ProfileCreate(ProfileBase):
    """Request body for creating a new profile with criteria.
    
    Requires at least one criterion to be provided.
    
    Attributes:
        criteria: List of criteria to create with the profile.
    
    Example:
        >>> profile = ProfileCreate(
        ...     name="Backend Developer",
        ...     passing_score=70,
        ...     criteria=[
        ...         CriterionCreate(name="Python", max_points=20),
        ...         CriterionCreate(name="SQL", max_points=15),
        ...     ]
        ... )
    """
    criteria: list[CriterionCreate] = Field(
        ..., 
        min_length=1, 
        description="Evaluation criteria (at least 1 required)"
    )


class ProfileUpdate(BaseModel):
    """Request body for updating a profile.
    
    All fields are optional - only provided fields are updated.
    Does NOT update criteria - use criterion endpoints for that.
    
    Example:
        >>> update = ProfileUpdate(passing_score=75)
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    passing_score: Optional[int] = Field(None, ge=0, le=100)
    minimum_criteria_met: Optional[int] = Field(None, ge=0)


class ProfileSummary(BaseModel):
    """Abbreviated profile for list views.
    
    Attributes:
        id: Profile UUID.
        name: Profile name.
        description: Brief description.
        is_system_template: Whether this is a built-in template.
        passing_score: Required score to pass.
        criteria_count: Number of criteria in this profile.
    
    Example:
        >>> for profile in response.profiles:
        ...     print(f"{profile.name}: {profile.criteria_count} criteria")
    """
    id: uuid.UUID = Field(description="Profile UUID")
    name: str = Field(description="Profile name")
    description: Optional[str] = Field(description="Profile description")
    is_system_template: bool = Field(description="True if built-in template")
    passing_score: int = Field(description="Minimum passing score")
    criteria_count: int = Field(description="Number of criteria")

    model_config = {"from_attributes": True}


class ProfileResponse(ProfileBase):
    """Full profile response with all criteria.
    
    Returned when getting a single profile or after create/update.
    
    Attributes:
        id: Profile UUID.
        user_id: Owner's user ID (None for system templates).
        is_system_template: Whether this is a built-in template.
        criteria: Full list of evaluation criteria.
    
    Example:
        >>> profile = await api.get_profile(profile_id)
        >>> for criterion in profile.criteria:
        ...     print(f"  {criterion.name}: {criterion.max_points} pts")
    """
    id: uuid.UUID = Field(description="Profile UUID")
    user_id: Optional[uuid.UUID] = Field(description="Owner user ID (None for system)")
    is_system_template: bool = Field(description="True if built-in template")
    criteria: list[CriterionResponse] = Field(description="Evaluation criteria")

    model_config = {"from_attributes": True}


class ProfileListResponse(BaseModel):
    """Response for listing profiles.
    
    Attributes:
        profiles: List of profile summaries.
        total: Total number of profiles.
    
    Example:
        >>> response = await api.list_profiles()
        >>> print(f"Found {response.total} profiles")
    """
    profiles: list[ProfileSummary] = Field(description="Profile summaries")
    total: int = Field(description="Total count")


class CloneProfileRequest(BaseModel):
    """Request body for cloning a profile.
    
    Clone any accessible profile (system or own) to create a custom copy.
    
    Attributes:
        new_name: Name for the cloned profile.
        description: Optional new description (uses source if not provided).
    
    Example:
        >>> request = CloneProfileRequest(
        ...     new_name="My Backend Profile",
        ...     description="Customized for our team",
        ... )
    """
    new_name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Name for the cloned profile"
    )
    description: Optional[str] = Field(
        None, 
        description="New description (uses source description if not provided)"
    )
