"""Authentication dependencies for FastAPI route protection.

This module provides FastAPI dependencies for extracting and validating
the current user from JWT Bearer tokens. These dependencies can be
injected into route handlers to protect endpoints.

Dependencies:
    get_current_user: Requires authentication, raises 401 if invalid.
    get_current_user_optional: Returns None if not authenticated.

Example:
    Protecting a route with required authentication::
    
        @router.get("/profile")
        async def get_profile(
            current_user: User = Depends(get_current_user)
        ) -> UserResponse:
            return UserResponse.from_orm(current_user)
    
    Optional authentication for public routes with user context::
    
        @router.get("/items")
        async def list_items(
            current_user: Optional[User] = Depends(get_current_user_optional)
        ) -> list[Item]:
            if current_user:
                # Show personalized items
                pass
            return []

Note:
    Uses HTTPBearer security scheme which expects the Authorization
    header in format: "Bearer <token>"
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .auth_service import auth_service
from .auth_models import User

# HTTP Bearer token security scheme for OpenAPI docs
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Dependency to get the current authenticated user.
    
    Extracts the JWT from the Authorization header, validates it,
    and returns the corresponding User object.
    
    Args:
        credentials: Automatically injected by FastAPI from the
            Authorization header.
    
    Returns:
        The authenticated User instance.
    
    Raises:
        HTTPException: 401 Unauthorized if:
            - No Authorization header provided
            - Token is invalid or expired
            - Token type is not "access"
            - User not found in database
        HTTPException: 403 Forbidden if user account is deactivated.
    
    Example:
        >>> @router.get("/me")
        ... async def get_me(user: User = Depends(get_current_user)):
        ...     return {"email": user.email}
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = auth_service.decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Dependency to optionally get the current authenticated user.
    
    Unlike get_current_user, this dependency does not raise errors
    if authentication fails. It returns None instead, allowing
    routes to work for both authenticated and anonymous users.
    
    Args:
        credentials: Automatically injected by FastAPI from the
            Authorization header (may be None).
    
    Returns:
        The authenticated User instance if valid token provided,
        None otherwise.
    
    Example:
        >>> @router.get("/public")
        ... async def public_endpoint(
        ...     user: Optional[User] = Depends(get_current_user_optional)
        ... ):
        ...     if user:
        ...         return {"message": f"Hello, {user.full_name}!"}
        ...     return {"message": "Hello, guest!"}
    
    Note:
        Use this for public endpoints that behave differently when
        a user is logged in (e.g., showing a personalized greeting).
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = auth_service.decode_token(token)
        
        if not payload or payload.get("type") != "access":
            return None
        
        user_id = payload.get("sub")
        user = auth_service.get_user_by_id(user_id)
        
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None
