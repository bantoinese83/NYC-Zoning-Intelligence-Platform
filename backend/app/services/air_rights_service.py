"""
Air rights transfer analysis business logic service.

Handles transferable development rights (TDR) analysis, including
unused FAR calculations and potential transfer recipients.
"""

import logging
from typing import Dict, List
from uuid import UUID

from sqlalchemy.orm import Session

from . import spatial_queries

logger = logging.getLogger(__name__)


def analyze_air_rights(property_id: UUID, session: Session) -> Dict:
    """
    Comprehensive air rights analysis for a property.

    Calculates unused FAR, transferable air rights value,
    and potential recipient properties.

    Args:
        property_id: Property identifier
        session: Database session

    Returns:
        Air rights analysis dictionary
    """
    logger.info(f"Analyzing air rights for property {property_id}")

    # Calculate unused FAR
    unused_far = calculate_transferable_far(property_id, session)

    # Find adjacent properties that could receive air rights
    recipients = find_air_rights_recipients(property_id, session)

    # Estimate market value
    tdr_price_per_sf = calculate_tdr_price(property_id, session)

    # Calculate total transferable square footage
    from ..models import Property

    property_obj = session.query(Property).filter_by(id=property_id).first()
    transferable_sf = unused_far * property_obj.land_area_sf if property_obj else 0
    estimated_value = transferable_sf * tdr_price_per_sf

    result = {
        "property_id": str(property_id),
        "unused_far": float(unused_far),
        "transferable_far": float(unused_far * 0.8),  # Assume 80% is transferable
        "transferable_sf": float(transferable_sf),
        "adjacent_properties": len(recipients),
        "potential_recipients": recipients[:5],  # Top 5 recipients
        "tdr_price_per_sf": tdr_price_per_sf,
        "estimated_value": float(estimated_value),
    }

    logger.debug(
        f"Air rights analysis complete for {property_id}: {unused_far:.2f} unused FAR"
    )
    return result


def calculate_transferable_far(property_id: UUID, session: Session) -> float:
    """
    Calculate unused FAR that could potentially be transferred.

    FAR Transfer = (Allowed FAR - Used FAR) if positive, else 0

    Args:
        property_id: Property identifier
        session: Database session

    Returns:
        Transferable FAR value
    """
    from ..models import Property

    property_obj = session.query(Property).filter_by(id=property_id).first()
    if not property_obj:
        return 0.0

    # Get zoning districts and calculate FAR
    from .spatial_queries import find_zoning_districts, calculate_far

    property_geom = spatial_queries.get_property_geometry(str(property_id), session)
    if not property_geom:
        return 0.0

    zoning_districts = find_zoning_districts(property_geom, session)
    far_analysis = calculate_far(str(property_id), zoning_districts, True, session)  # Use max FAR
    allowed_far = far_analysis.get("far_effective", 0)

    # Calculate current FAR usage
    current_far_used = property_obj.building_area_sf / property_obj.land_area_sf

    # Calculate unused FAR
    unused_far = max(0, allowed_far - current_far_used)

    return unused_far


def find_air_rights_recipients(property_id: UUID, session: Session) -> List[Dict]:
    """
    Find adjacent properties that could benefit from receiving air rights.

    Criteria for recipients:
    1. Adjacent to the source property (sharing boundary)
    2. Currently using less than maximum allowed FAR
    3. In zoning districts that allow additional development

    Args:
        property_id: Source property identifier
        session: Database session

    Returns:
        List of potential recipient properties with benefit analysis
    """
    from ..models import Property

    # Find adjacent properties
    adjacent_ids = spatial_queries.find_adjacent_properties(property_id, session)

    recipients = []
    for adj_id in adjacent_ids:
        adj_property = session.query(Property).filter_by(id=adj_id).first()
        if not adj_property:
            continue

        # Calculate how much additional FAR this property could use
        adj_geom = spatial_queries.get_property_geometry(str(adj_id), session)
        if not adj_geom:
            continue

        adj_zoning_districts = find_zoning_districts(adj_geom, session)
        adj_far_analysis = calculate_far(str(adj_id), adj_zoning_districts, True, session)  # Use max FAR
        adj_allowed_far = adj_far_analysis.get("far_effective", 0)
        adj_current_far = adj_property.building_area_sf / adj_property.land_area_sf
        additional_potential_far = max(0, adj_allowed_far - adj_current_far)

        if additional_potential_far > 0:
            # Calculate potential additional square footage
            additional_sf = additional_potential_far * adj_property.land_area_sf

            recipients.append(
                {
                    "property_id": str(adj_id),
                    "address": adj_property.address,
                    "current_far": float(adj_current_far),
                    "max_far": float(adj_allowed_far),
                    "additional_potential_far": float(additional_potential_far),
                    "additional_potential_sf": float(additional_sf),
                    "lot_area_sf": float(adj_property.land_area_sf),
                }
            )

    # Sort by potential additional square footage (descending)
    recipients.sort(key=lambda x: x["additional_potential_sf"], reverse=True)

    return recipients


def calculate_tdr_price(property_id: UUID, session: Session) -> float:
    """
    Estimate Transfer Development Rights price per square foot.

    NYC air rights prices vary by location and market conditions.
    Typical range: $100-400 per SF of transferable air rights.

    Args:
        property_id: Property identifier
        session: Database session

    Returns:
        Estimated price per square foot
    """
    from ..models import Property

    property_obj = session.query(Property).filter_by(id=property_id).first()
    if not property_obj:
        return 125.0  # Default NYC average

    # Get zoning districts to determine location premium
    zoning_districts = spatial_queries.find_zoning_districts(property_obj.geom, session)
    zone_codes = [d["district_code"] for d in zoning_districts]

    # Base price by zoning type
    base_price = 125.0  # NYC average

    # Premium for high-demand areas
    premium_zones = ["C5", "C6", "M1", "M2"]
    if any(code.startswith(prefix) for code in zone_codes for prefix in premium_zones):
        base_price *= 1.5  # 50% premium

    # Premium for Manhattan vs other boroughs
    # This would use geocoding to determine borough
    # For now, assume Manhattan premium
    manhattan_premium = 1.3
    base_price *= manhattan_premium

    return round(base_price, 2)


def simulate_air_rights_transfer(
    from_property_id: UUID,
    to_property_id: UUID,
    far_to_transfer: float,
    session: Session,
) -> Dict:
    """
    Simulate the impact of transferring air rights between properties.

    Args:
        from_property_id: Source property ID
        to_property_id: Recipient property ID
        far_to_transfer: Amount of FAR to transfer
        session: Database session

    Returns:
        Simulation results dictionary
    """
    from ..models import Property

    # Validate properties exist
    from_property = session.query(Property).filter_by(id=from_property_id).first()
    to_property = session.query(Property).filter_by(id=to_property_id).first()

    if not from_property or not to_property:
        raise ValueError("One or both properties not found")

    # Check if transfer is possible
    available_far = calculate_transferable_far(from_property_id, session)
    if far_to_transfer > available_far:
        raise ValueError(
            f"Transfer amount {far_to_transfer} exceeds available {available_far}"
        )

    # Calculate impact
    to_property_additional_area = far_to_transfer * to_property.land_area_sf
    to_property_new_area = to_property.building_area_sf + to_property_additional_area

    # Calculate values
    tdr_price = calculate_tdr_price(from_property_id, session)
    transfer_value = far_to_transfer * from_property.land_area_sf * tdr_price

    return {
        "transfer_possible": True,
        "far_transferred": far_to_transfer,
        "from_property": {
            "id": str(from_property_id),
            "address": from_property.address,
            "original_buildable_sf": from_property.building_area_sf,
            "remaining_buildable_sf": from_property.building_area_sf,
        },
        "to_property": {
            "id": str(to_property_id),
            "address": to_property.address,
            "original_buildable_sf": to_property.building_area_sf,
            "new_buildable_sf": to_property_new_area,
            "additional_sf": to_property_additional_area,
        },
        "transfer_value": transfer_value,
        "tdr_price_per_sf": tdr_price,
    }
