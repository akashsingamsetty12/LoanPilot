"""
Error Handler Middleware
=========================
Global exception handling for consistent API error responses.
All errors return JSON: {"error_code": "...", "detail": "...", "timestamp": "..."}
"""

from datetime import datetime, timezone
from fastapi import Request, HTTPException as FastAPIHTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


# ── Custom Exceptions ──

class LoanPilotException(Exception):
    """Base exception for LoanPilot application errors."""

    def __init__(self, detail: str, status_code: int = 500, error_code: str = "INTERNAL_ERROR"):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(detail)


class ApplicationNotFoundError(LoanPilotException):
    def __init__(self, app_id: str):
        super().__init__(
            detail=f"Application '{app_id}' not found",
            status_code=404,
            error_code="APPLICATION_NOT_FOUND",
        )


class DocumentNotFoundError(LoanPilotException):
    def __init__(self, doc_id: str):
        super().__init__(
            detail=f"Document '{doc_id}' not found",
            status_code=404,
            error_code="DOCUMENT_NOT_FOUND",
        )


class FileValidationError(LoanPilotException):
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=422, error_code="FILE_VALIDATION_ERROR")


class OCRProcessingError(LoanPilotException):
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=500, error_code="OCR_PROCESSING_ERROR")


class LLMServiceError(LoanPilotException):
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=502, error_code="LLM_SERVICE_ERROR")


class PipelineError(LoanPilotException):
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=500, error_code="PIPELINE_ERROR")


# ── Exception Handlers ──

async def loanpilot_exception_handler(request: Request, exc: LoanPilotException) -> JSONResponse:
    """Handle all LoanPilot custom exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "detail": exc.detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled exceptions, preserving HTTP exceptions."""
    if isinstance(exc, (FastAPIHTTPException, StarletteHTTPException)):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": "HTTP_ERROR",
                "detail": exc.detail,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            headers=getattr(exc, "headers", None),
        )

    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_ERROR",
            "detail": str(exc) if str(exc) else "An unexpected error occurred",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(LoanPilotException, loanpilot_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
