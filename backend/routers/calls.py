"""
Calls router — call management and detail endpoints.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from models.call import CallInitiate, CallResponse, CallDetailResponse, CallEventResponse
from database import db_select, db_insert

logger = logging.getLogger("riseagent.routers.calls")
router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("/initiate", response_model=CallResponse)
async def initiate_call_endpoint(payload: CallInitiate):
    """Manually initiate a call to a lead."""
    from services.call_service import initiate_call
    leads = await db_select("leads", filters={"id": payload.lead_id})
    if not leads:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead = leads[0]
    phone = payload.phone or lead.get("phone", "")
    if not phone:
        raise HTTPException(status_code=400, detail="No phone number provided")
    try:
        call = await initiate_call(payload.lead_id, phone)
        return CallResponse(**call)
    except Exception as exc:
        logger.error("Call initiation failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("", response_model=list[CallResponse])
async def list_calls(
    lead_id: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
):
    """List calls, optionally filtered by lead_id."""
    filters = {}
    if lead_id:
        filters["lead_id"] = lead_id
    calls = await db_select("calls", filters=filters, order_by="started_at", order_desc=True, limit=limit)
    return [CallResponse(**c) for c in calls]


@router.get("/{call_id}", response_model=CallDetailResponse)
async def get_call_detail(call_id: str):
    """Get full call detail including transcript and score."""
    calls = await db_select("calls", filters={"id": call_id})
    if not calls:
        raise HTTPException(status_code=404, detail="Call not found")
    call = calls[0]

    # Get conversation events
    events = await db_select("call_events", filters={"call_id": call_id}, order_by="turn_number", order_desc=False)

    # Get score
    scores = await db_select("scores", filters={"call_id": call_id})
    score = scores[0] if scores else None

    # Get lead info
    lead = None
    if call.get("lead_id"):
        leads = await db_select("leads", filters={"id": call["lead_id"]})
        lead = leads[0] if leads else None

    return CallDetailResponse(
        call=CallResponse(**call),
        events=[CallEventResponse(**e) for e in events],
        score=score,
        lead=lead,
    )
