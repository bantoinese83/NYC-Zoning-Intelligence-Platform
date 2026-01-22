"""
PDF report generation utilities.

Creates comprehensive zoning analysis reports using ReportLab.
"""

import io
import logging
from datetime import datetime
from typing import Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

logger = logging.getLogger(__name__)


class ZoningReportGenerator:
    """
    Generates PDF zoning analysis reports.

    Creates comprehensive reports with property information,
    zoning analysis, tax incentives, landmarks, and air rights.
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report."""
        self.styles.add(
            ParagraphStyle(
                name="ReportTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                spaceAfter=30,
                alignment=1,  # Center alignment
                textColor=colors.darkblue,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=16,
                spaceAfter=15,
                textColor=colors.darkgreen,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="SubHeader",
                parent=self.styles["Heading3"],
                fontSize=14,
                spaceAfter=10,
                textColor=colors.darkslategray,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="BodyText",
                parent=self.styles["Normal"],
                fontSize=10,
                spaceAfter=8,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="Footer",
                parent=self.styles["Normal"],
                fontSize=8,
                textColor=colors.gray,
                alignment=1,
            )
        )

    def generate_report(self, analysis_data: Dict[str, Any]) -> bytes:
        """
        Generate a complete PDF zoning report.

        Args:
            analysis_data: Complete property analysis data

        Returns:
            PDF content as bytes
        """
        logger.info("Generating PDF zoning report")

        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        # Build report content
        story = []
        story.extend(self._build_title_page(analysis_data))
        story.append(PageBreak())
        story.extend(self._build_property_summary(analysis_data))
        story.extend(self._build_zoning_analysis(analysis_data))
        story.extend(self._build_tax_incentives(analysis_data))
        story.extend(self._build_landmarks(analysis_data))
        story.extend(self._build_air_rights(analysis_data))
        story.extend(self._build_disclaimer())

        # Generate PDF
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()

        logger.info(f"Generated PDF report: {len(pdf_content)} bytes")
        return pdf_content

    def _build_title_page(self, data: Dict[str, Any]) -> list:
        """Build the report title page."""
        story = []

        # Title
        title = Paragraph("NYC Zoning Intelligence Report", self.styles["ReportTitle"])
        story.append(title)
        story.append(Spacer(1, 0.5 * inch))

        # Property information
        property_info = data.get("property", {})
        address = property_info.get("address", "Unknown Address")

        info_table_data = [
            ["Property Address:", address],
            ["Lot Number:", property_info.get("lot_number", "N/A")],
            ["Block Number:", property_info.get("block_number", "N/A")],
            ["Report Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Analysis Platform:", "NYC Zoning Intelligence v0.1.0"],
        ]

        info_table = Table(info_table_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(info_table)

        return story

    def _build_property_summary(self, data: Dict[str, Any]) -> list:
        """Build property summary section."""
        story = []

        story.append(Paragraph("Property Summary", self.styles["SectionHeader"]))

        property_info = data.get("property", {})

        summary_data = [
            ["Address:", property_info.get("address", "N/A")],
            ["Lot Number:", property_info.get("lot_number", "N/A")],
            ["Block Number:", property_info.get("block_number", "N/A")],
            ["ZIP Code:", property_info.get("zip_code", "N/A")],
            ["Land Area:", ".1f"],
            ["Building Area:", ".1f"],
            ["Current Use:", property_info.get("current_use", "Unknown")],
        ]

        summary_table = Table(summary_data, colWidths=[2 * inch, 4 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 0.25 * inch))

        return story

    def _build_zoning_analysis(self, data: Dict[str, Any]) -> list:
        """Build zoning analysis section."""
        story = []

        story.append(Paragraph("Zoning Analysis", self.styles["SectionHeader"]))

        zoning = data.get("zoning", {})

        # FAR Summary
        story.append(Paragraph("Floor Area Ratio (FAR)", self.styles["SubHeader"]))

        far_data = [
            ["Base FAR:", ".2f"],
            ["FAR with Bonuses:", ".2f"],
            ["Maximum Buildable Area:", ".0f"],
            ["Maximum Height:", f"{zoning.get('max_height_ft', 'N/A')} ft"],
        ]

        far_table = Table(far_data, colWidths=[2.5 * inch, 2.5 * inch])
        far_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(far_table)
        story.append(Spacer(1, 0.25 * inch))

        # Zoning Districts
        story.append(Paragraph("Zoning Districts", self.styles["SubHeader"]))

        districts = zoning.get("districts", [])
        if districts:
            district_data = [
                ["District", "FAR Base", "FAR Bonus", "% Area", "Max Height"]
            ]
            for district in districts:
                district_data.append(
                    [
                        district.get("district_code", "N/A"),
                        ".2f",
                        ".2f",
                        ".1f",
                        f"{district.get('max_height_ft', 'N/A')} ft",
                    ]
                )

            district_table = Table(
                district_data,
                colWidths=[1.2 * inch, 1 * inch, 1 * inch, 1 * inch, 1.2 * inch],
            )
            district_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTNAME", (1, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ]
                )
            )
            story.append(district_table)
        else:
            story.append(
                Paragraph("No zoning districts found.", self.styles["BodyText"])
            )

        story.append(Spacer(1, 0.25 * inch))

        # Setbacks
        story.append(Paragraph("Setback Requirements", self.styles["SubHeader"]))

        setbacks = zoning.get("setback_requirements", {})
        setback_data = [
            ["Front Setback:", f"{setbacks.get('front_ft', 'N/A')} ft"],
            ["Side Setback:", f"{setbacks.get('side_ft', 'N/A')} ft"],
            ["Rear Setback:", f"{setbacks.get('rear_ft', 'N/A')} ft"],
        ]

        setback_table = Table(setback_data, colWidths=[2 * inch, 2 * inch])
        setback_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(setback_table)
        story.append(Spacer(1, 0.25 * inch))

        return story

    def _build_tax_incentives(self, data: Dict[str, Any]) -> list:
        """Build tax incentives section."""
        story = []

        story.append(Paragraph("Tax Incentive Programs", self.styles["SectionHeader"]))

        incentives = data.get("tax_incentives", [])

        if incentives:
            incentive_data = [["Program", "Eligibility", "Est. Savings"]]
            for incentive in incentives:
                status = "Eligible" if incentive.get("is_eligible") else "Not Eligible"
                savings = ".0f" if incentive.get("estimated_abatement_value") else "N/A"
                incentive_data.append(
                    [incentive.get("program_name", "N/A"), status, savings]
                )

            incentive_table = Table(
                incentive_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch]
            )
            incentive_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTNAME", (1, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ]
                )
            )
            story.append(incentive_table)
        else:
            story.append(
                Paragraph("No tax incentives analyzed.", self.styles["BodyText"])
            )

        story.append(Spacer(1, 0.25 * inch))

        return story

    def _build_landmarks(self, data: Dict[str, Any]) -> list:
        """Build nearby landmarks section."""
        story = []

        story.append(Paragraph("Nearby Landmarks", self.styles["SectionHeader"]))

        landmarks = data.get("nearby_landmarks", [])

        if landmarks:
            landmark_data = [["Name", "Type", "Distance"]]
            for landmark in landmarks[:10]:  # Limit to top 10
                landmark_data.append(
                    [
                        landmark.get("name", "N/A"),
                        landmark.get("landmark_type", "N/A"),
                        ".0f",
                    ]
                )

            landmark_table = Table(
                landmark_data, colWidths=[2.5 * inch, 1.5 * inch, 1 * inch]
            )
            landmark_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTNAME", (1, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ]
                )
            )
            story.append(landmark_table)
        else:
            story.append(
                Paragraph("No nearby landmarks found.", self.styles["BodyText"])
            )

        story.append(Spacer(1, 0.25 * inch))

        return story

    def _build_air_rights(self, data: Dict[str, Any]) -> list:
        """Build air rights analysis section."""
        story = []

        story.append(Paragraph("Air Rights Analysis", self.styles["SectionHeader"]))

        air_rights = data.get("air_rights", {})

        air_rights_data = [
            ["Unused FAR:", ".2f"],
            ["Transferable FAR:", ".2f"],
            ["Transferable Square Footage:", ".0f"],
            ["Adjacent Properties:", str(air_rights.get("adjacent_properties", 0))],
            [
                "Estimated Market Value:",
                ".0f" if air_rights.get("estimated_value") else "N/A",
            ],
        ]

        air_table = Table(air_rights_data, colWidths=[2.5 * inch, 2.5 * inch])
        air_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(air_table)
        story.append(Spacer(1, 0.25 * inch))

        return story

    def _build_disclaimer(self) -> list:
        """Build report disclaimer and footer."""
        story = []

        story.append(Paragraph("Disclaimer", self.styles["SectionHeader"]))

        disclaimer_text = """
        This report is for informational purposes only and does not constitute legal advice.
        All zoning and tax information should be verified with official sources including
        the NYC Department of City Planning and NYC Department of Finance.
        Property values and tax estimates are approximate and may change.
        """

        story.append(Paragraph(disclaimer_text, self.styles["BodyText"]))
        story.append(Spacer(1, 0.5 * inch))

        # Footer
        footer_text = f"""
        Report generated by NYC Zoning Intelligence Platform on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Data sources: NYC DCP, NYC DOF, NYC Landmarks Preservation Commission
        """

        story.append(Paragraph(footer_text, self.styles["Footer"]))

        return story


def generate_pdf_report(analysis_data: Dict[str, Any]) -> bytes:
    """
    Generate a PDF zoning report from analysis data.

    This is the main entry point for PDF generation.

    Args:
        analysis_data: Complete property analysis data

    Returns:
        PDF content as bytes
    """
    generator = ZoningReportGenerator()
    return generator.generate_report(analysis_data)
