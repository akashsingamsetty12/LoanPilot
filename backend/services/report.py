import os
import html
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import get_settings
from models.application import Application
from models.document import Document
from models.verification import VerificationResult
from models.risk import RiskAssessment
from schemas.agent import ReportResponse


def _generate_report_html(
    app: Application,
    docs: list[Document],
    vr: Optional[VerificationResult],
    risk: Optional[RiskAssessment]
) -> str:
    """Generate a clean, professional HTML verification report."""
    risk_score = risk.score if risk else (app.risk_score or 0.0)
    risk_level = risk.level if risk else (app.risk_level or "LOW")
    recommendation = risk.recommendation if risk else (app.recommendation or "NEEDS_HUMAN_REVIEW")
    flags = risk.flags if risk and isinstance(risk.flags, list) else []
    matches = vr.matches if vr and isinstance(vr.matches, list) else []
    mismatches = vr.mismatches if vr and isinstance(vr.mismatches, list) else []
    missing_docs = vr.missing_documents if vr and isinstance(vr.missing_documents, list) else []

    level_color = "#dc2626" if risk_level == "HIGH" else ("#f59e0b" if risk_level == "MEDIUM" else "#16a34a")

    docs_html = "".join([
        f"<tr><td>{html.escape(d.filename or '')}</td><td>{html.escape(d.doc_type or 'unknown')}</td>"
        f"<td>{html.escape(d.status or '')}</td><td>{d.pages or 1}</td>"
        f"<td>{f'{int(d.ocr_confidence * 100)}%' if d.ocr_confidence else 'N/A'}</td></tr>"
        for d in docs
    ]) or "<tr><td colspan='5'>No documents uploaded.</td></tr>"

    mismatches_html = "".join([
        f"<tr><td style='color:#dc2626;font-weight:600;'>{html.escape(m.get('field', 'Discrepancy'))}</td>"
        f"<td>{html.escape(str(m.get('sources', '')))}</td>"
        f"<td>{html.escape(str(m.get('values', '')))}</td>"
        f"<td>{html.escape(str(m.get('evidence', '')))}</td></tr>"
        for m in mismatches if isinstance(m, dict)
    ]) or "<tr><td colspan='4'>No mismatches found.</td></tr>"

    flags_html = "".join([
        f"<div style='border-left:4px solid {'#dc2626' if f.get('severity')=='HIGH' else '#f59e0b'};padding:8px 12px;margin-bottom:8px;background:#f9fafb;'>"
        f"<strong>[{html.escape(f.get('severity','INFO'))}]</strong> {html.escape(f.get('reason',''))} "
        f"<span style='color:#6b7280;font-size:0.9em;'>(Evidence: {html.escape(f.get('evidence',''))})</span></div>"
        for f in flags if isinstance(f, dict)
    ]) or "<p style='color:#16a34a;'>No risk flags raised. All verification rules passed.</p>"

    loan_amt_str = f"₹{app.loan_amount:,.0f}" if getattr(app, "loan_amount", None) is not None else "N/A"
    income_str = f"₹{app.income_annum:,.0f}" if getattr(app, "income_annum", None) is not None else "N/A"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>Loan Verification Report - {html.escape(app.id)}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 40px; color: #1f2937; background: #fff; }}
  .header {{ border-bottom: 2px solid #e5e7eb; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }}
  h1 {{ margin: 0; font-size: 24px; color: #111827; }}
  h2 {{ font-size: 16px; color: #374151; border-bottom: 1px solid #e5e7eb; padding-bottom: 6px; margin-top: 25px; }}
  .badge {{ padding: 4px 12px; border-radius: 9999px; font-size: 13px; font-weight: 600; color: #fff; display: inline-block; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
  th, td {{ text-align: left; padding: 8px 12px; border: 1px solid #e5e7eb; }}
  th {{ background: #f3f4f6; color: #374151; }}
  .stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 15px; }}
  .stat-card {{ background: #f9fafb; border: 1px solid #e5e7eb; padding: 12px; border-radius: 6px; }}
  .stat-card .label {{ font-size: 12px; color: #6b7280; text-transform: uppercase; }}
  .stat-card .value {{ font-size: 18px; font-weight: 700; color: #111827; margin-top: 4px; }}
  .rec-box {{ background: #eff6ff; border: 1px solid #bfdbfe; padding: 15px; border-radius: 6px; margin-top: 20px; }}
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>LoanPilot Verification Report</h1>
    <p style="margin:4px 0 0 0;color:#6b7280;">Application ID: <strong>{html.escape(app.id)}</strong> | Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>
  </div>
  <div>
    <span class="badge" style="background:{level_color};">Risk: {html.escape(risk_level)} ({risk_score:.0f}/100)</span>
  </div>
</div>

<h2>1. Applicant Summary</h2>
<div class="stat-grid">
  <div class="stat-card"><div class="label">Applicant Name</div><div class="value">{html.escape(app.applicant_name or 'N/A')}</div></div>
  <div class="stat-card"><div class="label">Loan Amount</div><div class="value">{loan_amt_str}</div></div>
  <div class="stat-card"><div class="label">Declared Income</div><div class="value">{income_str}</div></div>
  <div class="stat-card"><div class="label">CIBIL Score</div><div class="value">{app.cibil_score or 'N/A'}</div></div>
</div>

<h2>2. Document Verification Summary</h2>
<table>
  <thead><tr><th>Document</th><th>Type</th><th>Status</th><th>Pages</th><th>OCR Confidence</th></tr></thead>
  <tbody>{docs_html}</tbody>
</table>

<h2>3. Cross-Document Consistency Findings</h2>
<table>
  <thead><tr><th>Field</th><th>Sources</th><th>Extracted Values</th><th>Evidence</th></tr></thead>
  <tbody>{mismatches_html}</tbody>
</table>
{f"<p style='color:#dc2626;'><strong>Missing Required Documents:</strong> {html.escape(', '.join(missing_docs))}</p>" if missing_docs else ""}

<h2>4. Risk Assessment & Evidence Flags</h2>
<div style="margin-top:10px;">{flags_html}</div>

<div class="rec-box">
  <h3 style="margin:0 0 6px 0;color:#1e40af;">Recommendation: {html.escape(recommendation)}</h3>
  <p style="margin:0;color:#1e3a8a;font-size:14px;">This report has been compiled automatically with evidence links for underwriter review. Final loan decision must be made by a designated credit officer.</p>
</div>
</body>
</html>"""


def _generate_report_pdf(
    app: Application,
    docs: list[Document],
    vr: Optional[VerificationResult],
    risk: Optional[RiskAssessment],
    output_path: str
) -> None:
    """Generate a clean, high-precision PDF verification dossier using ReportLab."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=6
    )
    section_h2 = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=8,
        spaceAfter=4
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1E293B')
    )
    cell_normal = ParagraphStyle(
        'CellNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#334155')
    )
    cell_header = ParagraphStyle(
        'CellHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0F172A')
    )
    cell_danger = ParagraphStyle(
        'CellDanger',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#DC2626')
    )
    cell_success = ParagraphStyle(
        'CellSuccess',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#16A34A')
    )

    risk_score = risk.score if risk else (app.risk_score or 0.0)
    risk_level = risk.level if risk else (app.risk_level or "LOW")
    recommendation = risk.recommendation if risk else (app.recommendation or "NEEDS_HUMAN_REVIEW")
    flags = risk.flags if risk and isinstance(risk.flags, list) else []
    matches = vr.matches if vr and isinstance(vr.matches, list) else []
    mismatches = vr.mismatches if vr and isinstance(vr.mismatches, list) else []
    missing_docs = vr.missing_documents if vr and isinstance(vr.missing_documents, list) else []

    risk_color = colors.HexColor('#DC2626') if risk_level == 'HIGH' else (colors.HexColor('#D97706') if risk_level == 'MEDIUM' else colors.HexColor('#16A34A'))

    story = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>LoanPilot AI — Loan Verification Dossier</b>", title_style),
            Paragraph(f"<font color='{risk_color.hexval()}'><b>RISK: {risk_level} ({risk_score:.0f}/100)</b></font>", ParagraphStyle('RiskBadge', fontName='Helvetica-Bold', fontSize=12, alignment=2))
        ],
        [
            Paragraph(f"Application ID: <b>{app.id}</b> | Generated: {datetime.now(timezone.utc).strftime('%d %b %Y, %H:%M UTC')}", subtitle_style),
            Paragraph(f"Recommendation: <b>{recommendation.replace('_', ' ')}</b>", ParagraphStyle('RecText', fontName='Helvetica-Bold', fontSize=8.5, alignment=2, textColor=colors.HexColor('#334155')))
        ]
    ]
    header_table = Table(header_data, colWidths=[360, 180])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#CBD5E1'), spaceAfter=6, spaceBefore=3))

    # 2. Applicant & Loan Summary Grid
    story.append(Paragraph("1. Applicant & Financial Overview", section_h2))
    loan_amt_str = f"Rs. {app.loan_amount:,.0f}" if getattr(app, "loan_amount", None) is not None else "N/A"
    income_str = f"Rs. {app.income_annum:,.0f}" if getattr(app, "income_annum", None) is not None else "N/A"
    cibil_str = str(app.cibil_score) if getattr(app, "cibil_score", None) else "N/A"
    decision_str = (app.decision or app.status or "Pending Review").upper()

    summary_data = [
        [Paragraph("Applicant Name", cell_header), Paragraph("Loan Amount", cell_header), Paragraph("Declared Annual Income", cell_header), Paragraph("CIBIL Score", cell_header)],
        [Paragraph(app.applicant_name or "N/A", cell_bold), Paragraph(loan_amt_str, cell_normal), Paragraph(income_str, cell_normal), Paragraph(cibil_str, cell_normal)],
        [Paragraph("Loan Type", cell_header), Paragraph("Underwriting Status", cell_header), Paragraph("Decided By", cell_header), Paragraph("Decision Date", cell_header)],
        [Paragraph(getattr(app, 'loan_type', 'Home Loan') or 'Home Loan', cell_normal), Paragraph(f"<b>{decision_str}</b>", cell_success if "APPROV" in decision_str else (cell_danger if "REJECT" in decision_str else cell_bold)), Paragraph(app.decided_by or "Loan Officer", cell_normal), Paragraph(app.decided_at.strftime('%d %b %Y') if getattr(app, 'decided_at', None) else "Pending", cell_normal)]
    ]
    summary_table = Table(summary_data, colWidths=[135, 135, 135, 135])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F1F5F9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 6))

    # 3. Document Verification Summary
    story.append(Paragraph("2. Document Verification Summary", section_h2))
    doc_rows = [
        [Paragraph("Document Name", cell_header), Paragraph("Type", cell_header), Paragraph("Status", cell_header), Paragraph("Pages", cell_header), Paragraph("OCR Confidence", cell_header)]
    ]
    if docs:
        for d in docs:
            conf_pct = f"{int(d.ocr_confidence * 100)}%" if d.ocr_confidence else "N/A"
            doc_rows.append([
                Paragraph(d.filename or "Unnamed Document", cell_bold),
                Paragraph(d.doc_type or "Unknown", cell_normal),
                Paragraph(d.status or "Completed", cell_success if d.status == "completed" else cell_normal),
                Paragraph(str(d.pages or 1), cell_normal),
                Paragraph(conf_pct, cell_normal)
            ])
    else:
        doc_rows.append([Paragraph("No documents uploaded.", cell_normal), Paragraph("", cell_normal), Paragraph("", cell_normal), Paragraph("", cell_normal), Paragraph("", cell_normal)])

    doc_table = Table(doc_rows, colWidths=[180, 110, 80, 50, 120])
    doc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(doc_table)
    story.append(Spacer(1, 6))

    # 4. Cross-Document Consistency Findings
    story.append(Paragraph("3. Cross-Document Consistency & Verification", section_h2))
    mismatch_rows = [
        [Paragraph("Field / Attribute", cell_header), Paragraph("Source Documents", cell_header), Paragraph("Extracted Values", cell_header), Paragraph("Audit Finding", cell_header)]
    ]
    if mismatches:
        for m in mismatches:
            if isinstance(m, dict):
                mismatch_rows.append([
                    Paragraph(str(m.get("field", "Discrepancy")).replace("_", " ").title(), cell_danger),
                    Paragraph(str(m.get("sources", "")), cell_normal),
                    Paragraph(str(m.get("values", "")), cell_normal),
                    Paragraph(str(m.get("evidence", "")), cell_normal)
                ])
    else:
        mismatch_rows.append([Paragraph("No cross-document discrepancies detected. All critical fields match.", cell_success), Paragraph("", cell_normal), Paragraph("", cell_normal), Paragraph("", cell_normal)])

    mismatch_table = Table(mismatch_rows, colWidths=[120, 130, 140, 150])
    mismatch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(mismatch_table)

    if missing_docs:
        story.append(Spacer(1, 3))
        story.append(Paragraph(f"<font color='#DC2626'><b>Missing Required Documents:</b> {', '.join(missing_docs)}</font>", cell_danger))

    story.append(Spacer(1, 6))

    # 5. Risk Assessment & Evidence Flags
    story.append(Paragraph("4. Risk Assessment & Evidence Flags", section_h2))
    if flags:
        flag_rows = [
            [Paragraph("Severity", cell_header), Paragraph("Risk Flag / Discrepancy", cell_header), Paragraph("Evidence / Details", cell_header)]
        ]
        for f in flags:
            if isinstance(f, dict):
                sev = f.get("severity", "MEDIUM")
                s_color = cell_danger if sev == "HIGH" else (ParagraphStyle('SevMed', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#D97706')))
                flag_rows.append([
                    Paragraph(f"[{sev}]", s_color),
                    Paragraph(f.get("reason", "Risk finding"), cell_bold),
                    Paragraph(str(f.get("evidence", "") or f.get("details", "")), cell_normal)
                ])
        flag_table = Table(flag_rows, colWidths=[70, 200, 270])
        flag_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(flag_table)
    else:
        story.append(Paragraph("<font color='#16A34A'><b>No risk flags raised. Application satisfies primary underwriting verification rules.</b></font>", cell_success))

    story.append(Spacer(1, 8))

    # 6. Officer Decision Box & Audit Sign-Off
    decision_title = f"Final Decision: {decision_str}"
    officer_notes = app.decision_notes or "No officer comments recorded."
    dec_box_data = [
        [Paragraph(f"<b>{decision_title}</b>", ParagraphStyle('DecTitle', fontName='Helvetica-Bold', fontSize=9.5, textColor=colors.HexColor('#0F172A')))],
        [Paragraph(f"<b>Underwriter Notes:</b> {officer_notes}", cell_normal)],
        [Paragraph("<i>Notice: This verification dossier was compiled by LoanPilot AI. Final credit approval and disbursement authorization remain subject to institution credit policy and compliance mandates.</i>", ParagraphStyle('Disc', fontName='Helvetica-Oblique', fontSize=7, leading=9, textColor=colors.HexColor('#64748B')))]
    ]
    dec_table = Table(dec_box_data, colWidths=[540])
    dec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(dec_table)

    doc.build(story)


async def generate_report(app_id: str, db: AsyncSession) -> ReportResponse:
    """Generate a comprehensive loan verification report."""
    stmt = select(Application).where(Application.id == app_id)
    res = await db.execute(stmt)
    app = res.scalar_one_or_none()

    if not app:
        raise ValueError(f"Application '{app_id}' not found.")

    doc_stmt = select(Document).where(Document.application_id == app_id)
    docs_res = await db.execute(doc_stmt)
    docs = list(docs_res.scalars().all())

    vr_stmt = select(VerificationResult).where(VerificationResult.application_id == app_id)
    vr_res = await db.execute(vr_stmt)
    vr = vr_res.scalar_one_or_none()

    risk_stmt = select(RiskAssessment).where(RiskAssessment.application_id == app_id)
    risk_res = await db.execute(risk_stmt)
    risk = risk_res.scalar_one_or_none()

    report_html = _generate_report_html(app, docs, vr, risk)

    # Save to disk for download
    settings = get_settings()
    report_dir = os.path.join(settings.UPLOAD_DIR, app_id, "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"report_{app_id}.html")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_html)

    # Generate PDF version
    pdf_file = os.path.join(report_dir, f"report_{app_id}.pdf")
    try:
        _generate_report_pdf(app, docs, vr, risk, pdf_file)
    except Exception as e:
        import traceback
        print(f"[ERROR] Failed to generate PDF report: {e}")
        traceback.print_exc()

    # Format verification results for frontend
    verif_results = []
    if vr:
        for m in (vr.matches or []):
            if isinstance(m, str):
                verif_results.append({
                    "field_name": m.replace("_", " ").title(),
                    "status": "PASS"
                })
            elif isinstance(m, dict):
                verif_results.append({
                    "field_name": m.get("field", "Field").replace("_", " ").title(),
                    "status": "PASS"
                })
        for m in (vr.mismatches or []):
            if isinstance(m, dict):
                verif_results.append({
                    "field_name": m.get("field", "Field").replace("_", " ").title(),
                    "status": "MISMATCH"
                })

    formatted_flags = []
    if risk and isinstance(risk.flags, list):
        for idx, f in enumerate(risk.flags):
            if isinstance(f, dict):
                formatted_flags.append({
                    "id": str(idx + 1),
                    "severity": f.get("severity", "MEDIUM"),
                    "reason": f.get("reason", ""),
                    "details": f.get("evidence", "") or f.get("reason", ""),
                    "evidence": []
                })

    return ReportResponse(
        application_id=app_id,
        report_html=report_html,
        report_url=f"/api/v1/applications/{app_id}/report/download",
        generated_at=datetime.now(timezone.utc),
        sections=[
            "applicant_info",
            "document_summary",
            "verification",
            "flags",
            "recommendation",
        ],
        applicant_name=app.applicant_name or "Applicant",
        documents_reviewed=len([d for d in docs if d.status in ("completed", "extracted", "verified")]),
        risk_score=risk.score if risk else (app.risk_score or 0.0),
        risk_level=risk.level if risk else (app.risk_level or "LOW"),
        flags=formatted_flags,
        verification_results=verif_results,
        missing_documents=vr.missing_documents if vr and isinstance(vr.missing_documents, list) else [],
        recommendation=risk.recommendation if risk else (app.recommendation or "NEEDS_HUMAN_REVIEW"),
    )


async def get_report(app_id: str, db: AsyncSession) -> ReportResponse:
    """Retrieve an existing report or generate on demand."""
    return await generate_report(app_id, db)

