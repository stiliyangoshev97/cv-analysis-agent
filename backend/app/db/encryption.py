"""AES-256 encryption utilities for API key storage.

This module provides encryption and decryption functions for securely
storing user API keys in the database.

Uses Fernet (AES-128-CBC with HMAC) from the cryptography library,
which provides authenticated encryption.

Functions:
    encrypt_api_key: Encrypt an API key for storage.
    decrypt_api_key: Decrypt an API key from storage.
    generate_encryption_key: Generate a new encryption key.
    get_key_hint: Extract last 4 characters for display.

Example:
    Encrypting and storing an API key::
    
        from app.db.encryption import encrypt_api_key, decrypt_api_key
        
        # Encrypt for storage
        encrypted = encrypt_api_key("sk-ant-api-key-here")
        
        # Later, decrypt for use
        api_key = decrypt_api_key(encrypted)

Security Notes:
    - ENCRYPTION_KEY must be set in environment and kept secret
    - Keys are encrypted with AES-128-CBC + HMAC (Fernet)
    - Each encrypted value includes a timestamp
    - Never log decrypted API keys
"""

import base64
import secrets
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings


def generate_encryption_key() -> str:
    """Generate a new Fernet-compatible encryption key.
    
    Generates a URL-safe base64-encoded 32-byte key suitable for
    use as ENCRYPTION_KEY environment variable.
    
    Returns:
        Base64-encoded encryption key string.
    
    Example:
        >>> key = generate_encryption_key()
        >>> print(f"ENCRYPTION_KEY={key}")
        ENCRYPTION_KEY=abcd1234...
    
    Note:
        Run this once to generate your ENCRYPTION_KEY, then store
        it securely in your environment variables.
    """
    return Fernet.generate_key().decode()


def _get_fernet() -> Fernet:
    """Get Fernet instance with configured encryption key.
    
    Returns:
        Configured Fernet instance.
    
    Raises:
        ValueError: If ENCRYPTION_KEY is not configured.
    """
    settings = get_settings()
    
    if not settings.encryption_key:
        raise ValueError(
            "ENCRYPTION_KEY not configured. Generate one with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    
    return Fernet(settings.encryption_key.encode())


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for secure database storage.
    
    Uses Fernet (AES-128-CBC with HMAC) for authenticated encryption.
    The encrypted value includes a timestamp for optional rotation.
    
    Args:
        api_key: The plaintext API key to encrypt.
    
    Returns:
        Base64-encoded encrypted string.
    
    Raises:
        ValueError: If encryption key is not configured.
    
    Example:
        >>> encrypted = encrypt_api_key("sk-ant-api-key-here")
        >>> print(encrypted)
        gAAAAABh...
    """
    fernet = _get_fernet()
    encrypted_bytes = fernet.encrypt(api_key.encode())
    return encrypted_bytes.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key from database storage.
    
    Decrypts a Fernet-encrypted API key back to plaintext.
    
    Args:
        encrypted_key: Base64-encoded encrypted string from database.
    
    Returns:
        Plaintext API key.
    
    Raises:
        ValueError: If encryption key is not configured or decryption fails.
    
    Example:
        >>> api_key = decrypt_api_key(encrypted_value)
        >>> print(api_key)
        sk-ant-api-key-here
    
    Note:
        Never log the returned plaintext API key.
    """
    try:
        fernet = _get_fernet()
        decrypted_bytes = fernet.decrypt(encrypted_key.encode())
        return decrypted_bytes.decode()
    except InvalidToken:
        raise ValueError("Failed to decrypt API key. Key may be corrupted or encryption key changed.")


def get_key_hint(api_key: str) -> str:
    """Extract last 4 characters of API key for display.
    
    Creates a safe hint for displaying which key is configured
    without revealing the full key.
    
    Args:
        api_key: The plaintext API key.
    
    Returns:
        String in format "...XXXX" showing last 4 characters.
    
    Example:
        >>> get_key_hint("sk-ant-api-key-abc123xyz")
        "...xyz"
    """
    if len(api_key) < 4:
        return "****"
    return f"...{api_key[-4:]}"


def validate_encryption_key() -> bool:
    """Validate that encryption key is properly configured.
    
    Performs a round-trip encryption/decryption test to verify
    the encryption key works correctly.
    
    Returns:
        True if encryption key is valid and working.
    
    Raises:
        ValueError: If encryption key is missing or invalid.
    
    Example:
        >>> if validate_encryption_key():
        ...     print("Encryption configured correctly")
    """
    test_value = "test-api-key-validation"
    encrypted = encrypt_api_key(test_value)
    decrypted = decrypt_api_key(encrypted)
    return decrypted == test_value
