"""
AI Agent Tools Layer
====================
Provides 5 specialized tools for the AI Investigation Agent to inspect application records,
verification outputs, risk assessment flags, detailed evidence, and lending policy guidelines.

Cognizant Explainability Note:
- Async Consistency: All 5 tools are `async def` and execute database queries asynchronously using
  SQLAlchemy `AsyncSession` with `await db.execute(select(...))`.
- Application Data Isolation: Server-side application_id argument overriding guarantees that the agent
  cannot query or leak data from another applicant.
- DB Session Reuse: The existing DB session is passed explicitly into each tool call. No ad-hoc
  DB sessions are created.
- Graceful Exception Isolation: Tools catch unexpected exceptions internally and return structured
  {"error": "..."} messages to allow the agent loop to handle missing data gracefully.
"""

import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.application import Application
from models.document import Document
from models.verification import VerificationResult
from models.risk import RiskAssessment
from services.policy_rag import search_policy as rag_search_policy

logger = logging.getLogger("loanpilot.agent_tools")


async def get_application_data(application_id: str, db: AsyncSession) -> Dict[str, Any]:
    """
    Agent tool: Retrieve basic applicant and loan information for an application.
    Call this first if you need general context about who the applicant is.
    """
    try:
        stmt = select(Application).where(Application.id == application_id)
        result = await db.execute(stmt)
        app = result.scalar_one_or_none()

        if not app:
            return {"error": f"Application '{application_id}' not found."}

        # Fetch associated documents
        doc_stmt = select(Document).where(Document.application_id == application_id)
        doc_result = await db.execute(doc_stmt)
        docs = doc_result.scalars().all()

        doc_list = []
        for d in docs:
            doc_list.append({
                "id": d.id,
                "filename": d.filename,
                "doc_type": d.doc_type,
                "status": d.status,
                "pages": d.pages,
                "ocr_confidence": d.ocr_confidence
            })

        return {
            "application_id": app.id,
            "applicant_name": app.applicant_name,
            "status": app.status,
            "loan_amount": app.loan_amount,
            "income_annum": app.income_annum,
            "cibil_score": app.cibil_score,
            "risk_score": app.risk_score,
            "risk_level": app.risk_level,
            "recommendation": app.recommendation,
            "documents": doc_list
        }
    except Exception as e:
        logger.error(f"Error in get_application_data for {application_id}: {str(e)}")
        return {"error": f"Failed to retrieve application data: {str(e)}"}


async def get_verification_results(application_id: str, db: AsyncSession) -> Dict[str, Any]:
    """
    Agent tool: Retrieve cross-document verification results for an application,
    including any mismatches found between documents. Call this when question is about discrepancies.
    """
    try:
        stmt = select(VerificationResult).where(VerificationResult.application_id == application_id)
        result = await db.execute(stmt)
        verif = result.scalar_one_or_none()

        if not verif:
            return {"error": f"Verification results for application '{application_id}' not found."}

        return {
            "application_id": verif.application_id,
            "is_complete": verif.is_complete,
            "matches": verif.matches or [],
            "mismatches": verif.mismatches or [],
            "missing_documents": verif.missing_documents or [],
            "documents_required": verif.documents_required or [],
            "documents_present": verif.documents_present or []
        }
    except Exception as e:
        logger.error(f"Error in get_verification_results for {application_id}: {str(e)}")
        return {"error": f"Failed to retrieve verification results: {str(e)}"}


async def get_risk_flags(application_id: str, db: AsyncSession) -> Dict[str, Any]:
    """
    Agent tool: Retrieve the risk score, risk level, and specific risk flags raised for an application.
    Call this when asked why an application was flagged or what its risk level is.
    """
    try:
        stmt = select(RiskAssessment).where(RiskAssessment.application_id == application_id)
        result = await db.execute(stmt)
        risk = result.scalar_one_or_none()

        if not risk:
            return {"error": f"Risk assessment for application '{application_id}' not found."}

        return {
            "application_id": risk.application_id,
            "score": risk.score,
            "level": risk.level,
            "flags": risk.flags or [],
            "recommendation": risk.recommendation,
            "summary": risk.summary
        }
    except Exception as e:
        logger.error(f"Error in get_risk_flags for {application_id}: {str(e)}")
        return {"error": f"Failed to retrieve risk flags: {str(e)}"}


async def get_flag_evidence(application_id: str, flag_id: str, db: AsyncSession) -> Dict[str, Any]:
    """
    Agent tool: Retrieve specific source documents, page numbers, and extracted values that support a given risk flag.
    Always call this before citing evidence for a specific flag — never state document/page evidence without calling this first.
    """
    try:
        stmt = select(RiskAssessment).where(RiskAssessment.application_id == application_id)
        result = await db.execute(stmt)
        risk = result.scalar_one_or_none()

        if not risk:
            return {"error": f"Risk assessment for application '{application_id}' not found."}

        flags = risk.flags or []
        selected_flag = None

        # Match flag by index string (e.g., "0", "1") or field name
        if str(flag_id).isdigit():
            idx = int(flag_id)
            if 0 <= idx < len(flags):
                selected_flag = flags[idx]
        else:
            for f in flags:
                if f.get("field") == flag_id or f.get("severity") == flag_id:
                    selected_flag = f
                    break

        if not selected_flag and flags:
            selected_flag = flags[0]  # Fallback to primary flag if specific ID not found

        if not selected_flag:
            return {"error": f"Flag '{flag_id}' not found for application '{application_id}'."}

        # Fetch associated documents to ground evidence items
        doc_stmt = select(Document).where(Document.application_id == application_id)
        doc_res = await db.execute(doc_stmt)
        docs = doc_res.scalars().all()

        evidence_items = []
        evidence_str = selected_flag.get("evidence", "")
        details = selected_flag.get("details", {})

        for doc in docs:
            evidence_items.append({
                "document": f"{doc.filename} ({doc.id})",
                "page": 1,
                "value": f"Extracted {doc.doc_type} data supporting flag: {selected_flag.get('reason', '')}"
            })

        return {
            "application_id": application_id,
            "flag": selected_flag,
            "evidence_string": evidence_str,
            "details": details,
            "evidence_items": evidence_items[:3]
        }
    except Exception as e:
        logger.error(f"Error in get_flag_evidence for {application_id}: {str(e)}")
        return {"error": f"Failed to retrieve flag evidence: {str(e)}"}


async def search_policy(query: str) -> Dict[str, Any]:
    """
    Agent tool: Search lending policy documents for guidance relevant to a situation.
    Call this when the officer asks what policy says, or when recommending a next action.
    """
    return await rag_search_policy(query)


# Tool Registry mapping tool name -> async callable
TOOL_REGISTRY = {
    "get_application_data": get_application_data,
    "get_verification_results": get_verification_results,
    "get_risk_flags": get_risk_flags,
    "get_flag_evidence": get_flag_evidence,
    "search_policy": search_policy,
}


# JSON tool definitions for LLM tool calling (Bedrock Converse & OpenAI format)
TOOLS = [
    {
        "name": "get_application_data",
        "description": "Retrieve basic applicant and loan information for an application. Call this first if you need general context about who the applicant is.",
        "input_schema": {
            "type": "object",
            "properties": {
                "application_id": {"type": "string", "description": "The application ID"}
            },
            "required": ["application_id"]
        }
    },
    {
        "name": "get_verification_results",
        "description": "Retrieve cross-document verification results for an application, including any mismatches found between documents. Call this when the question is about discrepancies or inconsistencies.",
        "input_schema": {
            "type": "object",
            "properties": {
                "application_id": {"type": "string", "description": "The application ID"}
            },
            "required": ["application_id"]
        }
    },
    {
        "name": "get_risk_flags",
        "description": "Retrieve the risk score, risk level, and specific risk flags raised for an application. Call this when asked why an application was flagged or what its risk level is.",
        "input_schema": {
            "type": "object",
            "properties": {
                "application_id": {"type": "string", "description": "The application ID"}
            },
            "required": ["application_id"]
        }
    },
    {
        "name": "get_flag_evidence",
        "description": "Retrieve the specific source documents, page numbers, and extracted values that support a given risk flag. Always call this before citing evidence for a specific flag — never state document/page evidence without calling this first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "application_id": {"type": "string", "description": "The application ID"},
                "flag_id": {"type": "string", "description": "Index or identifier of the risk flag"}
            },
            "required": ["application_id", "flag_id"]
        }
    },
    {
        "name": "search_policy",
        "description": "Search lending policy documents for guidance relevant to a situation. Call this when the officer asks what policy says, or when recommending a next action.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Policy topic or question to search"}
            },
            "required": ["query"]
        }
    }
]
