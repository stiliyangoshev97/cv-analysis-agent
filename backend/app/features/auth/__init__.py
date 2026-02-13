"""Authentication feature module.

This module provides user authentication functionality including
registration, login, token management, and Google OAuth integration.

Architecture (Controller-Service-Repository Pattern):
    - auth_routes.py: Route definitions (thin)
    - auth_controller.py: HTTP request/response handling
    - auth_service.py: Business logic
    - auth_repository.py: Database operations
    - auth_schemas.py: Pydantic validation schemas
    - auth_dependencies.py: FastAPI dependencies

Database Models:
    User model is centralized in app.db.models.user

Exports:
    auth_router: FastAPI router with all auth endpoints.
    AuthService: Service class for auth operations.
    UserRepository: Repository class for user database operations.
    get_current_user: Dependency for protected routes.
    get_current_user_optional: Dependency for optional auth.
"""

from .auth_routes import router as auth_router
from .auth_service import AuthService
from .auth_repository import UserRepository
from .auth_dependencies import get_current_user, get_current_user_optional
from .auth_schemas import (
    AuthResponse,
    TokenResponse,
    UserResponse,
    RegisterRequest,
    LoginRequest,
)

__all__ = [
    # Router
    "auth_router",
    # Service
    "AuthService",
    # Repository
    "UserRepository",
    # Dependencies
    "get_current_user",
    "get_current_user_optional",
    # Schemas
    "AuthResponse",
    "TokenResponse",
    "UserResponse",
    "RegisterRequest",
    "LoginRequest",
]
