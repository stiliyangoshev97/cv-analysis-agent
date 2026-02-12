"""Authentication controller for HTTP request handling.

This module contains the AuthController class which handles HTTP-level
concerns for authentication endpoints. It validates requests, calls
the service layer, and formats responses.

The controller is responsible for:
- Parsing and validating request data (via Pydantic schemas)
- Calling the appropriate service methods
- Handling errors and converting them to HTTP responses
- Formatting successful responses

Classes:
    AuthController: Handles all authentication HTTP endpoints.

Example:
    Using the controller in routes::
    
        from .auth_controller import AuthController
        
        controller = AuthController()
        
        @router.post("/register")
        async def register(request: RegisterRequest):
            return await controller.register(request)

Note:
    Business logic should NOT be in this file. It belongs in auth_service.py.
    This controller only handles HTTP concerns.
"""

import logging
from fastapi import HTTPException, status

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
from .auth_service import auth_service
from .auth_models import User

logger = logging.getLogger(__name__)


class AuthController:
    """Controller for authentication HTTP endpoints.
    
    Handles HTTP request/response logic for authentication operations.
    Delegates business logic to AuthService.
    
    Methods:
        register: Handle user registration requests.
        login: Handle user login requests.
        refresh_token: Handle token refresh requests.
        google_auth: Handle Google OAuth requests.
        get_me: Handle get current user requests.
        logout: Handle logout requests.
    
    Example:
        >>> controller = AuthController()
        >>> response = await controller.login(login_request)
    """
    
    async def register(self, request: RegisterRequest) -> AuthResponse:
        """Handle user registration request.
        
        Creates a new user account with the provided credentials.
        The password is hashed before storage.
        
        Args:
            request: Registration data (email, password, full_name).
        
        Returns:
            AuthResponse with user profile and tokens.
        
        Raises:
            HTTPException: 400 if email exists or validation fails.
        
        Example:
            POST /api/auth/register
            {"email": "user@example.com", "password": "pass123", "full_name": "John"}
        """
        try:
            logger.info(f"Registration attempt for: {request.email}")
            result = auth_service.register(request)
            logger.info(f"User registered successfully: {request.email}")
            return result
        except ValueError as e:
            logger.warning(f"Registration failed for {request.email}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def login(self, request: LoginRequest) -> AuthResponse:
        """Handle user login request.
        
        Validates credentials and returns tokens if valid.
        
        Args:
            request: Login credentials (email, password).
        
        Returns:
            AuthResponse with user profile and tokens.
        
        Raises:
            HTTPException: 401 if credentials are invalid.
        
        Example:
            POST /api/auth/login
            {"email": "user@example.com", "password": "pass123"}
        
        Note:
            Error message is intentionally vague to prevent enumeration.
        """
        try:
            logger.info(f"Login attempt for: {request.email}")
            result = auth_service.login(request)
            logger.info(f"User logged in successfully: {request.email}")
            return result
        except ValueError as e:
            logger.warning(f"Login failed for {request.email}: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    
    async def refresh_token(self, request: RefreshTokenRequest) -> TokenResponse:
        """Handle token refresh request.
        
        Exchanges a valid refresh token for new access/refresh tokens.
        
        Args:
            request: Contains the refresh token to exchange.
        
        Returns:
            TokenResponse with new token pair.
        
        Raises:
            HTTPException: 401 if refresh token is invalid/expired.
        
        Example:
            POST /api/auth/refresh
            {"refresh_token": "eyJhbGciOiJIUzI1NiIs..."}
        """
        try:
            logger.debug("Token refresh attempt")
            result = auth_service.refresh_tokens(request.refresh_token)
            logger.debug("Token refreshed successfully")
            return result
        except ValueError as e:
            logger.warning(f"Token refresh failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    
    async def google_auth(self, request: GoogleAuthRequest) -> AuthResponse:
        """Handle Google OAuth authentication request.
        
        Exchanges Google auth code for user info, creates or logs in user.
        
        Args:
            request: Contains Google auth code and redirect URI.
        
        Returns:
            AuthResponse with user profile and tokens.
        
        Raises:
            HTTPException: 400 if OAuth exchange fails.
        
        Example:
            POST /api/auth/google
            {"code": "4/0AfJohXn...", "redirect_uri": "http://localhost:5173/..."}
        
        Note:
            Requires GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET configured.
        """
        try:
            logger.info("Google OAuth attempt")
            result = await auth_service.google_auth(request.code, request.redirect_uri)
            logger.info(f"Google OAuth successful for: {result.user.email}")
            return result
        except ValueError as e:
            logger.warning(f"Google OAuth failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def get_me(self, current_user: User) -> UserResponse:
        """Handle get current user profile request.
        
        Returns the authenticated user's profile information.
        
        Args:
            current_user: User object from auth dependency.
        
        Returns:
            UserResponse with user's public profile data.
        
        Example:
            GET /api/auth/me
            Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
        """
        logger.debug(f"Profile request for user: {current_user.email}")
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            auth_provider=current_user.auth_provider,
            avatar_url=current_user.avatar_url,
            created_at=current_user.created_at,
        )
    
    async def logout(self, current_user: User) -> MessageResponse:
        """Handle user logout request.
        
        Logs the logout event. Client should discard tokens.
        
        Args:
            current_user: User object from auth dependency.
        
        Returns:
            MessageResponse confirming logout.
        
        Example:
            POST /api/auth/logout
            Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
        
        Note:
            With stateless JWT, tokens remain valid until expiration.
            Token blacklisting will be added in Phase 2.
        """
        logger.info(f"User logged out: {current_user.email}")
        return MessageResponse(message="Successfully logged out")
