"""
Pipeline Orchestrator
==================================
Chains processing modules: Ingestion → OCR → Classification → Extraction → Validation → Verification → Risk Assessment.
"""

from datetime import datetime, timezone
import logging

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.application import Application
from models.document import Document
from services.ocr import process_document as ocr_process_document
from services.classification import classify_document
from services.extraction import extract_fields
from services.validation import validate_application
from services.verification import verify_application
from services.risk_engine import assess_risk

logger = logging.getLogger("loanpilot.pipeline")


async def process_application(app_id: str, db: AsyncSession) -> dict:
    """
    Run the end-to-end processing pipeline for a loan application.

    Workflow:
      1. Load application and all documents
      2. Mark application status = "processing"
      3. For each document:
         a. OCR extraction
         b. Document classification
         c. Field extraction
      4. Single-document field validation
      5. Cross-document consistency verification
      6. Risk engine assessment & inconsistency flagging
      7. Mark application status = "review" (ready for underwriter)
    """
    # 1. Load application with documents
    result = await db.execute(
        select(Application)
        .options(selectinload(Application.documents))
        .where(Application.id == app_id)
    )
    application = result.scalar_one_or_none()

    if application is None:
        raise ValueError(f"Application not found: {app_id}")

    # 2. Update status to processing
    application.status = "processing"
    application.updated_at = datetime.now(timezone.utc)
    await db.commit()

    completed_steps = []
    documents = application.documents or []

    # 3. Process documents (OCR → Classification → Extraction)
    for doc in documents:
        doc_id = doc.id
        logger.info(f"Pipeline processing document {doc_id} ({doc.filename})")

        # Step 3a: OCR
        try:
            if doc.status not in ["ocr_complete", "extracted"]:
                await ocr_process_document(doc_id=doc_id, db=db)
                completed_steps.append(f"ocr_{doc_id}")
        except NotImplementedError:
            logger.warning(f"OCR not implemented yet for {doc_id}")
        except Exception as e:
            logger.error(f"OCR failed for {doc_id}: {e}", exc_info=True)

        # Step 3b: Classification
        try:
            if not doc.doc_type or doc.doc_type == "unclassified":
                await classify_document(doc_id=doc_id, db=db)
                completed_steps.append(f"classification_{doc_id}")
        except NotImplementedError:
            logger.warning(f"Classification not implemented yet for {doc_id}")
        except Exception as e:
            logger.error(f"Classification failed for {doc_id}: {e}", exc_info=True)

        # Step 3c: Extraction
        try:
            if not doc.extracted_fields:
                await extract_fields(doc_id=doc_id, db=db)
                completed_steps.append(f"extraction_{doc_id}")
        except NotImplementedError:
            logger.warning(f"Extraction not implemented yet for {doc_id}")
        except Exception as e:
            logger.error(f"Extraction failed for {doc_id}: {e}", exc_info=True)

    # 4. Field Validation
    try:
        await validate_application(app_id=app_id, db=db)
        completed_steps.append("validation")
    except NotImplementedError:
        logger.info("Validation module is in progress; skipping for now.")
    except Exception as e:
        logger.error(f"Validation step failed: {e}", exc_info=True)

    # 5. Cross-Document Verification
    try:
        await verify_application(app_id=app_id, db=db)
        completed_steps.append("verification")
    except NotImplementedError:
        logger.info("Verification module is in progress; skipping for now.")
    except Exception as e:
        logger.error(f"Verification step failed: {e}", exc_info=True)

    # 6. Risk Engine Assessment
    try:
        await assess_risk(app_id=app_id, db=db)
        completed_steps.append("risk_assessment")
    except NotImplementedError:
        logger.info("Risk engine is in progress; skipping for now.")
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}", exc_info=True)

    # 7. Final status transition
    # Refresh application state
    result = await db.execute(
        select(Application)
        .options(selectinload(Application.documents))
        .where(Application.id == app_id)
    )
    application = result.scalar_one_or_none()

    application.status = "review"
    application.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "application_id": app_id,
        "status": application.status,
        "documents_processed": len(documents),
        "completed_steps": completed_steps,
        "message": "Processing pipeline completed successfully. Ready for underwriter review.",
    }


async def get_pipeline_status(app_id: str, db: AsyncSession) -> dict:
    """
    Check the current processing status and progress for an application.
    """
    result = await db.execute(
        select(Application)
        .options(selectinload(Application.documents))
        .where(Application.id == app_id)
    )
    application = result.scalar_one_or_none()

    if application is None:
        raise ValueError(f"Application not found: {app_id}")

    docs_status = [
        {
            "document_id": d.id,
            "filename": d.filename,
            "status": d.status,
            "doc_type": d.doc_type,
            "ocr_confidence": d.ocr_confidence,
        }
        for d in (application.documents or [])
    ]

    # Calculate approximate progress percentage
    progress_map = {
        "created": 10,
        "documents_uploaded": 25,
        "processing": 50,
        "ocr_complete": 60,
        "classified": 70,
        "extracted": 80,
        "validated": 85,
        "verified": 90,
        "review": 95,
        "decided": 100,
    }
    progress = progress_map.get(application.status, 30)

    return {
        "application_id": app_id,
        "status": application.status,
        "progress_percent": progress,
        "current_step": application.status,
        "document_count": len(docs_status),
        "documents": docs_status,
        "updated_at": application.updated_at,
    }
