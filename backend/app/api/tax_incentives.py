"""
Tax incentives API routes.

Handles tax incentive eligibility checking and program information.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import (
    PropertyTaxIncentiveResponse,
    TaxIncentiveEligibilityResponse,
    TaxIncentiveProgramResponse,
)
from ..services import tax_incentive_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/properties/{property_id}/tax-incentives",
    response_model=TaxIncentiveEligibilityResponse,
    summary="Check tax incentive eligibility",
    description="""
    Check eligibility for all applicable NYC tax incentive programs.

    Analyzes property characteristics against program requirements for:
    - 467-M (Residential Conversion)
    - ICAP (Industrial & Commercial Abatement)
    - Other applicable programs
    """,
    tags=["tax-incentives"],
)
async def check_tax_incentive_eligibility(
    property_id: UUID, db: Session = Depends(get_db)
):
    """
    Check tax incentive eligibility for a property.
    """
    try:
        logger.info(f"Checking tax incentives for property {property_id}")

        # Check if property exists
        from ..models import Property

        property_obj = db.query(Property).filter_by(id=property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")

        # Get eligibility analysis
        eligibility_results = tax_incentive_service.check_tax_incentive_eligibility(
            property_id, db
        )

        # Calculate total savings
        total_savings = sum(
            result.get("estimated_abatement_value", 0)
            for result in eligibility_results
            if result.get("is_eligible")
        )

        # Convert to response schema
        incentives = []
        for result in eligibility_results:
            incentive = PropertyTaxIncentiveResponse(**result)
            incentives.append(incentive)

        response = TaxIncentiveEligibilityResponse(
            property_id=str(property_id),
            incentives=incentives,
            total_estimated_savings=total_savings if total_savings > 0 else None,
        )

        logger.info(
            f"Tax incentive check complete for {property_id}: {len(incentives)} programs analyzed"
        )
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking tax incentives: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error checking tax incentives: {str(e)}"
        )


@router.get(
    "/properties/{property_id}/tax-incentives/{program_code}",
    response_model=PropertyTaxIncentiveResponse,
    summary="Get detailed tax incentive information",
    description="""
    Get detailed eligibility information for a specific tax incentive program.

    Includes eligibility criteria, requirements, and benefit calculations.
    """,
    tags=["tax-incentives"],
)
async def get_tax_incentive_details(
    property_id: UUID, program_code: str, db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific tax incentive program.
    """
    try:
        logger.info(f"Getting {program_code} details for property {property_id}")

        # Get all eligibility results
        eligibility_results = tax_incentive_service.check_tax_incentive_eligibility(
            property_id, db
        )

        # Find the specific program
        program_result = None
        for result in eligibility_results:
            if result["program_code"] == program_code.upper():
                program_result = result
                break

        if not program_result:
            raise HTTPException(
                status_code=404,
                detail=f"Tax incentive program {program_code} not found",
            )

        response = PropertyTaxIncentiveResponse(**program_result)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tax incentive details: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error getting tax incentive details: {str(e)}"
        )


@router.get(
    "/tax-incentives/programs",
    response_model=list[TaxIncentiveProgramResponse],
    summary="List all tax incentive programs",
    description="Get information about all available NYC tax incentive programs.",
    tags=["tax-incentives"],
)
async def list_tax_incentive_programs(db: Session = Depends(get_db)):
    """
    List all tax incentive programs.
    """
    try:
        from ..models import TaxIncentiveProgram

        programs = (
            db.query(TaxIncentiveProgram)
            .order_by(TaxIncentiveProgram.program_name)
            .all()
        )

        results = [
            TaxIncentiveProgramResponse.from_orm(program) for program in programs
        ]

        return results

    except Exception as e:
        logger.error(f"Error listing tax incentive programs: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error listing tax incentive programs: {str(e)}"
        )


@router.get(
    "/tax-incentives/programs/{program_code}",
    response_model=TaxIncentiveProgramResponse,
    summary="Get tax incentive program details",
    description="Get detailed information about a specific tax incentive program.",
    tags=["tax-incentives"],
)
async def get_tax_incentive_program(program_code: str, db: Session = Depends(get_db)):
    """
    Get details about a specific tax incentive program.
    """
    from ..models import TaxIncentiveProgram

    program = (
        db.query(TaxIncentiveProgram)
        .filter_by(program_code=program_code.upper())
        .first()
    )

    if not program:
        raise HTTPException(status_code=404, detail="Tax incentive program not found")

    return TaxIncentiveProgramResponse.from_orm(program)
