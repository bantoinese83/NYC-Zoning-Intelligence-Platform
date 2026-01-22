"""
FastAPI application entry point with all routes and middleware.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

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


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Logs the error and returns a standardized error response.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Create standardized error response
    error_response = ErrorResponse(
        error="internal_server_error",
        message="An unexpected error occurred. Please try again later.",
        details={"path": str(request.url), "method": request.method} if request else None,
        code="INTERNAL_ERROR"
    )

    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(),
    )


# Include API routes
app.include_router(api_router, prefix="/api", tags=["api"])

logger.info("API documentation available at: http://localhost:8000/docs")
logger.info(f"Application running in {settings.environment} mode")
