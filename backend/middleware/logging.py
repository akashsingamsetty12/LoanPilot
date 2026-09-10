"""
Logging Middleware
==================
Structured request logging and pipeline step logging.
"""

import logging
import time
from fastapi import Request

from config import get_settings


def setup_logging():
    """Configure application-wide logging."""
    settings = get_settings()

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )


# Module-specific loggers (import these in your service files)
logger = logging.getLogger("loanpilot")
pipeline_logger = logging.getLogger("loanpilot.pipeline")
ocr_logger = logging.getLogger("loanpilot.ocr")
llm_logger = logging.getLogger("loanpilot.llm")
api_logger = logging.getLogger("loanpilot.api")


async def log_request_middleware(request: Request, call_next):
    """Log every API request with method, path, status, and duration."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    api_logger.info(
        "%s %s → %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response
