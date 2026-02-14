"""Unit tests for ProfileService.

Tests for hiring profile management including:
    - Listing profiles (system + user)
    - Creating user profiles
    - Updating profiles
    - Cloning system templates
    - Managing criteria

Run with: pytest app/tests/unit/test_profile_service.py -v
"""

import uuid

import pytest

from app.features.profile.profile_service import ProfileService
from app.features.profile.profile_schemas import (
    ProfileCreate,
    ProfileUpdate,
    CriterionCreate,
    CriterionUpdate,
)


@pytest.mark.asyncio
@pytest.mark.profile
class TestListProfiles:
    """Tests for listing profiles."""
    
    async def test_list_profiles_empty(self, db_session, test_user):
        """Should return ProfileListResponse with empty list when no profiles exist."""
        service = ProfileService(db_session)
        
        response = await service.list_profiles(test_user.id)
        
        assert response.total == 0
        assert response.profiles == []
    
    async def test_list_profiles_includes_system(self, db_session, test_user, system_template):
        """Should include system templates in listing."""
        service = ProfileService(db_session)
        
        response = await service.list_profiles(test_user.id)
        
        assert response.total >= 1
        system_ids = [p.id for p in response.profiles if p.is_system_template]
        assert system_template.id in system_ids
    
    async def test_list_profiles_includes_user(self, db_session, test_user, test_template):
        """Should include user's own templates."""
        service = ProfileService(db_session)
        
        response = await service.list_profiles(test_user.id)
        
        assert response.total >= 1
        profile_ids = [p.id for p in response.profiles]
        assert test_template.id in profile_ids
    
    async def test_list_profiles_excludes_other_users(
        self, db_session, test_user, test_user_2, test_template
    ):
        """Should not include other users' templates."""
        service = ProfileService(db_session)
        
        response = await service.list_profiles(test_user_2.id)
        
        profile_ids = [p.id for p in response.profiles]
        assert test_template.id not in profile_ids


@pytest.mark.asyncio
@pytest.mark.profile
class TestGetProfile:
    """Tests for getting a single profile."""
    
    async def test_get_profile_not_found(self, db_session, test_user):
        """Should return None when profile not found."""
        service = ProfileService(db_session)
        
        profile = await service.get_profile(uuid.uuid4(), test_user.id)
        
        assert profile is None
    
    async def test_get_profile_success(self, db_session, test_user, test_template):
        """Should return profile with criteria."""
        service = ProfileService(db_session)
        
        profile = await service.get_profile(test_template.id, test_user.id)
        
        assert profile is not None
        assert profile.id == test_template.id
        assert profile.name == "Software Engineer"
    
    async def test_get_system_profile(self, db_session, test_user, system_template):
        """Should allow access to system templates."""
        service = ProfileService(db_session)
        
        profile = await service.get_profile(system_template.id, test_user.id)
        
        assert profile is not None
        assert profile.is_system_template is True
    
    async def test_get_other_user_profile_denied(
        self, db_session, test_user_2, test_template
    ):
        """Should return None for other user's profile."""
        service = ProfileService(db_session)
        
        profile = await service.get_profile(test_template.id, test_user_2.id)
        
        assert profile is None


@pytest.mark.asyncio
@pytest.mark.profile
class TestCreateProfile:
    """Tests for creating profiles."""
    
    async def test_create_profile_success(self, db_session, test_user):
        """Should create profile with criteria."""
        service = ProfileService(db_session)
        
        data = ProfileCreate(
            name="Backend Developer",
            description="Evaluate backend developers",
            passing_score=75,
            minimum_criteria_met=2,
            criteria=[
                CriterionCreate(name="Python", max_points=30),
                CriterionCreate(name="SQL", max_points=20),
            ],
        )
        
        profile = await service.create_profile(test_user.id, data)
        
        assert profile is not None
        assert profile.name == "Backend Developer"
        assert profile.passing_score == 75
        assert profile.user_id == test_user.id
        assert profile.is_system_template is False
        assert len(profile.criteria) == 2
    
    async def test_create_profile_default_threshold(self, db_session, test_user):
        """Should use default passing score if not specified."""
        service = ProfileService(db_session)
        
        data = ProfileCreate(
            name="Simple Profile",
            criteria=[CriterionCreate(name="Skill", max_points=100)],
        )
        
        profile = await service.create_profile(test_user.id, data)
        
        assert profile.passing_score == 60
    
    async def test_create_profile_with_criteria_details(self, db_session, test_user):
        """Should create criteria with all fields."""
        service = ProfileService(db_session)
        
        data = ProfileCreate(
            name="Detailed Profile",
            criteria=[
                CriterionCreate(
                    name="Docker",
                    description="Container experience",
                    max_points=15,
                    keywords=["docker", "kubernetes", "containers"],
                    evaluation_guidelines="Look for K8s experience",
                    is_required=True,
                    sort_order=1,
                ),
            ],
        )
        
        profile = await service.create_profile(test_user.id, data)
        
        criterion = profile.criteria[0]
        assert criterion.name == "Docker"
        assert criterion.description == "Container experience"
        assert criterion.max_points == 15
        assert criterion.keywords == ["docker", "kubernetes", "containers"]
        assert criterion.is_required is True


@pytest.mark.asyncio
@pytest.mark.profile
class TestUpdateProfile:
    """Tests for updating profiles."""
    
    async def test_update_profile_success(self, db_session, test_user, test_template):
        """Should update profile fields."""
        service = ProfileService(db_session)
        
        data = ProfileUpdate(
            name="Updated Name",
            passing_score=80,
        )
        
        profile = await service.update_profile(test_template.id, test_user.id, data)
        
        assert profile is not None
        assert profile.name == "Updated Name"
        assert profile.passing_score == 80
    
    async def test_update_profile_partial(self, db_session, test_user, test_template):
        """Should support partial updates."""
        service = ProfileService(db_session)
        
        # Get original profile via service (avoids lazy loading issues)
        original_profile = await service.get_profile(test_template.id, test_user.id)
        original_name = original_profile.name
        
        data = ProfileUpdate(description="New description only")
        
        profile = await service.update_profile(test_template.id, test_user.id, data)
        
        assert profile.name == original_name
        assert profile.description == "New description only"
    
    async def test_update_system_profile_denied(
        self, db_session, test_user, system_template
    ):
        """Should raise error when updating system template."""
        service = ProfileService(db_session)
        
        data = ProfileUpdate(name="Hacked Name")
        
        with pytest.raises(ValueError, match="Cannot update system templates"):
            await service.update_profile(system_template.id, test_user.id, data)
    
    async def test_update_other_user_profile_denied(
        self, db_session, test_user_2, test_template
    ):
        """Should return None when updating other user's profile."""
        service = ProfileService(db_session)
        
        data = ProfileUpdate(name="Hacked Name")
        
        profile = await service.update_profile(test_template.id, test_user_2.id, data)
        
        assert profile is None


@pytest.mark.asyncio
@pytest.mark.profile
class TestDeleteProfile:
    """Tests for deleting profiles."""
    
    async def test_delete_profile_success(self, db_session, test_user, test_template):
        """Should delete profile and return True."""
        service = ProfileService(db_session)
        
        deleted = await service.delete_profile(test_template.id, test_user.id)
        
        assert deleted is True
        
        profile = await service.get_profile(test_template.id, test_user.id)
        assert profile is None
    
    async def test_delete_profile_not_found(self, db_session, test_user):
        """Should return False when profile not found."""
        service = ProfileService(db_session)
        
        deleted = await service.delete_profile(uuid.uuid4(), test_user.id)
        
        assert deleted is False
    
    async def test_delete_system_profile_denied(
        self, db_session, test_user, system_template
    ):
        """Should raise error when deleting system template."""
        service = ProfileService(db_session)
        
        with pytest.raises(ValueError, match="Cannot delete system templates"):
            await service.delete_profile(system_template.id, test_user.id)
    
    async def test_delete_other_user_profile_denied(
        self, db_session, test_user_2, test_template
    ):
        """Should return False when deleting other user's profile."""
        service = ProfileService(db_session)
        
        deleted = await service.delete_profile(test_template.id, test_user_2.id)
        
        assert deleted is False


@pytest.mark.asyncio
@pytest.mark.profile
class TestCloneProfile:
    """Tests for cloning profiles."""
    
    async def test_clone_system_profile(
        self, db_session, test_user, system_template
    ):
        """Should clone system template to user profile."""
        service = ProfileService(db_session)
        
        cloned = await service.clone_profile(
            source_id=system_template.id,
            user_id=test_user.id,
            new_name="My Cloned Profile",
        )
        
        assert cloned is not None
        assert cloned.name == "My Cloned Profile"
        assert cloned.user_id == test_user.id
        assert cloned.is_system_template is False
        assert cloned.id != system_template.id
    
    async def test_clone_preserves_criteria(
        self, db_session, test_user, system_template
    ):
        """Should clone all criteria from source."""
        service = ProfileService(db_session)
        
        cloned = await service.clone_profile(
            source_id=system_template.id,
            user_id=test_user.id,
            new_name="Cloned With Criteria",
        )
        
        source = await service.get_profile(system_template.id, test_user.id)
        assert len(cloned.criteria) == len(source.criteria)
    
    async def test_clone_with_custom_description(
        self, db_session, test_user, system_template
    ):
        """Should allow custom description on clone."""
        service = ProfileService(db_session)
        
        cloned = await service.clone_profile(
            source_id=system_template.id,
            user_id=test_user.id,
            new_name="Custom Clone",
            description="My custom description",
        )
        
        assert cloned.description == "My custom description"
    
    async def test_clone_other_user_profile_denied(
        self, db_session, test_user_2, test_template
    ):
        """Should return None when cloning other user's profile."""
        service = ProfileService(db_session)
        
        cloned = await service.clone_profile(
            source_id=test_template.id,
            user_id=test_user_2.id,
            new_name="Stolen Profile",
        )
        
        assert cloned is None
    
    async def test_clone_not_found(self, db_session, test_user):
        """Should return None when source not found."""
        service = ProfileService(db_session)
        
        cloned = await service.clone_profile(
            source_id=uuid.uuid4(),
            user_id=test_user.id,
            new_name="Ghost Clone",
        )
        
        assert cloned is None


@pytest.mark.asyncio
@pytest.mark.profile
class TestCriteria:
    """Tests for criterion operations."""
    
    async def test_add_criterion(self, db_session, test_user, test_template):
        """Should add criterion to profile."""
        service = ProfileService(db_session)
        
        data = CriterionCreate(
            name="New Skill",
            max_points=15,
        )
        
        criterion = await service.add_criterion(
            profile_id=test_template.id,
            user_id=test_user.id,
            data=data,
        )
        
        assert criterion is not None
        assert criterion.name == "New Skill"
        assert criterion.max_points == 15
        assert criterion.template_id == test_template.id
    
    async def test_add_criterion_to_system_denied(
        self, db_session, test_user, system_template
    ):
        """Should return None when adding to system template."""
        service = ProfileService(db_session)
        
        data = CriterionCreate(name="Hack", max_points=10)
        
        criterion = await service.add_criterion(
            profile_id=system_template.id,
            user_id=test_user.id,
            data=data,
        )
        
        assert criterion is None
    
    async def test_update_criterion(self, db_session, test_user, test_template):
        """Should update criterion fields."""
        service = ProfileService(db_session)
        
        profile = await service.get_profile(test_template.id, test_user.id)
        criterion_id = profile.criteria[0].id
        
        data = CriterionUpdate(
            name="Renamed Criterion",
            max_points=50,
        )
        
        updated = await service.update_criterion(
            profile_id=test_template.id,
            criterion_id=criterion_id,
            user_id=test_user.id,
            data=data,
        )
        
        assert updated is not None
        assert updated.name == "Renamed Criterion"
        assert updated.max_points == 50
    
    async def test_delete_criterion(self, db_session, test_user, test_template):
        """Should delete criterion from profile."""
        service = ProfileService(db_session)
        
        profile = await service.get_profile(test_template.id, test_user.id)
        criterion_id = profile.criteria[0].id
        
        deleted = await service.delete_criterion(
            profile_id=test_template.id,
            criterion_id=criterion_id,
            user_id=test_user.id,
        )
        
        assert deleted is True
