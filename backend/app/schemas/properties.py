"""
Property-related API schemas.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator


class AddressSearchRequest(BaseModel):
    """Request model for property address search."""

    address: str = Field(..., description="Property address to search for")
    city: Optional[str] = Field(None, description="City filter")
    state: Optional[str] = Field(None, description="State filter")


class PropertyCreate(BaseModel):
    """Request model for creating a new property."""

    address: str = Field(..., description="Full property address", min_length=1)
    lot_number: Optional[str] = Field(None, description="Lot number")
    block_number: Optional[str] = Field(None, description="Block number")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    borough: Optional[str] = Field(None, description="Borough")
    neighborhood: Optional[str] = Field(None, description="Neighborhood")
    building_area_sf: Optional[float] = Field(None, description="Building area in square feet")
    land_area_sf: Optional[float] = Field(None, description="Lot area in square feet")

    @field_validator('address')
    @classmethod
    def validate_address_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Address cannot be empty')
        return v.strip()


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
    current_use: Optional[str] = Field(None, description="Current property use")

    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to extract lat/lng from PostGIS geometry."""
        data = super().from_attributes(obj)

        # Extract coordinates from PostGIS geometry if available
        if hasattr(obj, 'geom') and obj.geom is not None:
            try:
                # For SQLAlchemy PostGIS geometries, we need to access the underlying data
                # The geom field contains a GeoAlchemy2 object
                if hasattr(obj.geom, 'x') and hasattr(obj.geom, 'y'):
                    # Direct access to coordinates (works with GeoAlchemy2)
                    data.longitude = float(obj.geom.x)
                    data.latitude = float(obj.geom.y)
                elif hasattr(obj.geom, 'data'):
                    # For WKTElement or other GeoAlchemy2 objects, try to parse coordinates
                    # This is a simplified approach for testing - in production we'd use PostGIS
                    geom_str = str(obj.geom)
                    if geom_str.startswith('POINT(') and geom_str.endswith(')'):
                        coords = geom_str[6:-1].split()
                        if len(coords) >= 2:
                            data.longitude = float(coords[0])
                            data.latitude = float(coords[1])
                # Note: PostGIS ST_X/ST_Y functions are not used here to maintain SQLite compatibility
            except Exception as e:
                # If extraction fails, leave as None
                pass

        return data


class PropertyAnalysisResponse(BaseModel):
    """Response model for comprehensive property analysis."""

    model_config = ConfigDict(from_attributes=True)

    property: PropertyResponse = Field(..., description="Property details")
    zoning: dict = Field(..., description="Zoning analysis results")
    nearby_landmarks: list = Field(default_factory=list, description="Nearby landmarks")
    tax_incentives: list = Field(default_factory=list, description="Available tax incentives")
    air_rights: Optional[dict] = Field(None, description="Air rights information")