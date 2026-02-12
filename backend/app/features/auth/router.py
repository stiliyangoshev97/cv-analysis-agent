"""
Authentication API routes.
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends

from .schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    GoogleAuthRequest,
    AuthResponse,
    TokenResponse,
    UserResponse,
    MessageResponse,
)
from .service import auth_service
from .dependencies import get_current_user
from .models import User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password.",
)
async def register(request: RegisterRequest) -> AuthResponse:
    """Register a new user with email/password."""
    try:
        return auth_service.register(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login user",
    description="Authenticate with email and password to receive tokens.",
)
async def login(request: LoginRequest) -> AuthResponse:
    """Login with email/password."""
    try:
        return auth_service.login(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get a new access token using a valid refresh token.",
)
async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
    """Refresh access token using refresh token."""
    try:
        return auth_service.refresh_tokens(request.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post(
    "/google",
    response_model=AuthResponse,
    summary="Google OAuth login",
    description="Authenticate using Google OAuth. Exchange auth code for tokens.",
)
async def google_auth(request: GoogleAuthRequest) -> AuthResponse:
    """Authenticate with Google OAuth."""
    try:
        return await auth_service.google_auth(request.code, request.redirect_uri)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the authenticated user's profile information.",
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Get current authenticated user's profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        auth_provider=current_user.auth_provider,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout user",
    description="Logout the current user. Client should discard tokens.",
)
async def logout(current_user: User = Depends(get_current_user)) -> MessageResponse:
    """
    Logout user.
    Note: With JWT, we can't invalidate tokens server-side without a blacklist.
    This endpoint confirms logout - client should discard tokens.
    Token blacklisting will be added in Phase 2 with database.
    """
    logger.info(f"User logged out: {current_user.email}")
    return MessageResponse(message="Successfully logged out")
