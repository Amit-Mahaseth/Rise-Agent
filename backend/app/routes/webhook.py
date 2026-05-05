import base64
import binascii
import logging
import time

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_realtime_call_service
from app.db.session import get_db
from app.repositories.lead_repository import LeadRepository

router = APIRouter()
logger = logging.getLogger(__name__)


class LeadWebhookPayload(BaseModel):
    lead_id: str
    full_name: str
    phone_number: str
    source: str = "webhook"
    product_interest: str = "personal-loan"


@router.post("/lead")
async def lead_webhook(
    payload: LeadWebhookPayload,
    db: Session = Depends(get_db),
    call_service=Depends(get_realtime_call_service),
) -> dict:
    repo = LeadRepository()
    lead = repo.get(db, payload.lead_id) or repo.create(db, payload)
    call_result = await call_service.initiate_call(lead.lead_id, lead.phone_number)
    await call_service.ensure_session_runner(call_result["call_id"])
    return {"status": "accepted", "lead_id": lead.lead_id, "call": call_result}


@router.post("/voice")
async def voice_webhook(request: Request, call_service=Depends(get_realtime_call_service)) -> dict:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        form = await request.form()
        payload = {k: v for k, v in form.items()}

    twilio_payload = _normalize_twilio_payload(payload)
    call_sid = twilio_payload.get("call_sid") or payload.get("call_sid") or payload.get("call_id") or payload.get("CallSid")
    lead_id = twilio_payload.get("lead_id") or payload.get("lead_id")
    event = twilio_payload.get("event") or payload.get("event", "media")

    if event == "stop":
        await call_service.end_session(call_sid)
        return {"status": "stopped", "call_sid": call_sid}

    if event == "start" and call_sid:
        init = await call_service.initialize_media_stream(call_sid)
        return {"status": "started", "call_sid": call_sid, "lead_id": lead_id, **init}

    media_payload = twilio_payload.get("audio_payload") or payload.get("audio_chunk", "")
    if not media_payload and isinstance(payload.get("media"), dict):
        media_payload = payload["media"].get("payload", "")
    audio_chunk = _safe_b64decode(media_payload)

    if audio_chunk and call_sid:
        await call_service.enqueue_audio_chunk(call_sid, audio_chunk)

    return {"status": "received", "bytes": len(audio_chunk), "call_sid": call_sid}


def _normalize_twilio_payload(payload: dict) -> dict:
    # Twilio Media Stream sends JSON envelopes with `event` + `start/media/stop`.
    event = payload.get("event")
    if event in {"start", "media", "stop"}:
        stream_sid = payload.get("streamSid")
        start = payload.get("start") or {}
        media = payload.get("media") or {}
        stop = payload.get("stop") or {}
        return {
            "event": event,
            "call_sid": start.get("callSid") or stop.get("callSid") or payload.get("CallSid"),
            "stream_sid": stream_sid,
            "lead_id": start.get("customParameters", {}).get("lead_id"),
            "audio_payload": media.get("payload"),
            "timestamp": media.get("timestamp") or int(time.time() * 1000),
        }
    return {}


def _safe_b64decode(raw_payload: str) -> bytes:
    if not raw_payload:
        return b""
    try:
        return base64.b64decode(raw_payload)
    except (ValueError, binascii.Error):
        logger.warning("Invalid base64 media payload")
        return b""
