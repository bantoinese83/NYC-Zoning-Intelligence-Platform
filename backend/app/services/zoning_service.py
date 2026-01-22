"""
Zoning service for property zoning analysis and compliance.

This module provides functions for zoning district analysis, FAR calculations,
and zoning compliance validation.
"""

import logging
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy.orm import Session

from . import spatial_queries

logger = logging.getLogger(__name__)


def analyze_property_zoning(property_id: UUID, session: Session) -> Dict:
    """
    Analyze zoning information for a property.

    Args:
        property_id: Property identifier
        session: Database session

    Returns:
        Comprehensive zoning analysis
    """
    try:
        # Get property geometry
        geom = spatial_queries.get_property_geometry(str(property_id), session)
        if not geom:
            return {"error": "Property geometry not found"}

        # Find zoning districts
        districts = spatial_queries.find_zoning_districts(geom, session)

        # Calculate FAR
        far_analysis = spatial_queries.calculate_far(str(property_id), districts, False, session)

        return {
            "property_id": str(property_id),
            "zoning_districts": districts,
            "far_analysis": far_analysis,
            "district_count": len(districts)
        }

    except Exception as e:
        logger.error(f"Error analyzing property zoning: {e}")
        return {"error": str(e)}


def calculate_far_with_bonuses(
    property_id: str,
    base_far: float,
    zoning_districts: List[Dict],
    bonuses: Optional[List[Dict]] = None,
    session: Session = None
) -> Dict:
    """
    Calculate FAR including zoning bonuses.

    Args:
        property_id: Property identifier
        base_far: Base Floor Area Ratio
        zoning_districts: Zoning district information
        bonuses: List of applicable bonuses
        session: Database session (optional)

    Returns:
        FAR calculation with bonuses
    """
    try:
        total_bonus = 0.0

        if bonuses:
            for bonus in bonuses:
                total_bonus += bonus.get("far_increase", 0.0)

        effective_far = base_far + total_bonus

        return {
            "base_far": base_far,
            "total_bonus": total_bonus,
            "effective_far": effective_far,
            "bonuses_applied": bonuses or []
        }

    except Exception as e:
        logger.error(f"Error calculating FAR with bonuses: {e}")
        return {
            "base_far": base_far,
            "total_bonus": 0.0,
            "effective_far": base_far,
            "error": str(e)
        }


def validate_zoning_compliance(
    property_id: UUID,
    proposed_building_area_sf: float,
    zoning_districts: List[Dict],
    session: Session
) -> Dict:
    """
    Validate zoning compliance for a proposed development.

    Args:
        property_id: Property identifier
        proposed_building_area_sf: Proposed building area in square feet
        zoning_districts: Applicable zoning districts
        session: Database session

    Returns:
        Compliance validation results
    """
    try:
        # Get property geometry and calculate lot area
        geom = spatial_queries.get_property_geometry(str(property_id), session)
        if not geom:
            return {"compliant": False, "error": "Property geometry not found"}

        # Calculate lot area
        far_analysis = spatial_queries.calculate_far(str(property_id), zoning_districts, True, session)

        lot_area_sf = far_analysis.get("lot_area_sf", 0)
        max_allowable_area = far_analysis.get("allowable_building_area_sf", 0)

        is_compliant = proposed_building_area_sf <= max_allowable_area

        violations = []
        if not is_compliant:
            violations.append({
                "type": "building_area_exceeds_far",
                "description": f"Proposed building area ({proposed_building_area_sf:.0f} SF) exceeds maximum allowable ({max_allowable_area:.0f} SF)",
                "severity": "major"
            })

        return {
            "compliant": is_compliant,
            "proposed_building_area_sf": proposed_building_area_sf,
            "max_allowable_area_sf": max_allowable_area,
            "lot_area_sf": lot_area_sf,
            "violations": violations,
            "districts_checked": len(zoning_districts)
        }

    except Exception as e:
        logger.error(f"Error validating zoning compliance: {e}")
        return {
            "compliant": False,
            "error": str(e)
        }


def get_setback_requirements(property_id: UUID, session: Session) -> Dict:
    """
    Get setback requirements for a property.

    Args:
        property_id: Property identifier
        session: Database session

    Returns:
        Setback requirements dictionary
    """
    try:
        # Get property geometry
        geom = spatial_queries.get_property_geometry(str(property_id), session)
        if not geom:
            return {"error": "Property geometry not found"}

        # Find zoning districts
        districts = spatial_queries.find_zoning_districts(geom, session)

        # Extract setback requirements
        setbacks = {}
        for district in districts:
            district_setbacks = district.get("setbacks", {})
            for key, value in district_setbacks.items():
                if key not in setbacks or value > setbacks[key]:
                    setbacks[key] = value

        return {
            "property_id": str(property_id),
            "setbacks": setbacks,
            "zoning_districts": [d["code"] for d in districts],
            "units": "feet"
        }

    except Exception as e:
        logger.error(f"Error getting setback requirements: {e}")
        return {"error": str(e)}