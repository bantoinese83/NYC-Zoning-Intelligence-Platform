"""
Property model with PostGIS geometry support.
"""

import os
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base

# Conditionally import GeoAlchemy2 based on environment
# For testing with SQLite, we use a simple Text column instead of Geometry
if os.getenv("ENVIRONMENT") == "testing":
    # For testing, use Text column to store WKT geometry strings
    geom_column = Column(Text, nullable=True, index=True)
else:
    from geoalchemy2 import Geometry
    geom_column = Column(Geometry("POINT", srid=4326), nullable=True, index=True)


class Property(Base):
    """Property model representing real estate parcels."""

    __tablename__ = "properties"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)

    # Basic property information
    address = Column(String(500), nullable=False, index=True)
    lot_number = Column(String(10), nullable=True)
    block_number = Column(String(10), nullable=True)
    zip_code = Column(String(10), nullable=True)

    # Property dimensions and area
    building_area_sf = Column(Float, nullable=True)
    land_area_sf = Column(Float, nullable=False)

    # Property characteristics
    current_use = Column(String(100), nullable=True)

    # Spatial data - Point geometry for property location
    geom = geom_column

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    zoning_districts = relationship(
        "PropertyZoning", back_populates="property", cascade="all, delete-orphan"
    )
    tax_incentives = relationship(
        "PropertyTaxIncentive", back_populates="property", cascade="all, delete-orphan"
    )
    air_rights = relationship(
        "AirRights",
        back_populates="property",
        cascade="all, delete-orphan",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<Property(id={self.id}, address='{self.address}')>"
