"""
LoanPilot API — Main Entry Point
==================================
FastAPI application with all routers, middleware, and lifecycle events.

Run with: uvicorn main:app --reload
Swagger UI: http://localhost:8000/docs
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import init_db, close_db
from middleware.error_handler import register_exception_handlers
from middleware.logging import setup_logging, log_request_middleware
from routers import all_routers

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    setup_logging()
    await init_db()
    settings.upload_path  # Ensure uploads directory exists
    yield
    # Shutdown
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="LoanPilot API",
    description="AI-powered Loan Document Processing & Verification Agent",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# ── Middleware ──

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging
app.middleware("http")(log_request_middleware)

# Error handling
register_exception_handlers(app)

# ── Register Routers ──

for router in all_routers:
    app.include_router(router, prefix="/api/v1")


# ── Health Check ──

@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "app": settings.APP_NAME,
    }
