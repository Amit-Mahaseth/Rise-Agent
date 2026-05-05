"""
RM handoff and post-call routing service.
Routes leads to RM queue, WhatsApp follow-up, or cold storage based on score.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta

from database import db_insert, db_update
from services.whatsapp import send_followup_whatsapp

logger = logging.getLogger("riseagent.rm_handoff")


async def route_lead_post_call(
    lead_id: str,
    lead_name: str,
    lead_phone: str,
    call_id: str,
    classification: str,
    score: int,
    transcript: str,
    objections_raised: list[str],
    rebuttals_used: list[str],
    language: str,
) -> dict:
    """Route a lead based on classification after call ends."""
    if classification == "hot":
        return await _route_hot(
            lead_id, lead_name, lead_phone, call_id,
            score, transcript, objections_raised, rebuttals_used, language,
        )
    elif classification == "warm":
        return await _route_warm(lead_id, lead_name, lead_phone, call_id)
    else:
        return await _route_cold(lead_id)


async def _route_hot(
    lead_id, lead_name, lead_phone, call_id,
    score, transcript, objections_raised, rebuttals_used, language,
) -> dict:
    """HOT lead → insert into RM queue for immediate action."""
    rm_entry = {
        "lead_id": lead_id,
        "call_id": call_id,
        "transcript": transcript,
        "objections_raised": objections_raised,
        "rebuttals_used": rebuttals_used,
        "recommended_action": (
            f"Call {lead_name} at {lead_phone} immediately. "
            f"Score: {score}. Language: {language}. "
            f"Lead showed strong interest — connect to RISE Portal signup."
        ),
        "rm_status": "pending",
        "queued_at": datetime.now(timezone.utc).isoformat(),
    }
    await db_insert("rm_queue", rm_entry)
    await db_update("leads", lead_id, {"status": "hot_rm_queued"})
    logger.info("HOT lead %s queued for RM", lead_id)
    return {"action": "rm_queued", "lead_id": lead_id, "classification": "hot"}


async def _route_warm(lead_id, lead_name, lead_phone, call_id) -> dict:
    """WARM lead → send WhatsApp follow-up."""
    wa_result = await send_followup_whatsapp(lead_id, lead_name, lead_phone)
    await db_update("leads", lead_id, {"status": "warm_whatsapp_sent"})
    logger.info("WARM lead %s — WhatsApp sent: %s", lead_id, wa_result.get("status"))
    return {"action": "whatsapp_sent", "lead_id": lead_id, "classification": "warm", "whatsapp": wa_result}


async def _route_cold(lead_id) -> dict:
    """COLD lead → mark cold, set re-engage date 30 days out."""
    re_engage = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    await db_update("leads", lead_id, {
        "status": "cold",
        "re_engage_after": re_engage,
    })
    logger.info("COLD lead %s — re-engage after %s", lead_id, re_engage[:10])
    return {"action": "cold_logged", "lead_id": lead_id, "classification": "cold", "re_engage_after": re_engage}
