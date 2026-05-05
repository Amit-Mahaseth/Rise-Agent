"""
Leads router — lead ingestion and management endpoints.
"""

from __future__ import annotations

import logging
import asyncio
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query

from models.lead import LeadCreate, LeadResponse, LeadListResponse
from database import db_insert, db_select, db_count, db_update
from config import get_settings
from services.language import get_language_code

logger = logging.getLogger("riseagent.routers.leads")
router = APIRouter(prefix="/leads", tags=["leads"])


async def _run_demo_simulation(lead_id: str, phone: str):
    """Background task: run demo simulation for a new lead."""
    from demo.simulator import get_persona_by_phone, simulate_call
    persona = get_persona_by_phone(phone)
    if persona:
        try:
            result = await simulate_call(lead_id, persona)
            logger.info("Demo simulation completed for %s", lead_id)
        except Exception as exc:
            logger.error("Demo simulation failed for %s: %s", lead_id, exc)
    else:
        logger.info("No matching persona for phone %s — skipping simulation", phone)


@router.post("/new", response_model=LeadResponse, status_code=200)
async def create_lead(payload: LeadCreate, background_tasks: BackgroundTasks):
    """
    Create a new lead and immediately trigger a call.
    In demo mode, runs the full conversation simulation in the background.
    """
    settings = get_settings()
    language = get_language_code(payload.language_hint) if payload.language_hint else "unknown"

    lead_data = {
        "name": payload.name,
        "phone": payload.phone,
        "language": language,
        "source": payload.source or "manual",
        "status": "pending",
    }

    try:
        lead = await db_insert("leads", lead_data)
    except Exception as exc:
        logger.error("Failed to insert lead: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to create lead: {exc}")

    lead_id = lead["id"]

    # Trigger call in background (do not wait)
    if settings.demo_mode:
        background_tasks.add_task(_run_demo_simulation, lead_id, payload.phone)
    else:
        from services.call_service import initiate_call
        background_tasks.add_task(initiate_call, lead_id, payload.phone)

    logger.info("Lead created: %s (%s) — call triggered", payload.name, lead_id)
    return LeadResponse(**lead)


@router.get("", response_model=LeadListResponse)
async def list_leads(
    status: Optional[str] = Query(default=None, description="Filter by status"),
    search: Optional[str] = Query(default=None, description="Search by name or phone"),
    limit: int = Query(default=50, ge=1, le=200),
):
    """List all leads with optional filters."""
    filters = {}
    if status and status != "all":
        filters["status"] = status

    leads = await db_select("leads", filters=filters, order_by="created_at", order_desc=True, limit=limit)

    # Apply search filter in memory (Supabase would use ilike)
    if search:
        search_lower = search.lower()
        leads = [
            l for l in leads
            if search_lower in l.get("name", "").lower()
            or search_lower in l.get("phone", "")
        ]

    return LeadListResponse(
        leads=[LeadResponse(**l) for l in leads],
        total=len(leads),
    )


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str):
    """Get a single lead by ID."""
    leads = await db_select("leads", filters={"id": lead_id})
    if not leads:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse(**leads[0])


@router.post("/demo/seed")
async def seed_demo_leads(background_tasks: BackgroundTasks):
    """Seed all 5 demo personas and run simulations."""
    from demo.simulator import load_personas
    settings = get_settings()
    if not settings.demo_mode:
        raise HTTPException(status_code=400, detail="Demo mode is not enabled")

    personas = load_personas()
    results = []

    for persona in personas:
        lead_data = {
            "name": persona["name"],
            "phone": persona["phone"],
            "language": persona["language"],
            "source": "demo",
            "status": "pending",
        }
        lead = await db_insert("leads", lead_data)
        lead_id = lead["id"]
        background_tasks.add_task(_run_demo_simulation, lead_id, persona["phone"])
        results.append({"lead_id": lead_id, "name": persona["name"], "status": "simulation_queued"})

    return {"message": f"Seeded {len(results)} demo leads", "leads": results}
