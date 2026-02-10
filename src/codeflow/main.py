"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .core.config import get_settings
from .core.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager - runs on startup and shutdown."""
    settings = get_settings()

    # Startup
    setup_logging()
    logger.info(f"🚀 Starting CodeFlow AI (Environment: {settings.environment})")
    logger.info(f"Debug mode: {settings.debug}")

    yield

    # Shutdown
    logger.info("👋 Shutting down CodeFlow AI")


# Create FastAPI app
app = FastAPI(
    title="CodeFlow AI",
    description="AI-powered Pull Request review automation",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - basic info about the service."""
    return {
        "service": "CodeFlow AI",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring."""
    settings = get_settings()
    return {
        "status": "healthy",
        "environment": settings.environment,
        "debug": str(settings.debug),
    }


@app.post("/webhook/github")
async def github_webhook(request: Request) -> JSONResponse:
    """
    Receive GitHub webhook events.

    This is where GitHub will send PR events (opened, synchronized, etc.)
    """
    # Get the event type from headers
    event_type = request.headers.get("X-GitHub-Event", "unknown")

    # Get the request body
    payload = await request.json()

    logger.info(f"📬 Received GitHub webhook: {event_type}")
    logger.debug(f"Payload: {payload}")

    # For now, just acknowledge receipt
    # We'll add actual processing logic later
    return JSONResponse(
        content={
            "status": "received",
            "event_type": event_type,
            "message": "Webhook received successfully",
        },
        status_code=200,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for uncaught errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    settings = get_settings()
    error_detail = str(exc) if settings.debug else "Internal server error"

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": error_detail,
        },
    )
