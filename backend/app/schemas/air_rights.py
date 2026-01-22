"""
Air rights-related API schemas.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AirRightsResponse(BaseModel):
    """Response model for air rights information."""

    property_id: UUID = Field(..., description="Property identifier")
    transferable_air_rights_sf: float = Field(..., description="Transferable air rights in square feet")
    development_rights_sf: float = Field(..., description="Development rights in square feet")
    zoning_district: str = Field(..., description="Zoning district")
    maximum_far: float = Field(..., description="Maximum Floor Area Ratio")
    current_far: Optional[float] = Field(None, description="Current Floor Area Ratio")
    available_for_transfer: bool = Field(..., description="Whether air rights are available for transfer")
    transfer_value_estimate: Optional[float] = Field(None, description="Estimated transfer value")


class AirRightsRecipientsResponse(BaseModel):
    """Response model for air rights recipients."""

    property_id: UUID = Field(..., description="Recipient property identifier")
    transferred_air_rights_sf: float = Field(..., description="Transferred air rights in square feet")
    transfer_date: str = Field(..., description="Date of transfer")
    transfer_value: Optional[float] = Field(None, description="Transfer value")
    source_property_id: UUID = Field(..., description="Source property identifier")
    zoning_benefits: dict = Field(..., description="Zoning benefits from transfer")