"""
Zoning-related API schemas.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class FARCalculatorRequest(BaseModel):
    """Request model for FAR calculation."""

    zoning_district: str = Field(..., description="Zoning district code")
    lot_area_sf: float = Field(..., description="Lot area in square feet")
    existing_building_area_sf: Optional[float] = Field(None, description="Existing building area in square feet")


class FARCalculatorResponse(BaseModel):
    """Response model for FAR calculation."""

    zoning_district: str = Field(..., description="Zoning district code")
    base_far: float = Field(..., description="Base Floor Area Ratio")
    maximum_far: float = Field(..., description="Maximum Floor Area Ratio")
    allowable_building_area_sf: float = Field(..., description="Allowable building area in square feet")
    lot_area_sf: float = Field(..., description="Lot area in square feet")
    calculations: dict = Field(..., description="Detailed calculation breakdown")


class ZoningDistrictResponse(BaseModel):
    """Response model for zoning district information."""

    code: str = Field(..., description="Zoning district code")
    name: str = Field(..., description="Zoning district name")
    base_far: float = Field(..., description="Base Floor Area Ratio")
    max_far: float = Field(..., description="Maximum Floor Area Ratio")
    max_height_ft: Optional[float] = Field(None, description="Maximum building height in feet")
    setbacks: dict = Field(..., description="Setback requirements")
    use_groups: List[str] = Field(..., description="Allowed use groups")


class ZoningComplianceResponse(BaseModel):
    """Response model for zoning compliance check."""

    property_id: str = Field(..., description="Property identifier")
    zoning_district: str = Field(..., description="Zoning district code")
    is_compliant: bool = Field(..., description="Whether the property is zoning compliant")
    violations: List[dict] = Field(default_factory=list, description="List of zoning violations")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")


class ZoningAnalysisResponse(BaseModel):
    """Response model for comprehensive zoning analysis."""

    zoning_districts: List[ZoningDistrictResponse] = Field(..., description="Applicable zoning districts")
    far_analysis: FARCalculatorResponse = Field(..., description="FAR calculation results")
    compliance: ZoningComplianceResponse = Field(..., description="Compliance assessment")
    development_potential: dict = Field(..., description="Development potential analysis")