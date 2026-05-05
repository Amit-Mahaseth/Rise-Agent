"""
Outbound call service.
Supports Exotel (default) and Twilio as call providers.
In demo mode, runs the full conversation simulation instead.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

import httpx

from config import get_settings
from database import db_insert, db_update, db_select

logger = logging.getLogger("riseagent.call_service")


async def initiate_call(lead_id: str, phone: str) -> dict:
    """Initiate an outbound call to a lead. Returns call record."""
    settings = get_settings()

    # Get call count for this lead
    existing_calls = await db_select("calls", filters={"lead_id": lead_id})
    call_number = len(existing_calls) + 1

    # Create call record
    call_record = {
        "lead_id": lead_id,
        "call_sid": f"demo_{uuid.uuid4().hex[:12]}" if settings.demo_mode else None,
        "provider": "demo" if settings.demo_mode else settings.call_provider,
        "status": "initiated",
        "duration_seconds": 0,
        "call_number": call_number,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    if settings.demo_mode:
        call_record["status"] = "in_progress"
        result = await db_insert("calls", call_record)
        logger.info("Demo call initiated for lead %s (call #%d)", lead_id, call_number)
        return result

    # Real call via provider
    if settings.call_provider == "exotel":
        call_sid = await _initiate_exotel(phone, lead_id)
    elif settings.call_provider == "twilio":
        call_sid = await _initiate_twilio(phone, lead_id)
    else:
        raise ValueError(f"Unknown call provider: {settings.call_provider}")

    call_record["call_sid"] = call_sid
    call_record["status"] = "ringing"
    result = await db_insert("calls", call_record)
    logger.info("Call initiated via %s: sid=%s", settings.call_provider, call_sid)
    return result


async def _initiate_exotel(phone: str, lead_id: str) -> str:
    """Make outbound call via Exotel API."""
    settings = get_settings()
    url = (
        f"https://{settings.exotel_api_key}:{settings.exotel_api_token}"
        f"@api.exotel.com/v1/Accounts/{settings.exotel_sid}/Calls/connect"
    )
    payload = {
        "From": phone,
        "CallerId": settings.exotel_caller_id,
        "Url": f"{settings.base_url}/webhooks/exotel/stream",
        "StatusCallback": f"{settings.base_url}/webhooks/exotel",
        "StatusCallbackEvents[0]": "terminal",
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, data=payload)
            resp.raise_for_status()
            data = resp.json()
            call_sid = data.get("Call", {}).get("Sid", f"exo_{uuid.uuid4().hex[:8]}")
            return call_sid
    except Exception as exc:
        logger.error("Exotel call initiation failed: %s", exc)
        raise


async def _initiate_twilio(phone: str, lead_id: str) -> str:
    """Make outbound call via Twilio API."""
    settings = get_settings()
    try:
        from twilio.rest import Client
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        call = client.calls.create(
            to=phone,
            from_=settings.twilio_phone_number,
            url=f"{settings.base_url}/webhooks/twilio/stream",
            status_callback=f"{settings.base_url}/webhooks/twilio",
            status_callback_event=["initiated", "ringing", "answered", "completed"],
        )
        return call.sid
    except Exception as exc:
        logger.error("Twilio call initiation failed: %s", exc)
        raise


async def end_call(call_id: str, duration_seconds: int = 0) -> dict:
    """Mark a call as completed."""
    update = {
        "status": "completed",
        "duration_seconds": duration_seconds,
        "ended_at": datetime.now(timezone.utc).isoformat(),
    }
    result = await db_update("calls", call_id, update)
    logger.info("Call %s ended (duration: %ds)", call_id, duration_seconds)
    return result
