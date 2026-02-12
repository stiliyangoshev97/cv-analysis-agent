"""User model and in-memory storage for authentication.

This module provides the User model and a temporary in-memory user store.
The storage layer will be replaced with PostgreSQL + SQLAlchemy in Phase 2.

Classes:
    AuthProvider: Enumeration of authentication methods.
    User: Pydantic model representing a user entity.
    UserStore: In-memory user storage with CRUD operations.

Example:
    Creating and storing a user::
    
        store = UserStore()
        user = User(
            email="user@example.com",
            full_name="John Doe",
            hashed_password="$2b$12$..."
        )
        stored_user = store.create(user)
        print(stored_user.id)  # usr_abc123...

Note:
    UserStore is a singleton pattern - use the global instance for
    consistency across the application.

Todo:
    - Phase 2: Replace UserStore with SQLAlchemy repository pattern
    - Phase 2: Add database migrations with Alembic
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class AuthProvider(str, Enum):
    """Authentication provider enumeration.
    
    Indicates the method used to authenticate a user. This is stored
    with the user record to handle provider-specific logic.
    
    Attributes:
        EMAIL: Traditional email/password authentication.
        GOOGLE: Google OAuth 2.0 authentication.
    
    Note:
        Additional providers (GitHub, LinkedIn) may be added in future.
    """
    EMAIL = "email"
    GOOGLE = "google"


class User(BaseModel):
    """User entity model.
    
    Represents a user in the CV Screening Agent system. Contains both
    authentication data and profile information.
    
    Attributes:
        id: Unique identifier (auto-generated, format: usr_xxxxx).
        email: User's email address (unique, used for login).
        full_name: User's display name.
        hashed_password: Bcrypt-hashed password (None for OAuth users).
        auth_provider: How the user authenticated (email/google).
        google_id: Google's unique user ID (for OAuth users).
        avatar_url: Profile picture URL (typically from OAuth provider).
        is_active: Whether the account is active (for soft-delete).
        created_at: Account creation timestamp (UTC).
        updated_at: Last modification timestamp (UTC).
    
    Example:
        >>> user = User(
        ...     email="recruiter@company.com",
        ...     full_name="Jane Smith",
        ...     hashed_password="$2b$12$..."
        ... )
        >>> print(user.id)  # usr_a1b2c3d4e5f6
    
    Note:
        Password is optional because OAuth users don't have passwords.
        The hashed_password field should NEVER contain plain text.
    """
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
    """In-memory user storage with CRUD operations.
    
    Provides dictionary-based storage for users with lookup indexes
    by email, ID, and Google ID. Thread-safe for single-process use.
    
    Attributes:
        _users: Primary store indexed by email (lowercase).
        _users_by_id: Secondary index by user ID.
        _google_users: Secondary index by Google ID.
    
    Example:
        >>> store = UserStore()
        >>> user = User(email="test@example.com", full_name="Test")
        >>> created = store.create(user)
        >>> retrieved = store.get_by_email("test@example.com")
        >>> assert created.id == retrieved.id
    
    Warning:
        Data is lost on application restart. This is intentional for
        development. Phase 2 will add persistent PostgreSQL storage.
    
    Note:
        All email lookups are case-insensitive (converted to lowercase).
    """
    
    def __init__(self) -> None:
        """Initialize empty user storage indexes."""
        self._users: dict[str, User] = {}  # email -> User
        self._users_by_id: dict[str, User] = {}  # id -> User
        self._google_users: dict[str, User] = {}  # google_id -> User
    
    def create(self, user: User) -> User:
        """Create a new user in the store.
        
        Adds the user to all relevant indexes (email, ID, and optionally
        Google ID).
        
        Args:
            user: The User instance to store.
        
        Returns:
            The stored User instance (same object).
        
        Note:
            Does not validate uniqueness - caller must check first.
        """
        self._users[user.email] = user
        self._users_by_id[user.id] = user
        if user.google_id:
            self._google_users[user.google_id] = user
        return user
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email address.
        
        Args:
            email: The email address to search for (case-insensitive).
        
        Returns:
            User instance if found, None otherwise.
        """
        return self._users.get(email.lower())
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve a user by their unique ID.
        
        Args:
            user_id: The user's ID (format: usr_xxxxx).
        
        Returns:
            User instance if found, None otherwise.
        """
        return self._users_by_id.get(user_id)
    
    def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Retrieve a user by their Google ID.
        
        Args:
            google_id: Google's unique user identifier.
        
        Returns:
            User instance if found, None otherwise.
        
        Note:
            Only returns users who authenticated via Google OAuth.
        """
        return self._google_users.get(google_id)
    
    def exists(self, email: str) -> bool:
        """Check if a user exists by email.
        
        Args:
            email: The email address to check (case-insensitive).
        
        Returns:
            True if a user with this email exists, False otherwise.
        """
        return email.lower() in self._users
    
    def update(self, user: User) -> User:
        """Update an existing user.
        
        Updates all indexes with the modified user data. Automatically
        sets the updated_at timestamp.
        
        Args:
            user: The User instance with updated fields.
        
        Returns:
            The updated User instance.
        
        Note:
            Caller must ensure the user exists before updating.
        """
        user.updated_at = datetime.utcnow()
        self._users[user.email] = user
        self._users_by_id[user.id] = user
        if user.google_id:
            self._google_users[user.google_id] = user
        return user


# Global user store instance
user_store = UserStore()
