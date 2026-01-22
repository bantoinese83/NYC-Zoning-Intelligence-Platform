"""
API schema exports and common models.
"""

from .air_rights import AirRightsRecipientsResponse, AirRightsResponse
from .landmarks import LandmarkResponse, NearbyLandmarksResponse
from .properties import (
    AddressSearchRequest,
    PropertyAnalysisResponse,
    PropertyCreate,
    PropertyResponse,
)
from .reports import PDFReportPreviewRequest, PDFReportRequest
from .tax_incentives import (
    PropertyTaxIncentiveResponse,
    TaxIncentiveEligibilityResponse,
    TaxIncentiveProgramResponse,
)
from .zoning import (
    FARCalculatorRequest,
    FARCalculatorResponse,
    ZoningAnalysisResponse,
    ZoningComplianceResponse,
    ZoningDistrictResponse,
)

# Common error response schema
from pydantic import BaseModel, Field
from typing import Any, Optional, Dict


class ErrorResponse(BaseModel):
    """Standardized error response schema."""

    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    code: Optional[str] = Field(None, description="Error code for programmatic handling")


class ValidationErrorResponse(BaseModel):
    """Validation error response schema."""

    error: str = Field(default="validation_error", description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Dict[str, Any] = Field(..., description="Field-specific validation errors")
    code: Optional[str] = Field(default="VALIDATION_ERROR", description="Error code")


class NotFoundErrorResponse(BaseModel):
    """Not found error response schema."""

    error: str = Field(default="not_found", description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    code: Optional[str] = Field(default="NOT_FOUND", description="Error code")