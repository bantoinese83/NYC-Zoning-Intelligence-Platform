"""
Reports API routes.

Handles PDF report generation and preview.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import PDFReportPreviewRequest, PDFReportRequest
from ..services import property_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/generate-pdf",
    summary="Generate PDF zoning report",
    description="""
    Generate a comprehensive PDF zoning analysis report.

    The report includes:
    - Property information and location
    - Zoning district analysis
    - FAR calculations and development potential
    - Tax incentive eligibility
    - Nearby landmarks
    - Air rights analysis

    Returns a PDF file for download.
    """,
    tags=["reports"],
    response_class=Response,
)
async def generate_pdf_report(request: PDFReportRequest, db: Session = Depends(get_db)):
    """
    Generate and return a PDF zoning report.
    """
    try:
        logger.info(f"Generating PDF report for property {request.property_id}")

        # Check if property exists
        from ..models import Property

        property_obj = db.query(Property).filter_by(id=request.property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")

        # Get complete analysis data
        analysis = property_service.get_property_full_analysis(request.property_id, db)

        # Generate PDF (placeholder - would use reportlab/weasyprint)
        pdf_content = await _generate_pdf_content(analysis, request)

        # Return PDF response
        response = Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=zoning-report-{request.property_id}.pdf"
            },
        )

        logger.info(f"PDF report generated for property {request.property_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error generating PDF report: {str(e)}"
        )


@router.post(
    "/preview",
    summary="Preview report data",
    description="""
    Get all data that would be included in a PDF report without generating the PDF.

    Useful for previewing report content or building custom reports.
    """,
    tags=["reports"],
)
async def preview_report(
    request: PDFReportPreviewRequest, db: Session = Depends(get_db)
):
    """
    Preview report data without generating PDF.
    """
    try:
        logger.info(f"Generating report preview for property {request.property_id}")

        # Check if property exists
        from ..models import Property

        property_obj = db.query(Property).filter_by(id=request.property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")

        # Get complete analysis
        analysis = property_service.get_property_full_analysis(request.property_id, db)

        # Filter based on request sections (if specified)
        if request.sections:
            filtered_analysis = {"property": analysis["property"]}
            section_map = {
                "zoning": "zoning",
                "incentives": "tax_incentives",
                "landmarks": "nearby_landmarks",
                "air_rights": "air_rights",
            }

            for section in request.sections:
                if section in section_map:
                    filtered_analysis[section_map[section]] = analysis.get(
                        section_map[section]
                    )

            analysis = filtered_analysis

        logger.info(f"Report preview generated for property {request.property_id}")
        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report preview: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error generating report preview: {str(e)}"
        )


@router.get(
    "/templates",
    summary="List available report templates",
    description="Get list of available PDF report templates and their features.",
    tags=["reports"],
)
async def list_report_templates():
    """
    List available report templates.
    """
    templates = [
        {
            "id": "comprehensive",
            "name": "Comprehensive Zoning Analysis",
            "description": "Full analysis including zoning, incentives, landmarks, and air rights",
            "sections": ["zoning", "tax_incentives", "landmarks", "air_rights"],
            "estimated_pages": 8,
        },
        {
            "id": "zoning_only",
            "name": "Zoning Summary",
            "description": "Zoning districts, FAR, and development potential only",
            "sections": ["zoning"],
            "estimated_pages": 3,
        },
        {
            "id": "development_focused",
            "name": "Development Analysis",
            "description": "Focus on development potential, incentives, and air rights",
            "sections": ["zoning", "tax_incentives", "air_rights"],
            "estimated_pages": 5,
        },
    ]

    return {"templates": templates}


async def _generate_pdf_content(analysis: dict, request: PDFReportRequest) -> bytes:
    """
    Generate PDF content from analysis data.

    This is a placeholder implementation. In production, this would use:
    - ReportLab for PDF generation
    - WeasyPrint for HTML-to-PDF
    - Proper styling and layout

    Returns PDF bytes.
    """
    # Placeholder PDF generation
    # In production, this would create a properly formatted PDF

    pdf_content = f"""
NYC Zoning Intelligence Report
Generated: 2026-01-22

Property: {analysis['property']['address']}
Lot: {analysis['property']['lot_number']}

Zoning Analysis:
- Districts: {len(analysis.get('zoning', {}).get('districts', []))}
- Total FAR: {analysis.get('zoning', {}).get('total_far', 'N/A')}
- Buildable Area: {analysis.get('zoning', {}).get('total_buildable_area_sf', 'N/A')} SF

Tax Incentives:
{len(analysis.get('tax_incentives', []))} programs checked

Landmarks:
{len(analysis.get('nearby_landmarks', []))} found within 150 feet

Air Rights:
Unused FAR: {analysis.get('air_rights', {}).get('unused_far', 'N/A')}

Report generated by NYC Zoning Intelligence Platform
""".encode("utf-8")

    # In production, return actual PDF bytes
    # For now, return text content as bytes
    return pdf_content
