"""Security utilities for authentication and authorization.

This module provides core security functions used across the application
for password hashing, JWT token generation, and token validation.

Functions:
    hash_password: Hash a plaintext password using bcrypt.
    verify_password: Verify a password against its hash.
    create_access_token: Generate a short-lived JWT access token.
    create_refresh_token: Generate a long-lived JWT refresh token.
    decode_token: Decode and validate a JWT token.

Example:
    Hashing and verifying passwords::
    
        hashed = hash_password("mypassword123")
        is_valid = verify_password("mypassword123", hashed)
    
    Creating and decoding tokens::
    
        access_token = create_access_token(user_id="usr_123")
        payload = decode_token(access_token)
        print(payload["sub"])  # "usr_123"

Note:
    - Passwords are hashed using bcrypt with automatic salt generation.
    - bcrypt has a 72-byte limit; longer passwords are truncated.
    - JWTs are signed using the HS256 algorithm by default.
"""

from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import jwt, JWTError

from ..config import get_settings


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt.
    
    Uses bcrypt with automatic salt generation. Passwords longer than
    72 bytes are truncated (bcrypt limitation).
    
    Args:
        password: The plaintext password to hash.
    
    Returns:
        The bcrypt hash as a string.
    
    Example:
        >>> hashed = hash_password("securepass123")
        >>> hashed.startswith("$2b$")
        True
    """
    # bcrypt has a 72-byte limit
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash.
    
    Args:
        plain_password: The plaintext password to verify.
        hashed_password: The bcrypt hash to check against.
    
    Returns:
        True if the password matches, False otherwise.
    
    Example:
        >>> hashed = hash_password("mypassword")
        >>> verify_password("mypassword", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    password_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(user_id: str) -> str:
    """Create a short-lived JWT access token.
    
    The token contains the user ID in the 'sub' claim and expires
    based on the ACCESS_TOKEN_EXPIRE_MINUTES setting.
    
    Args:
        user_id: The user's unique identifier.
    
    Returns:
        Encoded JWT access token string.
    
    Example:
        >>> token = create_access_token("usr_abc123")
        >>> token.count(".")  # JWT has 3 parts separated by dots
        2
    """
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived JWT refresh token.
    
    The token contains the user ID in the 'sub' claim and expires
    based on the REFRESH_TOKEN_EXPIRE_DAYS setting.
    
    Args:
        user_id: The user's unique identifier.
    
    Returns:
        Encoded JWT refresh token string.
    
    Example:
        >>> token = create_refresh_token("usr_abc123")
        >>> payload = decode_token(token)
        >>> payload["type"]
        'refresh'
    """
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token.
    
    Verifies the token signature and expiration. Returns None if
    the token is invalid or expired.
    
    Args:
        token: The JWT token string to decode.
    
    Returns:
        The decoded payload dict if valid, None otherwise.
        Payload contains 'sub' (user_id), 'exp', and 'type'.
    
    Example:
        >>> token = create_access_token("usr_123")
        >>> payload = decode_token(token)
        >>> payload["sub"]
        'usr_123'
        >>> payload["type"]
        'access'
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None
