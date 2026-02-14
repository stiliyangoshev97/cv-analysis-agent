"""Rate limiting configuration for the CV Screening Agent API.

This module provides tiered rate limiting using slowapi with different
limits based on endpoint type and authentication status.

Rate Limit Tiers:
    - Auth endpoints (unauthenticated): 5/minute - Prevent brute force
    - CV Upload (authenticated): 10/hour - Expensive AI processing
    - Chat/RAG (authenticated): 30/minute - LLM API costs
    - General API (authenticated): 100/minute - Fair usage
    - Public endpoints: 60/minute - Health checks, etc.

Key Functions:
    - get_user_identifier: Extracts user ID from JWT or falls back to IP
    - Custom rate limit decorators for each tier

Example:
    Apply rate limiting to a route::
    
        from app.core.rate_limit import limiter, RATE_LIMIT_AUTH
        
        @router.post("/login")
        @limiter.limit(RATE_LIMIT_AUTH)
        async def login(request: Request):
            ...

Note:
    Rate limits are stored in memory by default. For production with
    multiple workers, consider using Redis as a backend.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# Rate Limit Constants
# =============================================================================

# Auth endpoints - Strict limits to prevent brute force attacks
RATE_LIMIT_AUTH = "5/minute"

# CV Upload - Very expensive (AI processing + embeddings)
RATE_LIMIT_UPLOAD = "10/hour"

# Chat/RAG endpoints - Moderate limits (LLM API calls)
RATE_LIMIT_CHAT = "30/minute"

# General authenticated API calls
RATE_LIMIT_DEFAULT = "100/minute"

# Public endpoints (health checks, etc.)
RATE_LIMIT_PUBLIC = "60/minute"

# Test notifications - Prevent spam
RATE_LIMIT_NOTIFICATION_TEST = "5/hour"


# =============================================================================
# Key Functions
# =============================================================================

def get_user_identifier(request: Request) -> str:
    """Extract user identifier from request for rate limiting.
    
    This function attempts to identify the user by:
    1. Extracting user ID from JWT token (for authenticated users)
    2. Falling back to IP address (for unauthenticated users)
    
    Using user ID for authenticated users ensures that:
    - Rate limits are per-user, not per-IP
    - Users behind NAT/proxies get fair limits
    - Authenticated users can have higher limits
    
    Args:
        request: The FastAPI request object
        
    Returns:
        str: User ID (UUID) for authenticated users, IP address otherwise
        
    Example:
        Authenticated user: "user:550e8400-e29b-41d4-a716-446655440000"
        Unauthenticated: "ip:192.168.1.100"
    """
    # Try to get user from request state (set by auth middleware/dependencies)
    user = getattr(request.state, "user", None)
    if user and hasattr(user, "id"):
        return f"user:{user.id}"
    
    # Try to extract from Authorization header manually
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            from jose import jwt
            from ..config import get_settings
            
            token = auth_header.split(" ")[1]
            settings = get_settings()
            
            # Decode without verification just to get subject
            # Full verification happens in auth dependencies
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm],
                options={"verify_exp": False}  # Don't fail on expired for rate limiting
            )
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except Exception:
            # If token parsing fails, fall back to IP
            pass
    
    # Fall back to IP address
    return f"ip:{get_remote_address(request)}"


def get_ip_address(request: Request) -> str:
    """Get client IP address for unauthenticated rate limiting.
    
    Always uses IP address regardless of authentication status.
    Useful for auth endpoints where we want to limit by IP.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        str: Client IP address prefixed with "ip:"
    """
    return f"ip:{get_remote_address(request)}"


# =============================================================================
# Limiter Instance
# =============================================================================

# Create the main limiter instance
# Uses user identifier by default (user ID for authenticated, IP for anonymous)
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=[RATE_LIMIT_DEFAULT],
    headers_enabled=False,  # Don't require Response param in routes
)

# Separate limiter for auth endpoints (always uses IP)
auth_limiter = Limiter(
    key_func=get_ip_address,
    default_limits=[RATE_LIMIT_AUTH],
    headers_enabled=False,  # Don't require Response param in routes
)


# =============================================================================
# Exception Handler
# =============================================================================

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded errors.
    
    Returns a JSON response with details about the rate limit
    and when it resets.
    
    Args:
        request: The FastAPI request object
        exc: The RateLimitExceeded exception
        
    Returns:
        JSONResponse with 429 status and rate limit details
    """
    logger.warning(
        f"Rate limit exceeded: {request.url.path} - "
        f"Limit: {exc.detail} - "
        f"Client: {get_remote_address(request)}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "success": False,
            "error": "Rate limit exceeded",
            "detail": f"Too many requests. Limit: {exc.detail}",
            "retry_after": getattr(exc, "retry_after", None),
        },
        headers={
            "Retry-After": str(getattr(exc, "retry_after", 60)),
        }
    )


# =============================================================================
# Rate Limit Presets (for convenience)
# =============================================================================

class RateLimits:
    """Convenience class for applying rate limits.
    
    Example:
        @router.post("/upload")
        @RateLimits.upload()
        async def upload_cv(request: Request):
            ...
    """
    
    @staticmethod
    def auth():
        """Rate limit for auth endpoints (5/minute by IP)."""
        return auth_limiter.limit(RATE_LIMIT_AUTH)
    
    @staticmethod
    def upload():
        """Rate limit for CV upload (10/hour by user)."""
        return limiter.limit(RATE_LIMIT_UPLOAD)
    
    @staticmethod
    def chat():
        """Rate limit for chat/RAG endpoints (30/minute by user)."""
        return limiter.limit(RATE_LIMIT_CHAT)
    
    @staticmethod
    def default():
        """Default rate limit for authenticated endpoints (100/minute)."""
        return limiter.limit(RATE_LIMIT_DEFAULT)
    
    @staticmethod
    def public():
        """Rate limit for public endpoints (60/minute by IP)."""
        return limiter.limit(RATE_LIMIT_PUBLIC, key_func=get_ip_address)
    
    @staticmethod
    def notification_test():
        """Rate limit for test notifications (5/hour)."""
        return limiter.limit(RATE_LIMIT_NOTIFICATION_TEST)
