"""Authentication routes configuration.

This module defines the FastAPI router for authentication endpoints.
Routes are thin - they only wire up URL paths to controller handlers.

Rate Limits:
    - register, login, refresh, google: 5/minute (by IP) - Prevent brute force
    - me, logout: 100/minute (by user) - Standard authenticated

Routes:
    POST /api/auth/register - Create new user account
    POST /api/auth/login - Authenticate with email/password
    POST /api/auth/refresh - Exchange refresh token for new tokens
    POST /api/auth/google - Authenticate via Google OAuth
    GET /api/auth/me - Get current user profile
    POST /api/auth/logout - Logout (client-side token discard)

Example:
    Including the router in the FastAPI app::
    
        from app.features.auth import auth_router
        app.include_router(auth_router)

Note:
    All routes are prefixed with /api/auth and tagged for OpenAPI docs.
    HTTP handling logic is in auth.controller.py, not here.
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.db.models.user import User
from app.core.rate_limit import auth_limiter, limiter, RATE_LIMIT_AUTH, RATE_LIMIT_DEFAULT
from .auth_controller import AuthController
from .auth_schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    GoogleAuthRequest,
    AuthResponse,
    TokenResponse,
    UserResponse,
    MessageResponse,
)
from .auth_dependencies import get_current_user

# Router instance with prefix and OpenAPI tags
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

# Controller instance
controller = AuthController()


# =============================================================================
# Route Definitions
# =============================================================================

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password.",
)
@auth_limiter.limit(RATE_LIMIT_AUTH)
async def register(
    request: Request,
    data: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> AuthResponse:
    """Route handler for user registration."""
    return await controller.register(data, session)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login user",
    description="Authenticate with email and password to receive tokens.",
)
@auth_limiter.limit(RATE_LIMIT_AUTH)
async def login(
    request: Request,
    data: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> AuthResponse:
    """Route handler for user login."""
    return await controller.login(data, session)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get a new access token using a valid refresh token.",
)
@auth_limiter.limit(RATE_LIMIT_AUTH)
async def refresh_token(
    request: Request,
    data: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """Route handler for token refresh."""
    return await controller.refresh_token(data, session)


@router.post(
    "/google",
    response_model=AuthResponse,
    summary="Google OAuth login",
    description="Authenticate using Google OAuth. Exchange auth code for tokens.",
)
@auth_limiter.limit(RATE_LIMIT_AUTH)
async def google_auth(
    request: Request,
    data: GoogleAuthRequest,
    session: AsyncSession = Depends(get_db_session),
) -> AuthResponse:
    """Route handler for Google OAuth authentication."""
    return await controller.google_auth(data, session)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the authenticated user's profile information.",
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_me(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Route handler for getting current user profile."""
    return await controller.get_me(current_user)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout user",
    description="Logout the current user. Client should discard tokens.",
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Route handler for user logout."""
    return await controller.logout(current_user)
