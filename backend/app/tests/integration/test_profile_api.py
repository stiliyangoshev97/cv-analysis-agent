"""Integration tests for Profile API endpoints.

Tests:
    - GET /api/profiles/ - List profiles
    - GET /api/profiles/{id} - Get profile
    - POST /api/profiles/ - Create profile
    - PUT /api/profiles/{id} - Update profile
    - DELETE /api/profiles/{id} - Delete profile
    - POST /api/profiles/{id}/clone - Clone profile
    - Criteria management endpoints

Run with: pytest app/tests/integration/test_profile_api.py -v

API Schema Notes:
    - ProfileListResponse: {"profiles": [...], "total": N}
    - ProfileResponse: uses is_system_template, passing_score, max_points
    - CriterionResponse: uses max_points (not weight)
    - CloneProfileRequest: uses new_name (not name)
    - Delete returns 200 with {"message": "..."} (not 204)
"""

import uuid

import pytest


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.profile
class TestListProfilesEndpoint:
    """Tests for GET /api/profiles/."""
    
    async def test_list_profiles_empty(self, client, auth_headers):
        """Should return empty list when no profiles."""
        response = await client.get("/api/profiles/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        # Response is ProfileListResponse with profiles array and total
        assert "profiles" in data
        assert "total" in data
        assert isinstance(data["profiles"], list)
    
    async def test_list_profiles_with_system(self, client, auth_headers, system_template):
        """Should include system templates."""
        response = await client.get("/api/profiles/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        system_profiles = [p for p in data["profiles"] if p["is_system_template"]]
        assert len(system_profiles) >= 1
    
    async def test_list_profiles_unauthorized(self, client):
        """Should return 401 without auth."""
        response = await client.get("/api/profiles/")
        
        assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.profile
class TestGetProfileEndpoint:
    """Tests for GET /api/profiles/{id}."""
    
    async def test_get_profile_success(self, client, auth_headers, test_template):
        """Should return profile with criteria."""
        response = await client.get(
            f"/api/profiles/{test_template.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_template.id)
        assert data["name"] == test_template.name
        assert "criteria" in data
        assert "passing_score" in data
        assert "is_system_template" in data
    
    async def test_get_profile_not_found(self, client, auth_headers):
        """Should return 404 for non-existent profile."""
        response = await client.get(
            f"/api/profiles/{uuid.uuid4()}",
            headers=auth_headers,
        )
        
        assert response.status_code == 404
    
    async def test_get_system_profile(self, client, auth_headers, system_template):
        """Should allow access to system profiles."""
        response = await client.get(
            f"/api/profiles/{system_template.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_system_template"] is True


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.profile
class TestCreateProfileEndpoint:
    """Tests for POST /api/profiles/."""
    
    async def test_create_profile_success(self, client, auth_headers):
        """Should create profile successfully."""
        response = await client.post(
            "/api/profiles/",
            json={
                "name": "Data Engineer",
                "description": "Profile for data engineering roles",
                "passing_score": 75,
                "criteria": [
                    {"name": "Data Skills", "max_points": 50, "description": "SQL, ETL"},
                    {"name": "Programming", "max_points": 50, "description": "Python"},
                ],
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Data Engineer"
        assert data["passing_score"] == 75
        assert data["is_system_template"] is False
    
    async def test_create_profile_with_criteria(self, client, auth_headers):
        """Should create profile with initial criteria."""
        response = await client.post(
            "/api/profiles/",
            json={
                "name": "Full Stack Dev",
                "criteria": [
                    {"name": "Frontend", "max_points": 40, "description": "React/Vue"},
                    {"name": "Backend", "max_points": 40, "description": "Node/Python"},
                    {"name": "DevOps", "max_points": 20, "description": "CI/CD"},
                ],
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data.get("criteria", [])) == 3
        # Check that criteria use max_points
        for criterion in data["criteria"]:
            assert "max_points" in criterion
    
    async def test_create_profile_missing_name(self, client, auth_headers):
        """Should return 422 for missing name."""
        response = await client.post(
            "/api/profiles/",
            json={
                "description": "No name provided",
                "criteria": [{"name": "Test", "max_points": 50}],
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 422
    
    async def test_create_profile_missing_criteria(self, client, auth_headers):
        """Should return 422 for missing criteria (at least 1 required)."""
        response = await client.post(
            "/api/profiles/",
            json={"name": "No Criteria Profile"},
            headers=auth_headers,
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.profile
class TestUpdateProfileEndpoint:
    """Tests for PUT /api/profiles/{id}."""
    
    async def test_update_profile_success(self, client, auth_headers, test_template):
        """Should update profile successfully."""
        response = await client.put(
            f"/api/profiles/{test_template.id}",
            json={
                "name": "Updated Name",
                "description": "Updated description",
                "passing_score": 80,
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["passing_score"] == 80
    
    async def test_update_profile_partial(self, client, auth_headers, test_template):
        """Should allow partial updates."""
        original_name = test_template.name
        
        response = await client.put(
            f"/api/profiles/{test_template.id}",
            json={"description": "Only description changed"},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == original_name
        assert data["description"] == "Only description changed"
    
    async def test_update_system_profile_denied(
        self, client, auth_headers, system_template
    ):
        """Should deny updating system templates."""
        response = await client.put(
            f"/api/profiles/{system_template.id}",
            json={"name": "Hacked Name"},
            headers=auth_headers,
        )
        
        assert response.status_code == 403
    
    async def test_update_profile_not_found(self, client, auth_headers):
        """Should return 404 for non-existent profile."""
        response = await client.put(
            f"/api/profiles/{uuid.uuid4()}",
            json={"name": "Updated"},
            headers=auth_headers,
        )
        
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.profile
class TestDeleteProfileEndpoint:
    """Tests for DELETE /api/profiles/{id}."""
    
    async def test_delete_profile_success(self, client, auth_headers, test_template):
        """Should delete profile successfully."""
        response = await client.delete(
            f"/api/profiles/{test_template.id}",
            headers=auth_headers,
        )
        
        # Controller returns 200 with message dict
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verify deleted
        get_response = await client.get(
            f"/api/profiles/{test_template.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404
    
    async def test_delete_system_profile_denied(
        self, client, auth_headers, system_template
    ):
        """Should deny deleting system templates."""
        response = await client.delete(
            f"/api/profiles/{system_template.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 403
    
    async def test_delete_profile_not_found(self, client, auth_headers):
        """Should return 404 for non-existent profile."""
        response = await client.delete(
            f"/api/profiles/{uuid.uuid4()}",
            headers=auth_headers,
        )
        
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.profile
class TestCloneProfileEndpoint:
    """Tests for POST /api/profiles/{id}/clone."""
    
    async def test_clone_system_profile(self, client, auth_headers, system_template):
        """Should clone system template successfully."""
        response = await client.post(
            f"/api/profiles/{system_template.id}/clone",
            json={"new_name": "My Custom Profile"},
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Custom Profile"
        assert data["is_system_template"] is False
        assert data["id"] != str(system_template.id)
    
    async def test_clone_user_profile(self, client, auth_headers, test_template):
        """Should clone user's own profile."""
        response = await client.post(
            f"/api/profiles/{test_template.id}/clone",
            json={"new_name": "Profile Copy"},
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Profile Copy"
    
    async def test_clone_profile_with_description(self, client, auth_headers, test_template):
        """Should clone profile with custom description."""
        response = await client.post(
            f"/api/profiles/{test_template.id}/clone",
            json={
                "new_name": "Cloned Profile",
                "description": "Custom description for clone",
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Cloned Profile"
        assert data["description"] == "Custom description for clone"
    
    async def test_clone_profile_not_found(self, client, auth_headers):
        """Should return 404 for non-existent profile."""
        response = await client.post(
            f"/api/profiles/{uuid.uuid4()}/clone",
            json={"new_name": "Clone"},
            headers=auth_headers,
        )
        
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.profile
class TestCriteriaEndpoints:
    """Tests for criteria management endpoints."""
    
    async def test_add_criterion(self, client, auth_headers, test_template):
        """Should add criterion to profile."""
        response = await client.post(
            f"/api/profiles/{test_template.id}/criteria",
            json={
                "name": "Leadership",
                "max_points": 15,
                "description": "Leadership experience",
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Leadership"
        assert data["max_points"] == 15
    
    async def test_add_criterion_to_system_denied(
        self, client, auth_headers, system_template
    ):
        """Should deny adding criterion to system template."""
        response = await client.post(
            f"/api/profiles/{system_template.id}/criteria",
            json={"name": "New", "max_points": 10},
            headers=auth_headers,
        )
        
        # Controller returns 404 for "cannot be modified"
        assert response.status_code == 404
    
    async def test_update_criterion(self, client, auth_headers, test_template):
        """Should update existing criterion."""
        # Get profile to find criterion ID
        get_response = await client.get(
            f"/api/profiles/{test_template.id}",
            headers=auth_headers,
        )
        criterion_id = get_response.json()["criteria"][0]["id"]
        
        response = await client.put(
            f"/api/profiles/{test_template.id}/criteria/{criterion_id}",
            json={"name": "Updated Criterion", "max_points": 50},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Criterion"
        assert data["max_points"] == 50
    
    async def test_delete_criterion(self, client, auth_headers, test_template):
        """Should delete criterion from profile."""
        # Get profile to find criterion ID
        get_response = await client.get(
            f"/api/profiles/{test_template.id}",
            headers=auth_headers,
        )
        criteria = get_response.json()["criteria"]
        criterion_id = criteria[0]["id"]
        
        response = await client.delete(
            f"/api/profiles/{test_template.id}/criteria/{criterion_id}",
            headers=auth_headers,
        )
        
        # Controller returns 200 with message dict
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verify deleted by trying to delete again (should 404)
        response_2 = await client.delete(
            f"/api/profiles/{test_template.id}/criteria/{criterion_id}",
            headers=auth_headers,
        )
        assert response_2.status_code == 404
