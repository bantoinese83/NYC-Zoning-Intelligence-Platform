"""
Main API router combining all sub-routers.

This file imports all API route modules and combines them into a single
router for the FastAPI application.
"""

from fastapi import APIRouter

from . import air_rights, landmarks, properties, reports, tax_incentives, zoning

# Create main API router
api_router = APIRouter()

# Include all sub-routers with appropriate prefixes
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])

api_router.include_router(zoning.router, prefix="/zoning", tags=["zoning"])

api_router.include_router(landmarks.router, prefix="/landmarks", tags=["landmarks"])

api_router.include_router(
    tax_incentives.router, prefix="/tax-incentives", tags=["tax-incentives"]
)

api_router.include_router(air_rights.router, prefix="/air-rights", tags=["air-rights"])

api_router.include_router(reports.router, prefix="/reports", tags=["reports"])


# Health check endpoint (could also be in a separate health router)
@api_router.get("/health")
async def api_health_check():
    """
    API health check endpoint.

    Returns the status of the API and basic version information.
    """
    return {
        "status": "healthy",
        "service": "NYC Zoning Intelligence Platform API",
        "version": "0.1.0",
        "endpoints": [
            "/properties",
            "/zoning",
            "/landmarks",
            "/tax-incentives",
            "/air-rights",
            "/reports",
        ],
    }
