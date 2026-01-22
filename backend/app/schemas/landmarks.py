"""
Landmark-related API schemas.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class LandmarkResponse(BaseModel):
    """Response model for individual landmark information."""

    id: str = Field(..., description="Landmark identifier")
    name: str = Field(..., description="Landmark name")
    landmark_type: str = Field(..., description="Type of landmark (historic, cultural, natural, etc.)")
    address: str = Field(..., description="Landmark address")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    designation_date: Optional[str] = Field(None, description="Date of landmark designation")
    description: Optional[str] = Field(None, description="Landmark description")
    significance: Optional[str] = Field(None, description="Historical or cultural significance")


class NearbyLandmarksResponse(BaseModel):
    """Response model for nearby landmarks search."""

    property_latitude: float = Field(..., description="Search center latitude")
    property_longitude: float = Field(..., description="Search center longitude")
    search_radius_ft: float = Field(..., description="Search radius in feet")
    landmarks: List[dict] = Field(default_factory=list, description="Nearby landmarks with distances")
    total_count: int = Field(..., description="Total number of nearby landmarks")