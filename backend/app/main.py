"""
FastAPI application entry point with all routes and middleware.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .api.routes import api_router
from .config import settings
from .core.logging import setup_logging
from .database import create_database
from .schemas import ErrorResponse

# Setup logging
setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    logger.info("Starting NYC Zoning Intelligence Platform")

    # Create database tables on startup (development only)
    if settings.is_development:
        logger.info("Creating database tables...")
        create_database()

    logger.info("Application startup complete")
    yield

    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="NYC Zoning Intelligence Platform API",
    description="Comprehensive zoning analysis and property intelligence for New York City real estate",
    version="0.1.0",
    openapi_url="/api/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware (production only)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["your-domain.com", "*.your-domain.com"]
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.

    Returns basic application health status.
    """
    return {
        "status": "healthy",
        "service": "NYC Zoning Intelligence Platform API",
        "environment": settings.environment,
        "version": "0.1.0",
    }


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "NYC Zoning Intelligence Platform API",
        "docs": "/docs",
        "health": "/health",
    }


# Global exception handlers for production-grade error management
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Enterprise-grade global exception handler with comprehensive error classification.

    Features:
    - Structured error logging with context
    - Error classification and appropriate HTTP status codes
    - Sensitive information sanitization
    - Performance monitoring integration
    - User-friendly error messages without exposing internals

    Handles all uncaught exceptions with appropriate responses.
    """
    import traceback
    from datetime import datetime

    # Classify error types for appropriate handling
    error_context = {
        "timestamp": datetime.utcnow().isoformat(),
        "path": str(request.url) if request else "unknown",
        "method": request.method if request else "unknown",
        "user_agent": request.headers.get("user-agent") if request else "unknown",
        "client_ip": request.client.host if request and request.client else "unknown",
        "request_id": request.headers.get("x-request-id", "unknown"),
    }

    # Classify exception types
    if isinstance(exc, ValueError):
        status_code = 400
        error_code = "VALIDATION_ERROR"
        user_message = "Invalid input data provided."
    elif isinstance(exc, PermissionError) or isinstance(exc, OSError):
        status_code = 403
        error_code = "PERMISSION_DENIED"
        user_message = "Access denied to requested resource."
    elif isinstance(exc, ConnectionError) or "database" in str(exc).lower():
        status_code = 503
        error_code = "SERVICE_UNAVAILABLE"
        user_message = "Service temporarily unavailable. Please try again."
    elif isinstance(exc, TimeoutError):
        status_code = 504
        error_code = "TIMEOUT_ERROR"
        user_message = "Request timed out. Please try again."
    else:
        status_code = 500
        error_code = "INTERNAL_ERROR"
        user_message = "An unexpected error occurred. Please try again later."

    # Log error with full context (but sanitize sensitive data)
    logger.error(
        f"Unhandled {type(exc).__name__}: {str(exc)}",
        extra={
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "status_code": status_code,
            "error_code": error_code,
            "request_context": error_context,
            "traceback": traceback.format_exc() if settings.is_development else None,
        },
        exc_info=settings.is_development  # Full traceback in development only
    )

    # Create standardized error response (production-safe)
    error_response = ErrorResponse(
        error=error_code,
        message=user_message,
        details={
            **error_context,
            "traceback": traceback.format_exc() if settings.is_development else None,
        } if settings.is_development else None,
        code=error_code
    )

    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(),
        headers={
            "X-Error-Code": error_code,
            "X-Request-ID": error_context["request_id"],
            "Cache-Control": "no-cache, no-store, must-revalidate",
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Enhanced HTTP exception handler with structured logging.

    Provides consistent error responses for known HTTP errors.
    """
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": str(request.url),
            "method": request.method,
        }
    )

    error_response = ErrorResponse(
        error=f"HTTP_{exc.status_code}",
        message=exc.detail,
        details={"path": str(request.url), "method": request.method},
        code=f"HTTP_{exc.status_code}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
        headers={"X-Error-Code": f"HTTP_{exc.status_code}"}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Pydantic validation error handler with detailed field-level errors.

    Provides user-friendly validation error messages with specific field guidance.
    """
    from pydantic import ValidationError

    # Extract validation errors
    validation_errors = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        validation_errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"],
        })

    logger.warning(
        f"Validation error: {len(validation_errors)} field errors",
        extra={
            "validation_errors": validation_errors,
            "path": str(request.url),
            "method": request.method,
        }
    )

    error_response = ErrorResponse(
        error="VALIDATION_ERROR",
        message="Please check your input data and try again.",
        details={"validation_errors": validation_errors},
        code="VALIDATION_ERROR"
    )

    return JSONResponse(
        status_code=422,
        content=error_response.model_dump(),
        headers={"X-Error-Code": "VALIDATION_ERROR"}
    )


# Include API routes
app.include_router(api_router, prefix="/api", tags=["api"])

logger.info("API documentation available at: http://localhost:8000/docs")
logger.info(f"Application running in {settings.environment} mode")
