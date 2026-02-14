"""Unit tests for authentication.

Tests for:
    - Password hashing and verification
    - JWT token creation and validation
    - Login/register flows

Run with: pytest app/tests/unit/test_auth.py -v
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import pytest
from jose import jwt

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.config import get_settings


class TestPasswordHashing:
    """Tests for password hashing functions."""
    
    def test_hash_password_returns_hash(self):
        """Should return a bcrypt hash, not plaintext."""
        password = "mysecretpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt prefix
    
    def test_hash_password_unique_per_call(self):
        """Should generate different hashes for same password (salting)."""
        password = "samepassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
    
    def test_verify_password_correct(self):
        """Should return True for correct password."""
        password = "correctpassword"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Should return False for incorrect password."""
        password = "correctpassword"
        hashed = hash_password(password)
        
        assert verify_password("wrongpassword", hashed) is False
    
    def test_verify_password_empty(self):
        """Should handle empty password."""
        hashed = hash_password("somepassword")
        
        assert verify_password("", hashed) is False
    
    def test_hash_password_unicode(self):
        """Should handle unicode characters in password."""
        password = "пароль123密码"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Tests for JWT token functions."""
    
    def test_create_access_token(self):
        """Should create valid JWT access token."""
        user_id = str(uuid.uuid4())
        token = create_access_token(user_id)
        
        assert token is not None
        assert len(token) > 0
        
        # Decode and verify
        settings = get_settings()
        decoded = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        
        assert decoded["sub"] == user_id
        assert "exp" in decoded
        assert decoded["type"] == "access"
    
    def test_create_access_token_expiry(self):
        """Should have proper expiration."""
        user_id = str(uuid.uuid4())
        
        token = create_access_token(user_id)
        
        settings = get_settings()
        decoded = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Should expire within configured minutes
        diff = exp_time - now
        expected_seconds = settings.access_token_expire_minutes * 60
        assert 0 < diff.total_seconds() <= expected_seconds + 10  # Small tolerance
    
    def test_create_refresh_token(self):
        """Should create valid JWT refresh token."""
        user_id = str(uuid.uuid4())
        token = create_refresh_token(user_id)
        
        settings = get_settings()
        decoded = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        
        assert decoded["sub"] == user_id
        assert decoded["type"] == "refresh"
    
    def test_decode_token_valid(self):
        """Should decode valid token successfully."""
        user_id = "user123"
        token = create_access_token(user_id)
        
        decoded = decode_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == user_id
    
    def test_decode_token_invalid(self):
        """Should return None for invalid token."""
        decoded = decode_token("invalid.token.here")
        
        assert decoded is None
    
    def test_decode_token_tampered(self):
        """Should return None for tampered token."""
        token = create_access_token("user123")
        
        # Tamper with the token
        parts = token.split(".")
        parts[1] = "tampered"
        tampered_token = ".".join(parts)
        
        decoded = decode_token(tampered_token)
        
        assert decoded is None


@pytest.mark.asyncio
@pytest.mark.auth
class TestAuthService:
    """Tests for AuthService (if exists)."""
    
    async def test_register_user_success(self, db_session):
        """Should register new user successfully."""
        from app.features.auth.auth_service import AuthService
        from app.features.auth.auth_schemas import RegisterRequest
        
        service = AuthService(db_session)
        
        request = RegisterRequest(
            email="newuser@example.com",
            password="securepassword123",
            full_name="New User",
        )
        
        response = await service.register(request)
        
        assert response is not None
        assert response.user.email == "newuser@example.com"
        assert response.user.full_name == "New User"
        assert response.tokens.access_token is not None
    
    async def test_register_duplicate_email(self, db_session, test_user):
        """Should raise error for duplicate email."""
        from app.features.auth.auth_service import AuthService
        from app.features.auth.auth_schemas import RegisterRequest
        
        service = AuthService(db_session)
        
        request = RegisterRequest(
            email=test_user.email,  # Same as existing user
            password="password123",
            full_name="Another User",
        )
        
        with pytest.raises(ValueError, match="already registered"):
            await service.register(request)
    
    async def test_login_success(self, db_session, test_user):
        """Should login successfully with correct credentials."""
        from app.features.auth.auth_service import AuthService
        from app.features.auth.auth_schemas import LoginRequest
        
        service = AuthService(db_session)
        
        request = LoginRequest(
            email="test@example.com",
            password="testpassword123",
        )
        
        response = await service.login(request)
        
        assert response is not None
        assert response.tokens.access_token is not None
        assert response.tokens.refresh_token is not None
        assert response.user.email == "test@example.com"
    
    async def test_login_wrong_password(self, db_session, test_user):
        """Should raise error for wrong password."""
        from app.features.auth.auth_service import AuthService
        from app.features.auth.auth_schemas import LoginRequest
        
        service = AuthService(db_session)
        
        request = LoginRequest(
            email="test@example.com",
            password="wrongpassword",
        )
        
        with pytest.raises(ValueError, match="Invalid"):
            await service.login(request)
    
    async def test_login_user_not_found(self, db_session):
        """Should raise error for non-existent user."""
        from app.features.auth.auth_service import AuthService
        from app.features.auth.auth_schemas import LoginRequest
        
        service = AuthService(db_session)
        
        request = LoginRequest(
            email="nonexistent@example.com",
            password="somepassword",
        )
        
        with pytest.raises(ValueError, match="Invalid"):
            await service.login(request)
    
    async def test_get_user_by_id(self, db_session, test_user):
        """Should get user by ID."""
        from app.features.auth.auth_service import AuthService
        
        service = AuthService(db_session)
        
        user = await service.get_user_by_id(test_user.id)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email


@pytest.mark.asyncio
@pytest.mark.auth
class TestRefreshToken:
    """Tests for refresh token functionality."""
    
    async def test_refresh_token_success(self, db_session, test_user):
        """Should refresh tokens successfully."""
        from app.features.auth.auth_service import AuthService
        
        service = AuthService(db_session)
        
        # Create initial refresh token
        refresh_token = service.create_refresh_token(test_user.id)
        
        result = await service.refresh_tokens(refresh_token)
        
        assert result is not None
        assert result.access_token is not None
        assert result.refresh_token is not None
    
    async def test_refresh_token_invalid(self, db_session):
        """Should raise error for invalid refresh token."""
        from app.features.auth.auth_service import AuthService
        
        service = AuthService(db_session)
        
        with pytest.raises(ValueError, match="Invalid"):
            await service.refresh_tokens("invalid.token.here")
    
    async def test_refresh_token_wrong_type(self, db_session, test_user):
        """Should raise error when using access token as refresh."""
        from app.features.auth.auth_service import AuthService
        
        service = AuthService(db_session)
        
        # Try to use access token as refresh token
        access_token = service.create_access_token(test_user.id)
        
        with pytest.raises(ValueError):
            await service.refresh_tokens(access_token)
