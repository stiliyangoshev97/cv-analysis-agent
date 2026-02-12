"""
User model for in-memory storage (will be replaced with SQLAlchemy in Phase 2).
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class AuthProvider(str, Enum):
    """Authentication provider type."""
    EMAIL = "email"
    GOOGLE = "google"


class User(BaseModel):
    """User model for storage."""
    id: str = Field(default_factory=lambda: f"usr_{uuid.uuid4().hex[:12]}")
    email: EmailStr
    full_name: str
    hashed_password: Optional[str] = None  # None for OAuth users
    auth_provider: AuthProvider = AuthProvider.EMAIL
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ============== In-Memory Storage (temporary until Phase 2) ==============

class UserStore:
    """
    In-memory user storage.
    Will be replaced with PostgreSQL in Phase 2.
    """
    
    def __init__(self):
        self._users: dict[str, User] = {}  # email -> User
        self._users_by_id: dict[str, User] = {}  # id -> User
        self._google_users: dict[str, User] = {}  # google_id -> User
    
    def create(self, user: User) -> User:
        """Create a new user."""
        self._users[user.email] = user
        self._users_by_id[user.id] = user
        if user.google_id:
            self._google_users[user.google_id] = user
        return user
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self._users.get(email.lower())
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self._users_by_id.get(user_id)
    
    def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        return self._google_users.get(google_id)
    
    def exists(self, email: str) -> bool:
        """Check if user exists by email."""
        return email.lower() in self._users
    
    def update(self, user: User) -> User:
        """Update an existing user."""
        user.updated_at = datetime.utcnow()
        self._users[user.email] = user
        self._users_by_id[user.id] = user
        if user.google_id:
            self._google_users[user.google_id] = user
        return user


# Global user store instance
user_store = UserStore()
