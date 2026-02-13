"""
Authentication service - handles user registration, login, and token management.

This module provides the core authentication business logic:
- Password hashing with bcrypt
- JWT token creation and validation
- User registration and login
- Google OAuth integration

Example:
    >>> from app.features.auth.auth_service import AuthService
    >>> from app.db.session import get_db_session
    >>> async with get_db_session() as session:
    ...     service = AuthService(session)
    ...     response = await service.register(RegisterRequest(
    ...         email="user@example.com",
    ...         password="securepassword",
    ...         full_name="John Doe"
    ...     ))
    ...     print(response.user.email)
    user@example.com

Note:
    User data is stored in PostgreSQL using SQLAlchemy async sessions.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import uuid
import httpx
import bcrypt

from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models.user import User, AuthProvider
from .auth_repository import UserRepository
from .auth_schemas import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse,
    AuthResponse,
)

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service for authentication operations.
    
    Handles all authentication-related business logic including:
    - Password hashing and verification
    - JWT token creation and validation
    - User registration and login
    - Token refresh
    - Google OAuth authentication
    
    Attributes:
        settings: Application settings from environment.
        repository: UserRepository for database operations.
    
    Example:
        >>> async with get_db_session() as session:
        ...     service = AuthService(session)
        ...     tokens = service.create_tokens(user_id)
        ...     print(tokens.token_type)
        bearer
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize the authentication service with database session.
        
        Args:
            session: SQLAlchemy AsyncSession for database operations.
        """
        self.settings = get_settings()
        self.repository = UserRepository(session)
    
    # ============== Password Hashing ==============
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Uses bcrypt with 12 rounds for secure password hashing.
        Automatically truncates to 72 bytes (bcrypt limit).
        
        Args:
            password: Plain text password to hash.
            
        Returns:
            Bcrypt hash string suitable for storage.
            
        Example:
            >>> hashed = service.hash_password("mypassword")
            >>> hashed.startswith("$2b$")
            True
        """
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify.
            hashed_password: Bcrypt hash to compare against.
            
        Returns:
            True if password matches, False otherwise.
            
        Example:
            >>> hashed = service.hash_password("mypassword")
            >>> service.verify_password("mypassword", hashed)
            True
            >>> service.verify_password("wrongpassword", hashed)
            False
        """
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    # ============== JWT Token Management ==============
    
    def create_access_token(self, user_id: uuid.UUID, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            user_id: User UUID to encode in the token.
            expires_delta: Optional custom expiration time. Defaults to
                          ACCESS_TOKEN_EXPIRE_MINUTES from settings.
                          
        Returns:
            Encoded JWT access token string.
            
        Example:
            >>> token = service.create_access_token(user.id)
            >>> token.startswith("eyJ")
            True
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.settings.access_token_expire_minutes)
        
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(
            to_encode, 
            self.settings.jwt_secret_key, 
            algorithm=self.settings.jwt_algorithm
        )
    
    def create_refresh_token(self, user_id: uuid.UUID) -> str:
        """
        Create a JWT refresh token.
        
        Refresh tokens have a longer expiration (default 7 days)
        and are used to obtain new access tokens.
        
        Args:
            user_id: User UUID to encode in the token.
            
        Returns:
            Encoded JWT refresh token string.
        """
        expires_delta = timedelta(days=self.settings.refresh_token_expire_days)
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh"
        }
        return jwt.encode(
            to_encode, 
            self.settings.jwt_secret_key, 
            algorithm=self.settings.jwt_algorithm
        )
    
    def create_tokens(self, user_id: uuid.UUID) -> TokenResponse:
        """
        Create both access and refresh tokens.
        
        Convenience method that generates both tokens at once,
        typically used after successful login or registration.
        
        Args:
            user_id: User UUID to encode in both tokens.
            
        Returns:
            TokenResponse containing both tokens and metadata.
        """
        access_token = self.create_access_token(user_id)
        refresh_token = self.create_refresh_token(user_id)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.settings.access_token_expire_minutes * 60
        )
    
    def decode_token(self, token: str) -> Optional[dict]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token string to decode.
            
        Returns:
            Decoded payload dict if valid, None if invalid or expired.
            
        Example:
            >>> token = service.create_access_token(user.id)
            >>> payload = service.decode_token(token)
            >>> payload["sub"]
            'uuid-string'
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm]
            )
            return payload
        except JWTError as e:
            logger.warning(f"JWT decode error: {e}")
            return None
    
    # ============== User Operations ==============
    
    async def register(self, request: RegisterRequest) -> AuthResponse:
        """
        Register a new user with email/password.
        
        Creates a new user account and returns authentication tokens.
        The user is automatically logged in after registration.
        
        Args:
            request: Registration data with email, password, and name.
            
        Returns:
            AuthResponse with user data and tokens.
            
        Raises:
            ValueError: If email is already registered.
            
        Example:
            >>> response = await service.register(RegisterRequest(
            ...     email="new@example.com",
            ...     password="securepass123",
            ...     full_name="New User"
            ... ))
            >>> response.user.email
            'new@example.com'
        """
        if await self.repository.exists_by_email(request.email):
            raise ValueError("Email already registered")
        
        user = User(
            email=request.email.lower(),
            name=request.full_name,
            password_hash=self.hash_password(request.password),
            auth_provider=AuthProvider.EMAIL,
        )
        user = await self.repository.create(user)
        
        logger.info(f"New user registered: {user.email}")
        
        tokens = self.create_tokens(user.id)
        
        return AuthResponse(
            user=self._to_user_response(user),
            tokens=tokens
        )
    
    async def login(self, request: LoginRequest) -> AuthResponse:
        """
        Login with email/password.
        
        Validates credentials and returns authentication tokens.
        
        Args:
            request: Login credentials with email and password.
            
        Returns:
            AuthResponse with user data and tokens.
            
        Raises:
            ValueError: If credentials are invalid, account is deactivated,
                       or user should login with different provider.
        """
        user = await self.repository.get_by_email(request.email.lower())
        
        if not user:
            raise ValueError("Invalid email or password")
        
        if user.auth_provider != AuthProvider.EMAIL:
            raise ValueError(f"Please login with {user.auth_provider}")
        
        if not user.password_hash or not self.verify_password(request.password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        logger.info(f"User logged in: {user.email}")
        
        tokens = self.create_tokens(user.id)
        
        return AuthResponse(
            user=self._to_user_response(user),
            tokens=tokens
        )
    
    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.
        
        Validates the refresh token and issues new token pair.
        
        Args:
            refresh_token: Valid refresh token string.
            
        Returns:
            New TokenResponse with fresh tokens.
            
        Raises:
            ValueError: If refresh token is invalid, expired, or user inactive.
        """
        payload = self.decode_token(refresh_token)
        
        if not payload:
            raise ValueError("Invalid refresh token")
        
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")
        
        user_id_str = payload.get("sub")
        try:
            user_id = uuid.UUID(user_id_str)
        except (ValueError, TypeError):
            raise ValueError("Invalid user ID in token")
        
        user = await self.repository.get_by_id(user_id)
        
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        return self.create_tokens(user.id)
    
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User's unique identifier (UUID).
            
        Returns:
            User object if found, None otherwise.
        """
        return await self.repository.get_by_id(user_id)
    
    # ============== Google OAuth ==============
    
    async def google_auth(self, code: str, redirect_uri: str) -> AuthResponse:
        """
        Handle Google OAuth authentication.
        
        Exchanges Google authorization code for tokens, retrieves user
        info, and creates/updates the user account.
        
        Args:
            code: Authorization code from Google OAuth flow.
            redirect_uri: Redirect URI used in the OAuth flow.
            
        Returns:
            AuthResponse with user data and tokens.
            
        Raises:
            ValueError: If Google OAuth not configured, code invalid,
                       or email already registered with different provider.
                       
        Note:
            Requires GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in env.
        """
        settings = self.settings
        
        if not settings.google_client_id or not settings.google_client_secret:
            raise ValueError("Google OAuth not configured")
        
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                }
            )
            
            if token_response.status_code != 200:
                logger.error(f"Google token exchange failed: {token_response.text}")
                raise ValueError("Failed to authenticate with Google")
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            # Get user info
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if userinfo_response.status_code != 200:
                raise ValueError("Failed to get user info from Google")
            
            google_user = userinfo_response.json()
        
        google_id = google_user.get("id")
        email = google_user.get("email", "").lower()
        name = google_user.get("name", "")
        picture = google_user.get("picture")
        
        # Check if user exists by Google ID
        user = await self.repository.get_by_google_id(google_id)
        
        if user:
            # Existing Google user - update and login
            user.avatar_url = picture
            await self.repository.update(user)
        else:
            # Check if email exists with different provider
            existing_user = await self.repository.get_by_email(email)
            if existing_user:
                if existing_user.auth_provider != AuthProvider.GOOGLE:
                    raise ValueError(f"Email already registered with {existing_user.auth_provider}")
                # Link Google ID to existing account
                existing_user.google_id = google_id
                existing_user.avatar_url = picture
                await self.repository.update(existing_user)
                user = existing_user
            else:
                # Create new user
                user = User(
                    email=email,
                    name=name,
                    auth_provider=AuthProvider.GOOGLE,
                    google_id=google_id,
                    avatar_url=picture,
                )
                user = await self.repository.create(user)
                logger.info(f"New Google user registered: {user.email}")
        
        # Generate tokens
        tokens = self.create_tokens(user.id)
        
        return AuthResponse(
            user=self._to_user_response(user),
            tokens=tokens
        )
    
    # ============== Helpers ==============
    
    def _to_user_response(self, user: User) -> UserResponse:
        """
        Convert User model to UserResponse.
        
        Maps internal User model to public-facing UserResponse,
        excluding sensitive fields like password_hash.
        
        Args:
            user: Internal User model.
            
        Returns:
            UserResponse with public fields only.
        """
        return UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.name,
            auth_provider=user.auth_provider,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
        )
