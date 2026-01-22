"""
Report-related API schemas.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PDFReportRequest(BaseModel):
    """Request model for generating PDF reports."""

    property_id: UUID = Field(..., description="Property identifier")
    include_zoning_analysis: bool = Field(True, description="Include zoning analysis")
    include_landmarks: bool = Field(True, description="Include nearby landmarks")
    include_tax_incentives: bool = Field(True, description="Include tax incentives")
    include_air_rights: bool = Field(True, description="Include air rights information")
    report_format: str = Field("comprehensive", description="Report format (comprehensive, summary)")


class PDFReportPreviewRequest(BaseModel):
    """Request model for PDF report preview."""

    property_id: UUID = Field(..., description="Property identifier")
    preview_sections: List[str] = Field(..., description="Sections to include in preview")
    max_pages: int = Field(5, description="Maximum number of preview pages")