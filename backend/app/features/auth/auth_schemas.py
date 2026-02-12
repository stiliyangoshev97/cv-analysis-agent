"""Authentication schemas for request/response validation.

This module defines Pydantic models for authentication-related API
requests and responses. All schemas include validation rules and
JSON schema examples for OpenAPI documentation.

Schemas:
    Request schemas:
        - RegisterRequest: New user registration data
        - LoginRequest: User login credentials
        - RefreshTokenRequest: Token refresh request
        - GoogleAuthRequest: Google OAuth code exchange
    
    Response schemas:
        - UserResponse: Public user profile data
        - TokenResponse: JWT token pair with metadata
        - AuthResponse: Combined user + tokens response
        - MessageResponse: Simple message response

Example:
    Using schemas in FastAPI routes::
    
        @router.post("/register", response_model=AuthResponse)
        async def register(request: RegisterRequest) -> AuthResponse:
            user = auth_service.register(request)
            return AuthResponse(user=user, tokens=generate_tokens(user))

Note:
    All schemas use Pydantic v2 with `from_attributes = True` for
    ORM compatibility (Phase 2: SQLAlchemy integration).
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class AuthProvider(str, Enum):
    """Authentication provider enumeration.
    
    Indicates how a user authenticated to the system. Used to
    differentiate between email/password users and OAuth users.
    
    Attributes:
        EMAIL: User registered with email and password.
        GOOGLE: User authenticated via Google OAuth 2.0.
    """
    EMAIL = "email"
    GOOGLE = "google"


# ============== Request Schemas ==============

class RegisterRequest(BaseModel):
    """User registration request schema.
    
    Validates and parses incoming user registration data. Enforces
    email format, password minimum length, and name constraints.
    
    Attributes:
        email: Valid email address (validated by Pydantic's EmailStr).
        password: Password with minimum 8 characters.
        full_name: User's full name (2-100 characters).
    
    Example:
        >>> request = RegisterRequest(
        ...     email="user@example.com",
        ...     password="securepass123",
        ...     full_name="John Doe"
        ... )
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "recruiter@company.com",
                "password": "securepassword123",
                "full_name": "John Smith"
            }
        }


class LoginRequest(BaseModel):
    """User login request schema.
    
    Validates credentials for email/password authentication. Used
    by the /login endpoint to authenticate existing users.
    
    Attributes:
        email: User's registered email address.
        password: User's password (no length validation on login).
    
    Example:
        >>> request = LoginRequest(
        ...     email="user@example.com",
        ...     password="securepass123"
        ... )
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "recruiter@company.com",
                "password": "securepassword123"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema.
    
    Used to exchange a valid refresh token for a new access token
    without requiring re-authentication.
    
    Attributes:
        refresh_token: A valid JWT refresh token.
    
    Example:
        >>> request = RefreshTokenRequest(
        ...     refresh_token="eyJhbGciOiJIUzI1NiIs..."
        ... )
    """
    refresh_token: str = Field(..., description="The refresh token")


class GoogleAuthRequest(BaseModel):
    """Google OAuth code exchange request schema.
    
    Contains the authorization code received from Google OAuth flow
    and the redirect URI used during the authorization request.
    
    Attributes:
        code: Authorization code from Google OAuth redirect.
        redirect_uri: The exact redirect URI used in the auth request.
    
    Note:
        The redirect_uri must match exactly what was used in the
        authorization URL, otherwise Google will reject the exchange.
    
    Example:
        >>> request = GoogleAuthRequest(
        ...     code="4/0AfJohXn...",
        ...     redirect_uri="http://localhost:5173/auth/callback"
        ... )
    """
    code: str = Field(..., description="Google OAuth authorization code")
    redirect_uri: str = Field(..., description="Redirect URI used in the OAuth flow")


# ============== Response Schemas ==============

class UserResponse(BaseModel):
    """User profile response schema.
    
    Contains public user information suitable for API responses.
    Excludes sensitive data like hashed passwords.
    
    Attributes:
        id: Unique user identifier (format: usr_xxxxx).
        email: User's email address.
        full_name: User's display name.
        auth_provider: How the user authenticated (email/google).
        avatar_url: Optional profile picture URL (from OAuth providers).
        created_at: Account creation timestamp (UTC).
    
    Example:
        >>> response = UserResponse(
        ...     id="usr_abc123",
        ...     email="user@example.com",
        ...     full_name="John Doe",
        ...     auth_provider=AuthProvider.EMAIL,
        ...     avatar_url=None,
        ...     created_at=datetime.utcnow()
        ... )
    """
    id: str = Field(..., description="User's unique identifier")
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(..., description="User's full name")
    auth_provider: AuthProvider = Field(..., description="How the user authenticated")
    avatar_url: Optional[str] = Field(None, description="User's profile picture URL")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "usr_abc123",
                "email": "recruiter@company.com",
                "full_name": "John Smith",
                "auth_provider": "email",
                "avatar_url": None,
                "created_at": "2025-02-12T10:30:00Z"
            }
        }


class TokenResponse(BaseModel):
    """Authentication token response schema.
    
    Contains JWT access and refresh tokens with metadata.
    Returned after successful authentication or token refresh.
    
    Attributes:
        access_token: Short-lived JWT for API authorization.
        refresh_token: Long-lived JWT for obtaining new access tokens.
        token_type: Token type (always "bearer").
        expires_in: Access token TTL in seconds.
    
    Note:
        - Access tokens expire in 30 minutes (configurable).
        - Refresh tokens expire in 7 days (configurable).
        - Tokens are signed with HS256 algorithm.
    
    Example:
        >>> response = TokenResponse(
        ...     access_token="eyJhbGciOiJIUzI1NiIs...",
        ...     refresh_token="eyJhbGciOiJIUzI1NiIs...",
        ...     token_type="bearer",
        ...     expires_in=1800
        ... )
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class AuthResponse(BaseModel):
    """Full authentication response schema.
    
    Combined response containing user profile and authentication tokens.
    Returned from login, register, and OAuth endpoints.
    
    Attributes:
        user: User profile data (see UserResponse).
        tokens: Authentication tokens (see TokenResponse).
    
    Example:
        >>> response = AuthResponse(
        ...     user=UserResponse(...),
        ...     tokens=TokenResponse(...)
        ... )
    """
    user: UserResponse = Field(..., description="User data")
    tokens: TokenResponse = Field(..., description="Authentication tokens")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "usr_abc123",
                    "email": "recruiter@company.com",
                    "full_name": "John Smith",
                    "auth_provider": "email",
                    "avatar_url": None,
                    "created_at": "2025-02-12T10:30:00Z"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIs...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                    "token_type": "bearer",
                    "expires_in": 1800
                }
            }
        }


class MessageResponse(BaseModel):
    """Simple message response schema.
    
    Generic response for endpoints that return a status message.
    Used for operations like logout where no data is returned.
    
    Attributes:
        message: Human-readable status message.
    
    Example:
        >>> response = MessageResponse(message="Successfully logged out")
    """
    message: str = Field(..., description="Response message")
