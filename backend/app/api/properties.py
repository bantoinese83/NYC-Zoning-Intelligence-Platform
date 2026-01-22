"""
Properties API routes.

Handles property search, analysis, and CRUD operations.
"""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import (
    AddressSearchRequest,
    PropertyAnalysisResponse,
    PropertyCreate,
    PropertyResponse,
    ErrorResponse,
    NotFoundErrorResponse,
    ValidationErrorResponse,
)
from ..services import property_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/analyze",
    response_model=PropertyAnalysisResponse,
    summary="Analyze property by address",
    description="""
    Analyze a NYC property by address and return comprehensive zoning,
    tax incentive, air rights, and landmark information.

    This endpoint:
    1. Geocodes the address (or uses provided coordinates)
    2. Creates/finds the property record
    3. Performs zoning analysis
    4. Checks tax incentive eligibility
    5. Analyzes air rights potential
    6. Finds nearby landmarks
    """,
    tags=["properties"],
)
async def analyze_property(
    property_data: PropertyCreate, db: Session = Depends(get_db)
):
    """
    Analyze a property and return complete zoning intelligence.
    """
    try:
        logger.info(f"Analyzing property: {property_data.address}")

        # Create property record and perform analysis
        property_obj = property_service.create_property(property_data, db)

        # Get full analysis
        analysis = property_service.get_property_full_analysis(property_obj.id, db)

        # Convert to response schema
        from ..schemas import PropertyAnalysisResponse

        response = PropertyAnalysisResponse(**analysis)

        logger.info(f"Analysis complete for property {property_obj.id}")
        return response

    except Exception as e:
        logger.error(f"Error analyzing property: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error analyzing property: {str(e)}"
        )


@router.get(
    "/search",
    response_model=List[PropertyResponse],
    summary="Search properties by address",
    description="""
    Search for NYC properties near a given address.

    Returns up to 10 properties within 50 feet of the search location.
    Uses geocoding to convert addresses to coordinates.
    """,
    tags=["properties"],
)
async def search_properties(
    address: str = Query(..., description="Address to search for", min_length=1, max_length=200),
    city: str = Query("New York", description="City name", min_length=1, max_length=100),
    state: str = Query("NY", description="State code (must be NY)", min_length=2, max_length=2),
    db: Session = Depends(get_db),
):
    """
    Search properties by address.
    """
    try:
        # Validate and sanitize input
        if not address or not address.strip():
            raise HTTPException(
                status_code=400,
                detail=ValidationErrorResponse(
                    message="Address is required",
                    details={"address": "Address cannot be empty"}
                ).model_dump()
            )

        if state.upper() != "NY":
            raise HTTPException(
                status_code=400,
                detail=ValidationErrorResponse(
                    message="Only New York State properties are supported",
                    details={"state": "State must be NY"}
                ).model_dump()
            )

        # Validate request
        search_request = AddressSearchRequest(
            address=address.strip(),
            city=city.strip(),
            state=state.upper()
        )

        logger.info(f"Searching properties near: {search_request.address}")

        # Perform search
        properties = property_service.search_properties_by_address(
            f"{search_request.address}, {search_request.city}, {search_request.state}",
            db,
        )

        # Convert to response schemas
        results = []
        for prop in properties:
            try:
                results.append(PropertyResponse.from_orm(prop))
            except Exception as conversion_error:
                logger.warning(f"Failed to convert property {prop.id} to response schema: {conversion_error}")
                continue

        logger.info(f"Found {len(results)} properties near search location")
        return results

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error searching properties: {e}", exc_info=True)
        error_response = ErrorResponse(
            error="search_error",
            message="Failed to search properties. Please try again.",
            details={"original_error": str(e)},
            code="SEARCH_ERROR"
        )
        raise HTTPException(status_code=500, detail=error_response.model_dump())


@router.get(
    "/{property_id}",
    response_model=PropertyResponse,
    summary="Get property details",
    description="Retrieve basic information about a specific property.",
    tags=["properties"],
)
async def get_property(property_id: UUID, db: Session = Depends(get_db)):
    """
    Get property by ID.
    """
    property_obj = property_service.get_property_by_id(property_id, db)
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    return PropertyResponse.from_orm(property_obj)


@router.get(
    "/{property_id}/analysis",
    response_model=PropertyAnalysisResponse,
    summary="Get complete property analysis",
    description="""
    Get comprehensive analysis for an existing property including:

    - Zoning districts and FAR calculations
    - Tax incentive eligibility
    - Air rights analysis
    - Nearby landmarks
    - Development potential
    """,
    tags=["properties"],
)
async def get_property_analysis(property_id: UUID, db: Session = Depends(get_db)):
    """
    Get complete analysis for a property.
    """
    try:
        logger.info(f"Getting analysis for property {property_id}")

        # Check if property exists first
        property_obj = property_service.get_property_by_id(property_id, db)
        if not property_obj:
            error_response = NotFoundErrorResponse(
                message=f"Property with ID {property_id} not found",
                details={"property_id": str(property_id)},
                code="PROPERTY_NOT_FOUND"
            )
            raise HTTPException(status_code=404, detail=error_response.model_dump())

        analysis = property_service.get_property_full_analysis(property_id, db)

        # Convert to response schema
        from ..schemas import PropertyAnalysisResponse

        try:
            response = PropertyAnalysisResponse(**analysis)
        except Exception as conversion_error:
            logger.error(f"Failed to convert analysis to response schema: {conversion_error}")
            error_response = ErrorResponse(
                error="response_conversion_error",
                message="Failed to format analysis results",
                details={"conversion_error": str(conversion_error)},
                code="CONVERSION_ERROR"
            )
            raise HTTPException(status_code=500, detail=error_response.model_dump())

        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        error_response = NotFoundErrorResponse(
            message=str(e),
            details={"property_id": str(property_id)},
            code="PROPERTY_NOT_FOUND"
        )
        raise HTTPException(status_code=404, detail=error_response.model_dump())
    except Exception as e:
        logger.error(f"Error getting property analysis: {e}", exc_info=True)
        error_response = ErrorResponse(
            error="analysis_error",
            message="Failed to generate property analysis. Please try again.",
            details={"property_id": str(property_id), "original_error": str(e)},
            code="ANALYSIS_ERROR"
        )
        raise HTTPException(status_code=500, detail=error_response.model_dump())
