"""Core module for shared infrastructure.

This module provides application-wide utilities and infrastructure that
are used across all features. Includes security utilities, exception
handling, shared dependencies, and rate limiting.

Modules:
    security: JWT token handling, password hashing utilities
    exceptions: Custom exception classes for API error handling
    dependencies: Shared FastAPI dependencies
    rate_limit: Request rate limiting configuration
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
from .rate_limit import (
    limiter,
    auth_limiter,
    RateLimits,
    RATE_LIMIT_AUTH,
    RATE_LIMIT_UPLOAD,
    RATE_LIMIT_CHAT,
    RATE_LIMIT_DEFAULT,
    RATE_LIMIT_PUBLIC,
    RATE_LIMIT_NOTIFICATION_TEST,
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
    # Rate Limiting
    "limiter",
    "auth_limiter",
    "RateLimits",
    "RATE_LIMIT_AUTH",
    "RATE_LIMIT_UPLOAD",
    "RATE_LIMIT_CHAT",
    "RATE_LIMIT_DEFAULT",
    "RATE_LIMIT_PUBLIC",
    "RATE_LIMIT_NOTIFICATION_TEST",
]
