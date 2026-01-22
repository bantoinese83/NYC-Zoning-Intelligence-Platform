"""
Landmark model for historic, cultural, and natural landmarks.
"""

import os
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base

# Conditionally import GeoAlchemy2 based on environment
if os.getenv("ENVIRONMENT") == "testing":
    # For testing, use Text column to store WKT geometry strings
    geom_column = Column(Text, nullable=True, index=True)
else:
    from geoalchemy2 import Geometry
    geom_column = Column(Geometry("POINT", srid=4326), nullable=True, index=True)


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
    geom = geom_column

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<Landmark(id={self.id}, name='{self.name}', type='{self.landmark_type}')>"
        )
