"""
Authentication schemas for request/response validation.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class AuthProvider(str, Enum):
    """Authentication provider type."""
    EMAIL = "email"
    GOOGLE = "google"


# ============== Request Schemas ==============

class RegisterRequest(BaseModel):
    """User registration request."""
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
    """User login request."""
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
    """Refresh token request."""
    refresh_token: str = Field(..., description="The refresh token")


class GoogleAuthRequest(BaseModel):
    """Google OAuth code exchange request."""
    code: str = Field(..., description="Google OAuth authorization code")
    redirect_uri: str = Field(..., description="Redirect URI used in the OAuth flow")


# ============== Response Schemas ==============

class UserResponse(BaseModel):
    """User data response (public fields only)."""
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
    """Authentication token response."""
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
    """Full authentication response with user and tokens."""
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
    """Simple message response."""
    message: str = Field(..., description="Response message")
