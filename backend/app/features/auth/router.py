"""Authentication API routes.

This module defines the FastAPI router for all authentication endpoints.
Includes user registration, login, token refresh, Google OAuth, and
user profile management.

Routes:
    POST /api/auth/register - Create new user account
    POST /api/auth/login - Authenticate with email/password
    POST /api/auth/refresh - Exchange refresh token for new access token
    POST /api/auth/google - Authenticate via Google OAuth
    GET /api/auth/me - Get current user profile
    POST /api/auth/logout - Logout (client-side token discard)

Example:
    Including the router in the FastAPI app::
    
        from fastapi import FastAPI
        from app.features.auth.router import router as auth_router
        
        app = FastAPI()
        app.include_router(auth_router)

Note:
    All routes are prefixed with /api/auth and tagged for OpenAPI
    documentation grouping.
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
    """Register a new user with email and password.
    
    Creates a new user account with the provided credentials. The password
    is hashed using bcrypt before storage. Returns the created user profile
    along with access and refresh tokens.
    
    Args:
        request: Registration data containing email, password, and full_name.
    
    Returns:
        AuthResponse containing user profile and authentication tokens.
    
    Raises:
        HTTPException: 400 Bad Request if email already exists or
            validation fails.
    
    Example:
        POST /api/auth/register
        {
            "email": "user@example.com",
            "password": "securepass123",
            "full_name": "John Doe"
        }
    """
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
    """Authenticate user with email and password.
    
    Validates the provided credentials against stored user data. If valid,
    returns the user profile along with new access and refresh tokens.
    
    Args:
        request: Login credentials containing email and password.
    
    Returns:
        AuthResponse containing user profile and authentication tokens.
    
    Raises:
        HTTPException: 401 Unauthorized if credentials are invalid
            (wrong email or password).
    
    Example:
        POST /api/auth/login
        {
            "email": "user@example.com",
            "password": "securepass123"
        }
    
    Note:
        The error message is intentionally vague ("Invalid credentials")
        to prevent user enumeration attacks.
    """
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
    """Exchange a refresh token for new access and refresh tokens.
    
    Validates the provided refresh token and issues a new token pair.
    This allows clients to maintain authentication without requiring
    the user to re-enter credentials.
    
    Args:
        request: Contains the refresh token to exchange.
    
    Returns:
        TokenResponse with new access_token and refresh_token.
    
    Raises:
        HTTPException: 401 Unauthorized if refresh token is invalid
            or expired.
    
    Example:
        POST /api/auth/refresh
        {
            "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
        }
    
    Note:
        The old refresh token is not invalidated (stateless JWT).
        Token blacklisting will be added in Phase 2 with database.
    """
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
    """Authenticate or register user via Google OAuth.
    
    Exchanges the Google authorization code for user info, then either
    logs in an existing user or creates a new account. Returns user
    profile and authentication tokens.
    
    Args:
        request: Contains the Google auth code and redirect URI.
    
    Returns:
        AuthResponse containing user profile and authentication tokens.
    
    Raises:
        HTTPException: 400 Bad Request if OAuth exchange fails or
            Google returns an error.
    
    Example:
        POST /api/auth/google
        {
            "code": "4/0AfJohXn...",
            "redirect_uri": "http://localhost:5173/auth/callback"
        }
    
    Note:
        Requires GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to be
        configured in environment variables.
    """
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
    """Get current authenticated user's profile.
    
    Returns the profile information for the user associated with
    the provided access token. Requires a valid Bearer token.
    
    Args:
        current_user: Automatically injected by the get_current_user
            dependency from the Authorization header.
    
    Returns:
        UserResponse with the user's public profile data.
    
    Raises:
        HTTPException: 401 Unauthorized if not authenticated.
        HTTPException: 403 Forbidden if account is deactivated.
    
    Example:
        GET /api/auth/me
        Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
    """
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
    """Logout the current user.
    
    Logs a logout event for the user. Since JWTs are stateless, the
    server cannot invalidate tokens. The client is responsible for
    discarding the tokens.
    
    Args:
        current_user: Automatically injected by the get_current_user
            dependency from the Authorization header.
    
    Returns:
        MessageResponse confirming successful logout.
    
    Raises:
        HTTPException: 401 Unauthorized if not authenticated.
    
    Example:
        POST /api/auth/logout
        Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
    
    Note:
        Token blacklisting will be implemented in Phase 2 when
        database storage is available. Until then, tokens remain
        valid until expiration.
    
    Todo:
        - Phase 2: Implement token blacklist in Redis or PostgreSQL
        - Phase 2: Add refresh token rotation
    """
    logger.info(f"User logged out: {current_user.email}")
    return MessageResponse(message="Successfully logged out")
