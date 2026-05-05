"""
WhatsApp messaging service via Meta Cloud API.
Sends pre-approved template messages for warm lead follow-up.
"""

from __future__ import annotations

import logging
import httpx
from config import get_settings
from database import db_insert

logger = logging.getLogger("riseagent.whatsapp")
META_GRAPH_API = "https://graph.facebook.com/v18.0"


async def send_followup_whatsapp(
    lead_id: str, lead_name: str, lead_phone: str,
    signup_link: str = "https://rise.rupeezy.in/signup",
) -> dict:
    settings = get_settings()

    # Guard: never call real Meta API in demo mode
    if settings.demo_mode:
        logger.info("DEMO MODE: WhatsApp message skipped for %s (%s)", lead_name, lead_phone)
        return {"lead_id": lead_id, "status": "demo_skipped", "reason": "demo_mode"}

    if not settings.whatsapp_token or not settings.whatsapp_phone_number_id:
        logger.warning("WhatsApp credentials not configured — skipping")
        return {"lead_id": lead_id, "status": "skipped", "reason": "no credentials"}

    wa_phone = lead_phone.lstrip("+")
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": wa_phone,
        "type": "template",
        "template": {
            "name": "rupeezy_ap_followup",
            "language": {"code": "en"},
            "components": [{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": lead_name},
                    {"type": "text", "text": signup_link},
                ],
            }],
        },
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{META_GRAPH_API}/{settings.whatsapp_phone_number_id}/messages",
                json=payload, headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            msg_id = data.get("messages", [{}])[0].get("id", "unknown")
            logger.info("WhatsApp sent to %s: %s", lead_name, msg_id)
            return {"lead_id": lead_id, "status": "sent", "message_id": msg_id}
    except Exception as exc:
        logger.error("WhatsApp send failed: %s", exc)
        return {"lead_id": lead_id, "status": "failed", "error": str(exc)}
