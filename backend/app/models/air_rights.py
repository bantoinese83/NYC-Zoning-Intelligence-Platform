"""
Air rights model for Transfer Development Rights (TDR).
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class AirRights(Base):
    """Air rights (unused FAR) available for transfer."""

    __tablename__ = "air_rights"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)

    # Foreign key to property
    property_id = Column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One air rights record per property
        index=True,
    )

    # Air rights calculations
    unused_far = Column(Float, nullable=False, default=0.0)
    transferable_far = Column(Float, nullable=False, default=0.0)

    # Market data
    tdr_price_per_sf = Column(Float, nullable=True)  # $/SF for air rights

    # Adjacent properties that could receive transferred rights
    adjacent_property_ids = Column(JSON, nullable=True, default=list)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    property = relationship("Property", back_populates="air_rights")

    def get_estimated_value(self) -> Optional[float]:
        """Calculate estimated market value of transferable air rights."""
        if self.transferable_far is None or self.tdr_price_per_sf is None:
            return None

        # This is a simplified calculation - actual value depends on many factors
        # In a real implementation, this would consider zoning bonuses, location, etc.
        return self.transferable_far * self.tdr_price_per_sf

    def __repr__(self) -> str:
        return f"<AirRights(property_id={self.property_id}, unused_far={self.unused_far}, transferable_far={self.transferable_far})>"
