"""Custom exception classes for API error handling.

This module provides custom exception classes that map to HTTP status codes.
These exceptions can be raised anywhere in the application and will be
caught by FastAPI's exception handlers.

Classes:
    AppException: Base exception for all application errors.
    BadRequestException: 400 Bad Request errors.
    UnauthorizedException: 401 Unauthorized errors.
    ForbiddenException: 403 Forbidden errors.
    NotFoundException: 404 Not Found errors.
    ConflictException: 409 Conflict errors.

Example:
    Raising exceptions in service layer::
    
        from app.core.exceptions import NotFoundException, BadRequestException
        
        def get_user(user_id: str) -> User:
            user = user_store.get_by_id(user_id)
            if not user:
                raise NotFoundException(f"User {user_id} not found")
            return user
        
        def create_user(email: str) -> User:
            if user_store.exists(email):
                raise BadRequestException("Email already registered")
            ...

Note:
    These exceptions extend FastAPI's HTTPException, so they are
    automatically converted to proper HTTP responses.
"""

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base exception for application errors.
    
    All custom exceptions should inherit from this class.
    Provides a consistent interface for error handling.
    
    Attributes:
        status_code: HTTP status code for the error.
        detail: Human-readable error message.
        headers: Optional headers to include in response.
    """
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict | None = None
    ) -> None:
        """Initialize the exception.
        
        Args:
            status_code: HTTP status code.
            detail: Error message.
            headers: Optional response headers.
        """
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class BadRequestException(AppException):
    """Exception for 400 Bad Request errors.
    
    Use when the client sends invalid data or the request
    cannot be processed due to client error.
    
    Example:
        >>> raise BadRequestException("Invalid email format")
    """
    
    def __init__(self, detail: str = "Bad request") -> None:
        """Initialize with 400 status code.
        
        Args:
            detail: Error message describing what's wrong.
        """
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(AppException):
    """Exception for 401 Unauthorized errors.
    
    Use when authentication is required but not provided,
    or when credentials are invalid.
    
    Example:
        >>> raise UnauthorizedException("Invalid token")
    """
    
    def __init__(self, detail: str = "Not authenticated") -> None:
        """Initialize with 401 status code.
        
        Args:
            detail: Error message.
        """
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(AppException):
    """Exception for 403 Forbidden errors.
    
    Use when the user is authenticated but doesn't have
    permission to perform the action.
    
    Example:
        >>> raise ForbiddenException("Admin access required")
    """
    
    def __init__(self, detail: str = "Access forbidden") -> None:
        """Initialize with 403 status code.
        
        Args:
            detail: Error message.
        """
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(AppException):
    """Exception for 404 Not Found errors.
    
    Use when a requested resource doesn't exist.
    
    Example:
        >>> raise NotFoundException(f"User {user_id} not found")
    """
    
    def __init__(self, detail: str = "Resource not found") -> None:
        """Initialize with 404 status code.
        
        Args:
            detail: Error message.
        """
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictException(AppException):
    """Exception for 409 Conflict errors.
    
    Use when the request conflicts with current state,
    such as duplicate entries.
    
    Example:
        >>> raise ConflictException("Email already registered")
    """
    
    def __init__(self, detail: str = "Resource conflict") -> None:
        """Initialize with 409 status code.
        
        Args:
            detail: Error message.
        """
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
