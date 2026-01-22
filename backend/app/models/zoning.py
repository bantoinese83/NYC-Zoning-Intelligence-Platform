"""
Zoning models for districts and property zoning relationships.
"""

from datetime import datetime
from uuid import uuid4

from geoalchemy2 import Geometry
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class ZoningDistrict(Base):
    """Zoning district model with spatial boundaries."""

    __tablename__ = "zoning_districts"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)

    # Zoning information
    district_code = Column(String(20), nullable=False, unique=True, index=True)
    district_name = Column(String(200), nullable=True)

    # Zoning regulations
    far_base = Column(Float, nullable=False)
    far_with_bonus = Column(Float, nullable=False)
    max_height_ft = Column(Float, nullable=True)

    # Setback requirements (stored as JSON)
    setback_requirements = Column(JSON, nullable=True, default=dict)

    # Additional zoning attributes
    building_class = Column(String(10), nullable=True)

    # Spatial data - MultiPolygon geometry for district boundaries
    geom = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    properties = relationship(
        "PropertyZoning", back_populates="zoning_district", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ZoningDistrict(code='{self.district_code}', name='{self.district_name}')>"


class PropertyZoning(Base):
    """Junction table linking properties to zoning districts."""

    __tablename__ = "property_zoning"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign keys
    property_id = Column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    zoning_district_id = Column(
        UUID(as_uuid=True),
        ForeignKey("zoning_districts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationship attributes
    percent_in_district = Column(Float, nullable=False)  # 0-100

    # Relationships
    property = relationship("Property", back_populates="zoning_districts")
    zoning_district = relationship("ZoningDistrict", back_populates="properties")

    def __repr__(self) -> str:
        return f"<PropertyZoning(property_id={self.property_id}, district='{self.zoning_district.district_code if self.zoning_district else None}', percent={self.percent_in_district})>"
