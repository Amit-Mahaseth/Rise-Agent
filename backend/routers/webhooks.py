"""
Webhooks router — Exotel and Twilio callback handlers.
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, Request, Response
from database import db_select, db_update

logger = logging.getLogger("riseagent.routers.webhooks")
router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/exotel")
async def exotel_status_callback(request: Request):
    """Handle Exotel call status callback."""
    try:
        form = await request.form()
        call_sid = form.get("CallSid", "")
        status = form.get("Status", "")
        duration = form.get("Duration", "0")
        logger.info("Exotel webhook: sid=%s status=%s duration=%s", call_sid, status, duration)

        if call_sid:
            calls = await db_select("calls", filters={"call_sid": call_sid})
            if calls:
                call = calls[0]
                update = {"status": status.lower()}
                if status.lower() in ("completed", "no-answer", "busy", "failed"):
                    update["duration_seconds"] = int(duration)
                await db_update("calls", call["id"], update)
    except Exception as exc:
        logger.error("Exotel webhook error: %s", exc)
    return Response(status_code=200)


@router.post("/exotel/stream")
async def exotel_stream(request: Request):
    """Handle Exotel audio stream for real-time conversation."""
    logger.info("Exotel stream endpoint hit")
    return Response(content="<Response><Say>Hello</Say></Response>", media_type="application/xml")


@router.post("/twilio")
async def twilio_status_callback(request: Request):
    """Handle Twilio call status callback."""
    try:
        form = await request.form()
        call_sid = form.get("CallSid", "")
        status = form.get("CallStatus", "")
        duration = form.get("CallDuration", "0")
        logger.info("Twilio webhook: sid=%s status=%s duration=%s", call_sid, status, duration)

        if call_sid:
            calls = await db_select("calls", filters={"call_sid": call_sid})
            if calls:
                call = calls[0]
                update = {"status": status.lower()}
                if status.lower() in ("completed", "no-answer", "busy", "failed"):
                    update["duration_seconds"] = int(duration)
                await db_update("calls", call["id"], update)
    except Exception as exc:
        logger.error("Twilio webhook error: %s", exc)
    return Response(status_code=200)


@router.post("/twilio/stream")
async def twilio_stream(request: Request):
    """Handle Twilio audio stream for real-time conversation."""
    logger.info("Twilio stream endpoint hit")
    from twilio.twiml.voice_response import VoiceResponse
    resp = VoiceResponse()
    resp.say("Hello from RiseAgent")
    return Response(content=str(resp), media_type="application/xml")
