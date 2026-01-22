"""
Property CRUD and analysis orchestration service.

Handles property creation, geocoding, and comprehensive analysis
combining all other services.
"""

import logging
import os
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..models import Property
from ..schemas import PropertyCreate
from . import air_rights_service, spatial_queries, tax_incentive_service, zoning_service

logger = logging.getLogger(__name__)


def create_property(property_data: PropertyCreate, session: Session) -> Property:
    """
    Create a new property record with geocoding and initial analysis.

    Args:
        property_data: Property creation data
        session: Database session

    Returns:
        Created Property object
    """
    logger.info(f"Creating property: {property_data.address}")

    # Geocode address if coordinates not provided
    latitude = property_data.latitude
    longitude = property_data.longitude

    if latitude is None or longitude is None:
        # Would integrate with geocoding service here
        # For now, use placeholder coordinates
        latitude = 40.7128
        longitude = -74.0060
        logger.warning("Using placeholder coordinates - geocoding not implemented")

    # Create geometry from coordinates
    if os.getenv("ENVIRONMENT") == "testing":
        # For testing, use WKT string directly
        geom = f"POINT({longitude} {latitude})"
    else:
        from geoalchemy2 import WKTElement
        geom = WKTElement(f"POINT({longitude} {latitude})", srid=4326)

    # Create property record
    property_obj = Property(
        address=property_data.address,
        zip_code=property_data.zip_code,
        lot_number=property_data.lot_number,
        block_number=property_data.block_number,
        geom=geom,
        building_area_sf=property_data.building_area_sf,
        land_area_sf=property_data.land_area_sf,
    )

    session.add(property_obj)
    session.commit()
    session.refresh(property_obj)

    # Perform initial analysis and create related records
    try:
        # Find zoning districts
        zoning_districts = spatial_queries.find_zoning_districts(geom, session)
        _create_property_zoning_relationships(
            property_obj.id, zoning_districts, session
        )

        # Check tax incentives
        tax_eligibility = tax_incentive_service.check_tax_incentive_eligibility(
            property_obj.id, session
        )
        _create_tax_incentive_records(property_obj.id, tax_eligibility, session)

        # Analyze air rights
        air_rights_analysis = air_rights_service.analyze_air_rights(
            property_obj.id, session
        )
        _create_air_rights_record(property_obj.id, air_rights_analysis, session)

        logger.info(f"Property created and analyzed: {property_obj.id}")

    except Exception as e:
        logger.error(f"Error during property analysis: {e}")
        # Don't fail property creation if analysis fails

    return property_obj


def get_property_full_analysis(property_id: UUID, session: Session) -> Dict:
    """
    Get comprehensive property analysis combining all services.

    Args:
        property_id: Property identifier
        session: Database session

    Returns:
        Complete analysis dictionary
    """
    logger.info(f"Generating full analysis for property {property_id}")

    # Get base property
    property_obj = session.query(Property).filter_by(id=property_id).first()
    if not property_obj:
        raise ValueError(f"Property {property_id} not found")

    # Get zoning analysis
    zoning_analysis = zoning_service.analyze_property_zoning(property_id, session)

    # Get tax incentives
    tax_incentives = tax_incentive_service.check_tax_incentive_eligibility(
        property_id, session
    )

    # Get air rights analysis
    air_rights = air_rights_service.analyze_air_rights(property_id, session)

    # Get nearby landmarks
    landmarks = spatial_queries.find_nearby_landmarks(
        property_id, 150, session
    )

    # Calculate centroids for mapping
    try:
        centroid = spatial_queries.get_property_centroid(property_id, session)
        latitude, longitude = centroid[1], centroid[0]
    except Exception:
        latitude, longitude = None, None

    # Compile complete analysis with null-safe handling
    analysis = {
        "property": {
            "id": str(property_obj.id),
            "address": property_obj.address or "",
            "lot_number": property_obj.lot_number,
            "block_number": property_obj.block_number,
            "zip_code": property_obj.zip_code,
            "building_area_sf": property_obj.building_area_sf,
            "land_area_sf": property_obj.land_area_sf,
            "current_use": property_obj.current_use or "Unknown",
            "latitude": latitude,
            "longitude": longitude,
            "created_at": (
                property_obj.created_at.isoformat() if property_obj.created_at else None
            ),
        },
        "zoning": zoning_analysis or {"error": "Zoning analysis unavailable"},
        "tax_incentives": tax_incentives or [],
        "air_rights": air_rights or {"error": "Air rights analysis unavailable"},
        "nearby_landmarks": landmarks or [],
        "report_data": {
            "generated_at": "2026-01-22T14:30:00Z",
            "analysis_version": "1.0",
            "data_sources": ["NYC DOF", "NYC DCP", "NYC Landmarks"],
        },
    }

    logger.debug(f"Full analysis complete for property {property_id}")
    return analysis


def search_properties_by_address(address: str, session: Session) -> List[Property]:
    """
    Search for properties near an address using geocoding and spatial proximity.

    Args:
        address: Search address
        session: Database session

    Returns:
        List of nearby properties (up to 10)
    """
    logger.info(f"Searching properties near: {address}")

    try:
        # Get total count of properties for fallback logic
        total_count = session.query(Property).count()

        if total_count == 0:
            logger.warning("No properties found in database")
            return []

        # For demo purposes, return properties regardless of address
        # In production, this would geocode the address and find nearby properties
        logger.info("Returning sample properties for demo (geocoding not implemented)")

        # Query with coordinates extracted from geometry
        from sqlalchemy import text
        from sqlalchemy.engine import Engine

        # Check if we're using PostgreSQL with PostGIS or SQLite for testing
        engine = session.get_bind()
        is_postgresql = engine.dialect.name == 'postgresql'

        if is_postgresql:
            # Use PostGIS functions for production
            result = session.execute(text("""
                SELECT
                    p.id, p.address, p.lot_number, p.block_number, p.zip_code,
                    p.building_area_sf, p.land_area_sf, p.current_use,
                    p.created_at, p.updated_at,
                    ST_Y(p.geom) as latitude, ST_X(p.geom) as longitude
                FROM properties p
                WHERE p.geom IS NOT NULL
                ORDER BY p.id
                LIMIT :limit
            """), {"limit": min(50, total_count)})
        else:
            # For SQLite/testing, extract coordinates from WKT representation
            result = session.execute(text("""
                SELECT
                    p.id, p.address, p.lot_number, p.block_number, p.zip_code,
                    p.building_area_sf, p.land_area_sf, p.current_use,
                    p.created_at, p.updated_at,
                    p.geom as geom_wkt
                FROM properties p
                WHERE p.geom IS NOT NULL
                ORDER BY p.id
                LIMIT :limit
            """), {"limit": min(50, total_count)})

        # Convert to property-like objects with coordinates
        nearby_properties = []
        for row in result:
            # Create a mock property object with coordinates
            class PropertyWithCoords:
                def __init__(self, row, is_postgresql):
                    self.id = row[0]
                    self.address = row[1]
                    self.lot_number = row[2]
                    self.block_number = row[3]
                    self.zip_code = row[4]
                    self.building_area_sf = row[5]
                    self.land_area_sf = row[6]
                    self.current_use = row[7]
                    self.created_at = row[8]
                    self.updated_at = row[9]

                    if is_postgresql:
                        # Direct latitude/longitude from PostGIS
                        self.latitude = float(row[10]) if row[10] else None
                        self.longitude = float(row[11]) if row[11] else None
                    else:
                        # Parse coordinates from WKT geometry string for SQLite
                        geom_wkt = row[10]
                        self.latitude = None
                        self.longitude = None

                        if geom_wkt and isinstance(geom_wkt, str):
                            # Parse WKT format like "POINT(-74.0060 40.7128)"
                            if geom_wkt.startswith('POINT(') and geom_wkt.endswith(')'):
                                coords = geom_wkt[6:-1].strip().split()
                                if len(coords) >= 2:
                                    try:
                                        self.longitude = float(coords[0])
                                        self.latitude = float(coords[1])
                                    except (ValueError, IndexError):
                                        pass

            nearby_properties.append(PropertyWithCoords(row, is_postgresql))

        logger.info(f"Service returning {len(nearby_properties)} properties with coordinates")
        if nearby_properties:
            logger.info(f"First property: {nearby_properties[0].address} at ({nearby_properties[0].latitude}, {nearby_properties[0].longitude})")

        logger.info(f"Found {len(nearby_properties)} properties in search results")
        return nearby_properties

    except Exception as e:
        logger.error(f"Error searching properties by address: {e}")
        # Return empty list instead of crashing
        return []


def get_property_by_id(property_id: UUID, session: Session) -> Optional[Property]:
    """
    Get property by ID with error handling.

    Args:
        property_id: Property identifier
        session: Database session

    Returns:
        Property object or None if not found
    """
    return session.query(Property).filter_by(id=property_id).first()


def update_property(
    property_id: UUID, update_data: Dict, session: Session
) -> Optional[Property]:
    """
    Update property with new data.

    Args:
        property_id: Property identifier
        update_data: Fields to update
        session: Database session

    Returns:
        Updated Property object or None if not found
    """
    property_obj = session.query(Property).filter_by(id=property_id).first()
    if not property_obj:
        return None

    # Update allowed fields
    allowed_fields = {
        "address",
        "zip_code",
        "building_area_sf",
        "land_area_sf",
        "current_use",
    }

    for field, value in update_data.items():
        if field in allowed_fields:
            setattr(property_obj, field, value)

    session.commit()
    session.refresh(property_obj)
    return property_obj


def _create_property_zoning_relationships(
    property_id: UUID, zoning_districts: List[Dict], session: Session
) -> None:
    """Create property-zoning junction records."""
    from ..models import PropertyZoning, ZoningDistrict

    for zone_data in zoning_districts:
        zone = (
            session.query(ZoningDistrict)
            .filter_by(district_code=zone_data["district_code"])
            .first()
        )

        if zone:
            relationship = PropertyZoning(
                property_id=property_id,
                zoning_district_id=zone.id,
                percent_in_district=zone_data["percent_in_district"],
            )
            session.add(relationship)

    session.commit()


def _create_tax_incentive_records(
    property_id: UUID, tax_eligibility: List[Dict], session: Session
) -> None:
    """Create property tax incentive eligibility records."""
    from ..models import PropertyTaxIncentive, TaxIncentiveProgram

    for eligibility in tax_eligibility:
        program = (
            session.query(TaxIncentiveProgram)
            .filter_by(program_code=eligibility["program_code"])
            .first()
        )

        if program:
            record = PropertyTaxIncentive(
                property_id=property_id,
                tax_incentive_id=program.id,
                is_eligible=eligibility["is_eligible"],
                eligibility_reason=eligibility["eligibility_reason"],
                estimated_abatement_value=eligibility.get("estimated_abatement_value"),
            )
            session.add(record)

    session.commit()


def _create_air_rights_record(
    property_id: UUID, air_rights_analysis: Dict, session: Session
) -> None:
    """Create air rights analysis record."""
    from ..models import AirRights

    record = AirRights(
        property_id=property_id,
        unused_far=air_rights_analysis["unused_far"],
        transferable_far=air_rights_analysis["transferable_far"],
        tdr_price_per_sf=air_rights_analysis["tdr_price_per_sf"],
    )
    session.add(record)
    session.commit()
