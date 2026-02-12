"""Core module for shared infrastructure.

This module provides application-wide utilities and infrastructure that
are used across all features. Includes security utilities, exception
handling, and shared dependencies.

Modules:
    security: JWT token handling, password hashing utilities
    exceptions: Custom exception classes for API error handling
    dependencies: Shared FastAPI dependencies
"""

from .security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from .exceptions import (
    AppException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
)

__all__ = [
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    # Exceptions
    "AppException",
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
]
