"""
Landmark model for historic, cultural, and natural landmarks.
"""

from datetime import datetime
from uuid import uuid4

from geoalchemy2 import Geometry
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class Landmark(Base):
    """Landmark model for points of interest."""

    __tablename__ = "landmarks"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)

    # Landmark information
    name = Column(String(200), nullable=False, index=True)
    landmark_type = Column(
        String(50), nullable=False, index=True
    )  # historic, cultural, natural, transportation, religious, educational

    # Additional information
    description = Column(Text, nullable=True)

    # Spatial data - Point geometry for landmark location
    geom = Column(Geometry("POINT", srid=4326), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<Landmark(id={self.id}, name='{self.name}', type='{self.landmark_type}')>"
        )
