"""Authentication feature module.

This module provides user authentication functionality including
registration, login, token management, and Google OAuth integration.

Architecture (Controller-Service-Model Pattern):
    - auth_routes.py: Route definitions (thin)
    - auth_controller.py: HTTP request/response handling
    - auth_service.py: Business logic
    - auth_schemas.py: Pydantic validation schemas
    - auth_models.py: User model and storage
    - auth_dependencies.py: FastAPI dependencies

Exports:
    auth_router: FastAPI router with all auth endpoints.
    AuthService: Service class for auth operations.
    get_current_user: Dependency for protected routes.
    get_current_user_optional: Dependency for optional auth.
"""

from .auth_routes import router as auth_router
from .auth_service import AuthService, auth_service
from .auth_dependencies import get_current_user, get_current_user_optional
from .auth_schemas import (
    AuthResponse,
    TokenResponse,
    UserResponse,
    RegisterRequest,
    LoginRequest,
)
from .auth_models import User, UserStore

__all__ = [
    # Router
    "auth_router",
    # Service
    "AuthService",
    "auth_service",
    # Dependencies
    "get_current_user",
    "get_current_user_optional",
    # Schemas
    "AuthResponse",
    "TokenResponse",
    "UserResponse",
    "RegisterRequest",
    "LoginRequest",
    # Models
    "User",
    "UserStore",
]
