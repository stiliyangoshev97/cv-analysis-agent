"""Authentication feature module."""

from .router import router as auth_router
from .service import AuthService
from .dependencies import get_current_user, get_current_user_optional

__all__ = [
    "auth_router",
    "AuthService",
    "get_current_user",
    "get_current_user_optional",
]
