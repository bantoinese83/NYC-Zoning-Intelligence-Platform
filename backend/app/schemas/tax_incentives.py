"""
Tax incentive-related API schemas.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TaxIncentiveProgramResponse(BaseModel):
    """Response model for tax incentive program information."""

    id: str = Field(..., description="Program identifier")
    name: str = Field(..., description="Program name")
    description: str = Field(..., description="Program description")
    category: str = Field(..., description="Program category")
    eligibility_criteria: dict = Field(..., description="Eligibility requirements")
    benefits: dict = Field(..., description="Tax benefits provided")
    application_process: str = Field(..., description="How to apply")
    contact_information: Optional[dict] = Field(None, description="Contact information")
    active: bool = Field(True, description="Whether the program is currently active")


class TaxIncentiveEligibilityResponse(BaseModel):
    """Response model for tax incentive eligibility check."""

    property_id: UUID = Field(..., description="Property identifier")
    eligible_programs: List[TaxIncentiveProgramResponse] = Field(default_factory=list, description="Eligible tax incentive programs")
    ineligible_programs: List[dict] = Field(default_factory=list, description="Ineligible programs with reasons")
    total_potential_savings: Optional[float] = Field(None, description="Estimated annual tax savings")
    application_priority: List[str] = Field(default_factory=list, description="Recommended application order")


class PropertyTaxIncentiveResponse(BaseModel):
    """Response model for property-specific tax incentives."""

    property_id: UUID = Field(..., description="Property identifier")
    applied_incentives: List[dict] = Field(default_factory=list, description="Currently applied incentives")
    available_incentives: List[TaxIncentiveProgramResponse] = Field(default_factory=list, description="Available incentives")
    application_status: dict = Field(..., description="Application status for various programs")
    expiration_dates: dict = Field(..., description="Expiration dates for applied incentives")