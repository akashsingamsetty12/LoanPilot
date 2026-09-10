"""
Pipeline Orchestrator
==================================
Chains modules 3→4→5→6 for an application.
This is the central pipeline orchestration service.


Pipeline steps:
  1. OCR each document
  2. Classify each document
  3. Extract fields
  4. Validate within documents
  5. Cross-document verification
  6. Risk assessment
  7. Update application status  → "review"

Data flow:
  Application with uploaded docs → full processing pipeline → ready for human review
"""

from sqlalchemy.ext.asyncio import AsyncSession
from middleware.logging import pipeline_logger as logger


async def process_application(app_id: str, db: AsyncSession) -> dict:
    """
    Run the full processing pipeline for a loan application.

    Steps:
      1. Load application and all its documents from DB
      2. Update application status to "processing"
      3. For each document:
         a. Run OCR (services.ocr.process_document)
         b. Classify (services.classification.classify_document)
         c. Extract fields (services.extraction.extract_fields)
      4. Run validation (services.validation.validate_application)
      5. Run cross-document verification (services.verification.verify_application)
      6. Run risk assessment (services.risk_engine.assess_risk)
      7. Update application status to "review"
      8. Return pipeline summary

    Error handling:
      - If any step fails, log the error and continue with remaining steps
      - Set document status to "failed" with error message for failed documents
      - Set application status to "review" even if some documents failed

    TODO: implement pipeline orchestration
    """
    raise NotImplementedError("process_application() is not implemented")


async def get_pipeline_status(app_id: str, db: AsyncSession) -> dict:
    """
    Check the current pipeline processing status for an application.

    Returns:
      {"application_id": app_id, "status": "processing",
       "documents": [{"doc_id": "DOC-0001", "status": "ocr_complete"}, ...],
       "current_step": "extraction", "progress_percent": 60}

    TODO: implement status tracking
    """
    raise NotImplementedError("get_pipeline_status() is not implemented")
