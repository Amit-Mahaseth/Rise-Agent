"""
Dashboard router — aggregated stats and analytics endpoints.
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, Query
from database import db_select, db_count, db_update

logger = logging.getLogger("riseagent.routers.dashboard")
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats():
    """Return aggregated dashboard statistics."""
    all_leads = await db_select("leads")
    all_calls = await db_select("calls")
    all_scores = await db_select("scores")
    rm_queue = await db_select("rm_queue")

    total = len(all_leads)
    contacted = len([l for l in all_leads if l.get("status") != "pending"])
    hot = len([l for l in all_leads if l.get("status") in ("hot", "hot_rm_queued")])
    warm = len([l for l in all_leads if l.get("status") in ("warm", "warm_whatsapp_sent")])
    cold = len([l for l in all_leads if l.get("status") == "cold"])
    conversion_pct = round((hot / total * 100) if total > 0 else 0, 1)

    # Funnel data
    engaged = len([c for c in all_calls if c.get("duration_seconds", 0) > 30])
    qualified = len([s for s in all_scores if s.get("total_score", 0) >= 35])
    rm_handed = len(rm_queue)

    # Recent calls
    recent_calls = await db_select("calls", order_by="started_at", order_desc=True, limit=10)
    recent_with_info = []
    for call in recent_calls:
        lead_id = call.get("lead_id")
        leads = await db_select("leads", filters={"id": lead_id}) if lead_id else []
        lead = leads[0] if leads else {}
        scores = await db_select("scores", filters={"call_id": call.get("id")})
        score = scores[0] if scores else {}
        recent_with_info.append({
            "call_id": call.get("id"),
            "lead_name": lead.get("name", "Unknown"),
            "phone": lead.get("phone", ""),
            "status": call.get("status", "unknown"),
            "duration": call.get("duration_seconds", 0),
            "language": call.get("language_used") or lead.get("language", "unknown"),
            "classification": score.get("classification", "pending"),
            "score": score.get("total_score", 0),
            "started_at": call.get("started_at"),
        })

    # LLM provider usage breakdown
    all_events = await db_select("call_events")
    provider_counts = {}
    for evt in all_events:
        p = evt.get("provider", "unknown") or "unknown"
        provider_counts[p] = provider_counts.get(p, 0) + 1

    return {
        "stats": {
            "total_leads": total,
            "contacted": contacted,
            "hot": hot,
            "warm": warm,
            "cold": cold,
            "conversion_pct": conversion_pct,
        },
        "funnel": {
            "contacted": contacted,
            "engaged": engaged,
            "qualified": qualified,
            "rm_handed_off": rm_handed,
        },
        "distribution": {
            "hot": hot,
            "warm": warm,
            "cold": cold,
            "pending": total - contacted,
        },
        "provider_usage": provider_counts,
        "recent_calls": recent_with_info,
    }


@router.get("/rm-queue")
async def get_rm_queue():
    """Return RM queue items with lead info."""
    queue = await db_select("rm_queue", order_by="queued_at", order_desc=True)
    enriched = []
    for item in queue:
        lead_id = item.get("lead_id")
        leads = await db_select("leads", filters={"id": lead_id}) if lead_id else []
        lead = leads[0] if leads else {}
        scores = await db_select("scores", filters={"lead_id": lead_id})
        score = scores[0] if scores else {}
        enriched.append({
            **item,
            "lead_name": lead.get("name", "Unknown"),
            "phone": lead.get("phone", ""),
            "language": lead.get("language", "unknown"),
            "score": score.get("total_score", 0),
        })
    return {"queue": enriched}


@router.put("/rm-queue/{item_id}/status")
async def update_rm_status(item_id: str, status: str = Query(...)):
    """Update RM queue item status."""
    from datetime import datetime, timezone
    valid = {"pending", "called", "converted", "lost"}
    if status not in valid:
        from fastapi import HTTPException
        raise HTTPException(400, f"Status must be one of {valid}")
    update = {"rm_status": status}
    if status in ("converted", "lost", "called"):
        update["actioned_at"] = datetime.now(timezone.utc).isoformat()
    result = await db_update("rm_queue", item_id, update)
    return {"status": "updated", "item": result}
