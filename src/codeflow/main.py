"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .core.config import get_settings
from .core.logging import setup_logging
from .core.webhook_handler import WebhookHandler

logger = logging.getLogger(__name__)

# Global webhook handler (initialized at startup)
webhook_handler: WebhookHandler | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager - runs on startup and shutdown."""
    global webhook_handler

    settings = get_settings()

    # Startup
    setup_logging()
    logger.info(f"🚀 Starting CodeFlow AI (Environment: {settings.environment})")
    logger.info(f"Debug mode: {settings.debug}")

    # Initialize webhook handler
    webhook_handler = WebhookHandler()
    logger.info("✅ Webhook handler ready")

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
        "ai_agent": "ready" if webhook_handler else "not initialized",
    }


@app.post("/webhook/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook events"""
    from src.codeflow.core.webhook_handler import get_webhook_handler

    # Get event type
    event_type = request.headers.get("X-GitHub-Event")

    # Get payload
    payload = await request.json()

    # Get webhook handler
    handler = get_webhook_handler()

    # Route to appropriate handler
    if event_type == "pull_request":
        result = await handler.handle_pull_request(payload)
        return result
    elif event_type == "pull_request_review":
        result = await handler.handle_pull_request_review(payload)
        return result
    else:
        return {"status": "ignored", "event": event_type}


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
