"""
RiseAgent AI — FastAPI application entry point.
"""

from __future__ import annotations

import logging
import sys

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routers import leads, calls, webhooks, dashboard

# ── Logging ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-30s | %(levelname)-5s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("riseagent")

# ── Settings validation ──────────────────────────────────────────
settings = get_settings()
missing = settings.validate_required()
if missing:
    logger.warning("Missing env vars (non-fatal in demo mode): %s", ", ".join(missing))

# ── FastAPI app ──────────────────────────────────────────────────
app = FastAPI(
    title="RiseAgent AI",
    description=(
        "Production-grade multilingual AI voice agent for "
        "Rupeezy's Authorized Person lead conversion program."
    ),
    version="1.0.0",
)

# ── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount routers ────────────────────────────────────────────────
app.include_router(leads.router)
app.include_router(calls.router)
app.include_router(webhooks.router)
app.include_router(dashboard.router)


# ── Health check ─────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "service": "RiseAgent AI",
        "version": "1.0.0",
        "demo_mode": settings.demo_mode,
        "status": "operational",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "demo_mode": settings.demo_mode}


# ── Startup event ────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("=" * 60)
    logger.info("RiseAgent AI starting up")
    logger.info("Demo mode: %s", settings.demo_mode)
    logger.info("Call provider: %s", settings.call_provider)
    logger.info("Frontend URL: %s", settings.frontend_url)
    logger.info("=" * 60)

    # Pre-load knowledge base in background
    try:
        from knowledge.loader import load_knowledge_base
        load_knowledge_base()
        logger.info("Knowledge base loaded successfully")
    except Exception as exc:
        logger.warning("Knowledge base pre-load failed (will retry on first use): %s", exc)
