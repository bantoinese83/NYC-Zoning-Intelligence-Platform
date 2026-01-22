"""
Security utilities and authentication helpers.

Provides functions for API key validation, rate limiting, and security headers.
"""

import hashlib
import hmac
import secrets
from datetime import timedelta
from typing import Optional, Tuple

from ..config import settings


def generate_api_key() -> str:
    """
    Generate a secure API key.

    Returns a cryptographically secure random API key.
    """
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage.

    Uses SHA-256 with a salt for secure storage in database.
    """
    salt = settings.secret_key.encode()
    return hashlib.sha256(api_key.encode() + salt).hexdigest()


def verify_api_key(provided_key: str, stored_hash: str) -> bool:
    """
    Verify an API key against its stored hash.

    Args:
        provided_key: The API key provided by the client
        stored_hash: The hashed version stored in database

    Returns:
        True if the key is valid, False otherwise
    """
    expected_hash = hash_api_key(provided_key)
    return hmac.compare_digest(expected_hash, stored_hash)


def generate_jwt_token(user_id: str, expires_in: timedelta = None) -> str:
    """
    Generate a JWT token for user authentication.

    Args:
        user_id: User identifier
        expires_in: Token expiration time (default: 24 hours)

    Returns:
        JWT token string
    """
    if expires_in is None:
        expires_in = timedelta(hours=24)

    # In production, use a proper JWT library like PyJWT
    # For now, return a placeholder
    import jwt
    import time

    payload = {
        "user_id": user_id,
        "exp": int(time.time()) + int(expires_in.total_seconds()),
        "iat": int(time.time()),
    }

    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    return token


def verify_jwt_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload if valid, None if invalid
    """
    try:
        import jwt

        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def check_rate_limit(
    identifier: str, max_requests: int = None, window_seconds: int = 60
) -> Tuple[bool, int]:
    """
    Check if a request exceeds rate limits.

    Args:
        identifier: Unique identifier (IP, API key, user ID)
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds

    Returns:
        Tuple of (allowed: bool, remaining_requests: int)
    """
    if max_requests is None:
        max_requests = settings.rate_limit_requests_per_minute

    # In production, this would check Redis or similar
    # For now, return unlimited (always allowed)
    return True, max_requests


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Truncate to max length
    text = text[:max_length]

    # Remove potentially dangerous characters
    # This is a basic implementation - in production use bleach or similar
    dangerous_chars = ["<", ">", "&", '"', "'"]
    for char in dangerous_chars:
        text = text.replace(char, "")

    return text.strip()


def validate_request_origin(origin: str) -> bool:
    """
    Validate request origin against allowed origins.

    Args:
        origin: Request origin header

    Returns:
        True if origin is allowed, False otherwise
    """
    if not origin:
        return False

    allowed_origins = settings.allowed_origins

    # Check exact match
    if origin in allowed_origins:
        return True

    # Check if origin matches any pattern (e.g., localhost with different ports)
    for allowed in allowed_origins:
        if allowed.startswith("http://localhost") and origin.startswith(
            "http://localhost"
        ):
            return True
        if allowed.startswith("https://localhost") and origin.startswith(
            "https://localhost"
        ):
            return True

    return False


def generate_request_id() -> str:
    """
    Generate a unique request ID for tracing.

    Returns a secure random identifier for request tracing.
    """
    return secrets.token_hex(8)


def add_security_headers(response) -> None:
    """
    Add security headers to HTTP response.

    Args:
        response: FastAPI response object
    """
    headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'",
    }

    # Add headers to response
    for key, value in headers.items():
        response.headers[key] = value


def validate_file_upload(filename: str, content_type: str) -> bool:
    """
    Validate uploaded file for security.

    Args:
        filename: Original filename
        content_type: MIME content type

    Returns:
        True if file is safe to accept, False otherwise
    """
    # Check file extension
    allowed_extensions = {".pdf", ".txt", ".json", ".csv"}
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        return False

    # Check content type
    allowed_types = {"application/pdf", "text/plain", "application/json", "text/csv"}
    if content_type not in allowed_types:
        return False

    # Additional checks could include file size limits, virus scanning, etc.
    return True
