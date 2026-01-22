"""
Zoning API routes.

Handles zoning analysis, FAR calculations, and compliance checking.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import (
    FARCalculatorRequest,
    FARCalculatorResponse,
    ZoningAnalysisResponse,
    ZoningComplianceResponse,
    ZoningDistrictResponse,
)
from ..services import zoning_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/properties/{property_id}/zoning",
    response_model=ZoningAnalysisResponse,
    summary="Get property zoning analysis",
    description="""
    Get detailed zoning analysis for a property including:

    - Zoning districts with percentages
    - FAR calculations (base and with bonuses)
    - Maximum height restrictions
    - Setback requirements
    - Buildable area calculations
    """,
    tags=["zoning"],
)
async def get_property_zoning(property_id: UUID, db: Session = Depends(get_db)):
    """
    Get zoning analysis for a property.
    """
    try:
        logger.info(f"Getting zoning analysis for property {property_id}")

        analysis = zoning_service.analyze_property_zoning(property_id, db)

        # Convert to response schema
        response = ZoningAnalysisResponse(**analysis)

        return response

    except Exception as e:
        logger.error(f"Error getting zoning analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error getting zoning analysis: {str(e)}"
        )


@router.get(
    "/districts/{district_code}",
    response_model=ZoningDistrictResponse,
    summary="Get zoning district details",
    description="Get detailed information about a specific zoning district.",
    tags=["zoning"],
)
async def get_zoning_district(district_code: str, db: Session = Depends(get_db)):
    """
    Get zoning district by code.
    """
    from ..models import ZoningDistrict

    district = db.query(ZoningDistrict).filter_by(district_code=district_code).first()
    if not district:
        raise HTTPException(status_code=404, detail="Zoning district not found")

    return ZoningDistrictResponse.from_orm(district)


@router.post(
    "/far-calculator",
    response_model=FARCalculatorResponse,
    summary="Calculate FAR for zoning codes",
    description="""
    Calculate Floor Area Ratio for a given lot area and zoning districts.

    This calculator helps determine maximum buildable area based on:
    - Lot size
    - Zoning district codes
    - Whether to include City of Yes bonuses
    """,
    tags=["zoning"],
)
async def calculate_far(request: FARCalculatorRequest, db: Session = Depends(get_db)):
    """
    Calculate FAR based on zoning codes and lot area.
    """
    try:
        logger.info(
            f"Calculating FAR for {request.lot_area_sf} SF lot with zones: {request.zoning_codes}"
        )

        # This would be implemented as a service method
        # For now, return a simple calculation
        from decimal import Decimal

        # Simple FAR lookup (would be more sophisticated in production)
        far_lookup = {
            "R10": Decimal("10.0"),
            "R8": Decimal("8.0"),
            "R6": Decimal("6.0"),
            "C6-4": Decimal("6.0"),
            "M1-1": Decimal("5.0"),
        }

        # Find highest FAR among zones
        far_base = Decimal("2.0")  # Minimum fallback
        for code in request.zoning_codes:
            for zone_prefix, far_value in far_lookup.items():
                if code.startswith(zone_prefix):
                    far_base = max(far_base, far_value)
                    break

        # Apply bonuses if requested
        far_with_bonuses = far_base
        if request.include_bonuses:
            # City of Yes bonus (simplified)
            far_with_bonuses = far_base * Decimal("1.2")

        buildable_sf = float(far_with_bonuses * request.lot_area_sf)

        response = FARCalculatorResponse(
            far=float(far_with_bonuses), buildable_sf=buildable_sf
        )

        return response

    except Exception as e:
        logger.error(f"Error calculating FAR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error calculating FAR: {str(e)}")


@router.get(
    "/properties/{property_id}/zoning/compliance",
    response_model=ZoningComplianceResponse,
    summary="Check zoning compliance",
    description="""
    Validate if a proposed development complies with zoning regulations.

    Check proposed Floor Area Ratio and building height against
    zoning district requirements.
    """,
    tags=["zoning"],
)
async def check_zoning_compliance(
    property_id: UUID,
    proposed_far: float = Query(None, description="Proposed Floor Area Ratio"),
    proposed_height: int = Query(None, description="Proposed building height in feet"),
    db: Session = Depends(get_db),
):
    """
    Check if proposed development complies with zoning.
    """
    try:
        logger.info(f"Checking zoning compliance for property {property_id}")

        compliance = zoning_service.validate_zoning_compliance(
            property_id, proposed_far, proposed_height, db
        )

        response = ZoningComplianceResponse(**compliance)

        return response

    except Exception as e:
        logger.error(f"Error checking zoning compliance: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error checking zoning compliance: {str(e)}"
        )


@router.get(
    "/properties/{property_id}/setbacks",
    summary="Get property setback requirements",
    description="Get the strictest setback requirements from all zoning districts affecting the property.",
    tags=["zoning"],
)
async def get_property_setbacks(property_id: UUID, db: Session = Depends(get_db)):
    """
    Get setback requirements for a property.
    """
    try:
        logger.info(f"Getting setbacks for property {property_id}")

        setbacks = zoning_service.get_setback_requirements(property_id, db)

        return {"property_id": str(property_id), "setback_requirements": setbacks}

    except Exception as e:
        logger.error(f"Error getting setbacks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting setbacks: {str(e)}")
