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

