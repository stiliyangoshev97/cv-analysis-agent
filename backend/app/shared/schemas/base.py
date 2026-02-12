"""Base schemas for API responses.

This module provides common response schemas used across all API
endpoints for consistent response formatting.

Classes:
    BaseResponse: Base class for all response schemas.
    ErrorResponse: Standard error response format.
    SuccessResponse: Simple success message response.
    PaginatedResponse: Paginated list response wrapper.

Example:
    Using base schemas in feature responses::
    
        from app.shared.schemas import SuccessResponse
        
        @router.delete("/items/{id}")
        async def delete_item(id: str) -> SuccessResponse:
            item_service.delete(id)
            return SuccessResponse(message="Item deleted successfully")
"""

from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional
from datetime import datetime

T = TypeVar("T")


class BaseResponse(BaseModel):
    """Base class for all API response schemas.
    
    Provides common configuration for response serialization.
    All response schemas should inherit from this class.
    
    Example:
        >>> class UserResponse(BaseResponse):
        ...     id: str
        ...     email: str
    """
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class ErrorResponse(BaseModel):
    """Standard error response format.
    
    Used for consistent error responses across all endpoints.
    
    Attributes:
        error: Error type or code.
        message: Human-readable error message.
        details: Optional additional error details.
        timestamp: When the error occurred.
    
    Example:
        >>> error = ErrorResponse(
        ...     error="ValidationError",
        ...     message="Invalid email format",
        ...     details={"field": "email"}
        ... )
    """
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the error occurred"
    )


class SuccessResponse(BaseModel):
    """Simple success message response.
    
    Used for operations that don't return data, like delete operations.
    
    Attributes:
        success: Always True for success responses.
        message: Success message describing what happened.
    
    Example:
        >>> response = SuccessResponse(message="Item deleted successfully")
    """
    success: bool = Field(default=True, description="Operation success status")
    message: str = Field(..., description="Success message")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response wrapper.
    
    Generic wrapper for paginated list responses. The type parameter T
    specifies the type of items in the list.
    
    Attributes:
        items: List of items for the current page.
        total: Total number of items across all pages.
        page: Current page number (1-indexed).
        page_size: Number of items per page.
        total_pages: Total number of pages.
        has_next: Whether there's a next page.
        has_prev: Whether there's a previous page.
    
    Example:
        >>> response = PaginatedResponse[UserResponse](
        ...     items=[user1, user2],
        ...     total=50,
        ...     page=1,
        ...     page_size=10
        ... )
    """
    items: list[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")
    
    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response with calculated fields.
        
        Args:
            items: Items for the current page.
            total: Total number of items.
            page: Current page number (1-indexed).
            page_size: Number of items per page.
        
        Returns:
            PaginatedResponse with calculated pagination fields.
        """
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
