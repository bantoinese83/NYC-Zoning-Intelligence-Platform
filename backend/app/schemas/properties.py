"""
Property-related API schemas.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class AddressSearchRequest(BaseModel):
    """Request model for property address search."""

    address: str = Field(..., description="Property address to search for")
    city: Optional[str] = Field(None, description="City filter")
    state: Optional[str] = Field(None, description="State filter")


class PropertyCreate(BaseModel):
    """Request model for creating a new property."""

    address: str = Field(..., description="Full property address")
    lot_number: Optional[str] = Field(None, description="Lot number")
    block_number: Optional[str] = Field(None, description="Block number")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    borough: Optional[str] = Field(None, description="Borough")
    neighborhood: Optional[str] = Field(None, description="Neighborhood")


class PropertyResponse(BaseModel):
    """Response model for property data."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique property identifier")
    address: str = Field(..., description="Full property address")
    lot_number: Optional[str] = Field(None, description="Lot number")
    block_number: Optional[str] = Field(None, description="Block number")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    borough: Optional[str] = Field(None, description="Borough")
    neighborhood: Optional[str] = Field(None, description="Neighborhood")
    building_area_sf: Optional[float] = Field(None, description="Building area in square feet")
    lot_area_sf: Optional[float] = Field(None, description="Lot area in square feet")
    year_built: Optional[int] = Field(None, description="Year the building was constructed")


class PropertyAnalysisResponse(BaseModel):
    """Response model for comprehensive property analysis."""

    model_config = ConfigDict(from_attributes=True)

    property: PropertyResponse = Field(..., description="Property details")
    zoning: dict = Field(..., description="Zoning analysis results")
    nearby_landmarks: list = Field(default_factory=list, description="Nearby landmarks")
    tax_incentives: list = Field(default_factory=list, description="Available tax incentives")
    air_rights: Optional[dict] = Field(None, description="Air rights information")