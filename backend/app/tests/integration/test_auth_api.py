"""Integration tests for authentication API endpoints.

Tests:
    - POST /api/auth/register
    - POST /api/auth/login
    - GET /api/auth/me
    - POST /api/auth/refresh

Run with: pytest app/tests/integration/test_auth_api.py -v
"""

import pytest


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.auth
class TestRegisterEndpoint:
    """Tests for POST /api/auth/register."""
    
    async def test_register_success(self, client):
        """Should register new user successfully."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "name": "New User",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "newuser@example.com"
    
    async def test_register_duplicate_email(self, client, test_user):
        """Should return 400 for duplicate email."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,
                "password": "password123",
                "name": "Duplicate User",
            },
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    async def test_register_invalid_email(self, client):
        """Should return 422 for invalid email format."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "notanemail",
                "password": "password123",
                "name": "Test User",
            },
        )
        
        assert response.status_code == 422
    
    async def test_register_short_password(self, client):
        """Should return 422 for password too short."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",
                "name": "Test User",
            },
        )
        
        assert response.status_code == 422
    
    async def test_register_missing_fields(self, client):
        """Should return 422 for missing required fields."""
        response = await client.post(
            "/api/auth/register",
            json={"email": "test@example.com"},
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.auth
class TestLoginEndpoint:
    """Tests for POST /api/auth/login."""
    
    async def test_login_success(self, client, test_user):
        """Should login successfully with correct credentials."""
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "test@example.com"
    
    async def test_login_wrong_password(self, client, test_user):
        """Should return 401 for wrong password."""
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == 401
    
    async def test_login_nonexistent_user(self, client):
        """Should return 401 for non-existent user."""
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )
        
        assert response.status_code == 401
    
    async def test_login_invalid_email(self, client):
        """Should return 422 for invalid email."""
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "notanemail",
                "password": "password123",
            },
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.auth
class TestMeEndpoint:
    """Tests for GET /api/auth/me."""
    
    async def test_me_success(self, client, test_user, auth_headers):
        """Should return current user profile."""
        response = await client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
    
    async def test_me_no_token(self, client):
        """Should return 401 without token."""
        response = await client.get("/api/auth/me")
        
        assert response.status_code == 401
    
    async def test_me_invalid_token(self, client):
        """Should return 401 with invalid token."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.auth
class TestRefreshEndpoint:
    """Tests for POST /api/auth/refresh."""
    
    async def test_refresh_success(self, client, test_user):
        """Should refresh tokens successfully."""
        # First login to get refresh token
        login_response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Use refresh token
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    async def test_refresh_invalid_token(self, client):
        """Should return 401 for invalid refresh token."""
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        
        assert response.status_code == 401
