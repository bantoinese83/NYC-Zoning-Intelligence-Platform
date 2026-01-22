"""
Tax incentive models for NYC programs like 467-M, ICAP, etc.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    Float,
    Integer,
    ForeignKey,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class TaxIncentiveProgram(Base):
    """Tax incentive program definitions."""

    __tablename__ = "tax_incentive_programs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)

    # Program information
    program_code = Column(String(20), nullable=False, unique=True, index=True)
    program_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Eligibility criteria
    eligible_zoning_districts = Column(
        JSON, nullable=True, default=list
    )  # List of zoning codes
    min_building_age = Column(Integer, nullable=True)  # Years since construction
    requires_residential = Column(Boolean, default=False)

    # Tax benefits
    tax_abatement_years = Column(Integer, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    property_applications = relationship(
        "PropertyTaxIncentive", back_populates="program", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<TaxIncentiveProgram(code='{self.program_code}', name='{self.program_name}')>"


class PropertyTaxIncentive(Base):
    """Junction table linking properties to tax incentive programs."""

    __tablename__ = "property_tax_incentives"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign keys
    property_id = Column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    program_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tax_incentive_programs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Application status
    is_eligible = Column(Boolean, default=False)
    eligibility_reason = Column(Text, nullable=True)

    # Financial information
    estimated_abatement_value = Column(Float, nullable=True)  # Annual savings

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    property = relationship("Property", back_populates="tax_incentives")
    program = relationship(
        "TaxIncentiveProgram", back_populates="property_applications"
    )

    def __repr__(self) -> str:
        return f"<PropertyTaxIncentive(property_id={self.property_id}, program='{self.program.program_code if self.program else None}', eligible={self.is_eligible})>"
