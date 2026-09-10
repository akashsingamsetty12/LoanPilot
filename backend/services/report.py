"""
Report Generation Service
======================================
Generates the Loan Verification Report combining extracted fields,
flags, and recommendations into HTML and PDF formats.


Report sections:
  1. Applicant Information
  2. Document Summary (type, status, OCR confidence per doc)
  3. Extracted Fields Table
  4. Cross-Document Verification Results
  5. Risk Assessment (score, level, flags with evidence)
  6. Recommendation

Technologies:
  - Jinja2: HTML report templating
  - ReportLab: PDF generation

Data flow:
  Application + Documents + Verification + Risk → HTML/PDF report

Input:  Application ID (loads all data from DB)
Output: ReportResponse (HTML string + PDF download URL)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from schemas.agent import ReportResponse


async def generate_report(app_id: str, db: AsyncSession) -> ReportResponse:
    """
    Generate a comprehensive loan verification report.

    Steps:
      1. Load application, all documents, verification, risk assessment from DB
      2. Render HTML report using Jinja2 template
      3. Generate PDF using ReportLab
      4. Save PDF to uploads/{app_id}/reports/report_{app_id}.pdf
      5. Return ReportResponse with HTML and PDF URL

    TODO: implement report generation
    """
    raise NotImplementedError("generate_report() is not implemented")


async def get_report(app_id: str, db: AsyncSession) -> ReportResponse:
    """
    Retrieve a previously generated report.

    TODO: implement report retrieval
    """
    raise NotImplementedError("get_report() is not implemented")
