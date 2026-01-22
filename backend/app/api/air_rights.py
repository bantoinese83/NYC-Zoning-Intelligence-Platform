"""
Air rights API routes.

Handles transferable development rights analysis and transfer simulations.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import AirRightsRecipientsResponse, AirRightsResponse
from ..services import air_rights_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/properties/{property_id}/air-rights",
    response_model=AirRightsResponse,
    summary="Analyze air rights potential",
    description="""
    Analyze air rights (transferable development rights) for a property.

    Calculates:
    - Unused FAR available for transfer
    - Transferable square footage
    - Market value estimates
    - Potential recipient properties
    """,
    tags=["air-rights"],
)
async def analyze_air_rights(property_id: UUID, db: Session = Depends(get_db)):
    """
    Analyze air rights for a property.
    """
    try:
        logger.info(f"Analyzing air rights for property {property_id}")

        # Check if property exists
        from ..models import Property

        property_obj = db.query(Property).filter_by(id=property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")

        # Get air rights analysis
        analysis = air_rights_service.analyze_air_rights(property_id, db)

        # Convert to response schema
        response = AirRightsResponse(**analysis)

        logger.info(
            f"Air rights analysis complete for {property_id}: {analysis['unused_far']:.2f} unused FAR"
        )
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing air rights: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error analyzing air rights: {str(e)}"
        )


@router.get(
    "/properties/{property_id}/air-rights/recipients",
    response_model=AirRightsRecipientsResponse,
    summary="Find potential air rights recipients",
    description="""
    Find adjacent properties that could benefit from receiving air rights.

    Criteria for recipients:
    - Share boundary with the source property
    - Have unused FAR capacity
    - Are in compatible zoning districts
    """,
    tags=["air-rights"],
)
async def get_air_rights_recipients(property_id: UUID, db: Session = Depends(get_db)):
    """
    Find potential recipients for air rights transfer.
    """
    try:
        logger.info(f"Finding air rights recipients for property {property_id}")

        # Check if property exists
        from ..models import Property

        property_obj = db.query(Property).filter_by(id=property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")

        # Get potential recipients
        recipients = air_rights_service.find_air_rights_recipients(property_id, db)

        # Convert to response format
        response = AirRightsRecipientsResponse(
            property_id=str(property_id),
            adjacent_properties=[
                {
                    "property_id": r["property_id"],
                    "address": r["address"],
                    "current_far": r["current_far"],
                    "max_far": r["max_far"],
                    "additional_potential_far": r["additional_potential_far"],
                    "additional_potential_sf": r["additional_potential_sf"],
                }
                for r in recipients
            ],
        )

        logger.info(
            f"Found {len(recipients)} potential recipients for property {property_id}"
        )
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding air rights recipients: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error finding air rights recipients: {str(e)}"
        )


@router.post(
    "/air-rights/simulate-transfer",
    summary="Simulate air rights transfer",
    description="""
    Simulate the impact of transferring air rights between two properties.

    Shows how the transfer would affect buildable area for both
    the sender and recipient properties.
    """,
    tags=["air-rights"],
)
async def simulate_air_rights_transfer(
    from_property_id: UUID,
    to_property_id: UUID,
    far_to_transfer: float,
    db: Session = Depends(get_db),
):
    """
    Simulate air rights transfer between properties.
    """
    try:
        logger.info(
            f"Simulating air rights transfer: {far_to_transfer} FAR from {from_property_id} to {to_property_id}"
        )

        # Perform simulation
        simulation = air_rights_service.simulate_air_rights_transfer(
            from_property_id, to_property_id, far_to_transfer, db
        )

        return simulation

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error simulating air rights transfer: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error simulating air rights transfer: {str(e)}"
        )


@router.get(
    "/air-rights/market-data",
    summary="Get air rights market data",
    description="""
    Get current market data for Transfer Development Rights (TDR).

    Includes average prices by zoning district and recent transactions.
    """,
    tags=["air-rights"],
)
async def get_air_rights_market_data(db: Session = Depends(get_db)):
    """
    Get market data for air rights transactions.
    """
    try:
        # This would integrate with market data sources
        # For now, return placeholder data
        market_data = {
            "average_price_per_sf": {
                "manhattan": 150.00,
                "brooklyn": 95.00,
                "queens": 85.00,
                "bronx": 75.00,
                "staten_island": 70.00,
            },
            "recent_transactions": [
                {
                    "date": "2026-01-15",
                    "borough": "Manhattan",
                    "price_per_sf": 175.00,
                    "far_transferred": 2.5,
                }
            ],
            "price_factors": [
                "Zoning district demand",
                "Proximity to subway",
                "Building age and condition",
                "Market absorption rate",
            ],
        }

        return market_data

    except Exception as e:
        logger.error(f"Error getting air rights market data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error getting air rights market data: {str(e)}"
        )
