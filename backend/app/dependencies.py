"""
FastAPI dependency injection functions.

Provides common dependencies used across API endpoints.
"""

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .database import get_db


def get_database_session(db: Session = Depends(get_db)) -> Session:
    """
    Get database session dependency.

    This is the main database session dependency used by all endpoints
    that need database access.
    """
    return db


def get_current_user_optional(request: Request) -> str | None:
    """
    Get current user from request headers (optional).

    In a production system, this would validate JWT tokens or API keys.
    For now, it's a placeholder for future authentication.
    """
    # Check for API key in header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        # In production, validate API key against database
        # For now, accept any non-empty key
        if api_key.strip():
            return api_key

    # Check for Authorization header (Bearer token)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]  # Remove "Bearer " prefix
        if token.strip():
            # In production, validate JWT token
            return token

    # No authentication provided - return None for optional auth
    return None


def get_current_user(request: Request) -> str:
    """
    Get current user from request (required authentication).

    Raises HTTPException if no valid authentication is provided.
    """
    user = get_current_user_optional(request)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_api_key(request: Request) -> str:
    """
    Require API key authentication.

    This is a stricter version that requires an API key to be provided.
    """
    api_key = request.headers.get("X-API-Key")
    if not api_key or not api_key.strip():
        raise HTTPException(
            status_code=401,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # In production, validate API key against database/rate limits
    # For now, accept any non-empty key
    return api_key.strip()


def rate_limit_check(request: Request) -> None:
    """
    Rate limiting dependency.

    In production, this would check request rates against Redis or similar.
    For now, it's a placeholder that always allows requests.
    """
    # Placeholder rate limiting logic
    # In production:
    # - Check client IP or API key against rate limit store
    # - Increment request count
    # - Raise 429 if limit exceeded

    # Log for monitoring (in production, this would be metrics)
    # logger.info(f"Request from {client_ip}: {request.method} {request.url.path}")

    # For now, allow all requests
    pass


# Combined dependencies for common use cases
def get_db_with_auth(
    db: Session = Depends(get_database_session),
    user: str = Depends(get_current_user_optional),
) -> tuple[Session, str | None]:
    """
    Get database session with optional authentication.

    Returns tuple of (session, user_identifier)
    """
    return db, user


def get_db_with_required_auth(
    db: Session = Depends(get_database_session), user: str = Depends(get_current_user)
) -> tuple[Session, str]:
    """
    Get database session with required authentication.

    Returns tuple of (session, user_identifier)
    Raises 401 if not authenticated.
    """
    return db, user
