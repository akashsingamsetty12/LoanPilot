"""LoanPilot API Routers — endpoint definitions."""

from routers.applications import router as applications_router
from routers.documents import router as documents_router
from routers.ocr import router as ocr_router
from routers.classification import router as classification_router
from routers.extraction import router as extraction_router
from routers.validation import router as validation_router
from routers.verification import router as verification_router
from routers.risk import router as risk_router
from routers.agent import router as agent_router
from routers.report import router as report_router
from routers.pipeline import router as pipeline_router

all_routers = [
    applications_router,
    documents_router,
    ocr_router,
    classification_router,
    extraction_router,
    validation_router,
    verification_router,
    risk_router,
    agent_router,
    report_router,
    pipeline_router,
]
