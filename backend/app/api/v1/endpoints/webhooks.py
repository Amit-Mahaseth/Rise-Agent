"""
Webhook endpoints for external services.
"""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db
from app.services.voice_service import VoiceService
from app.services.whatsapp_service import WhatsAppService
from app import models
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/twilio/call-status")
async def twilio_call_status(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Twilio call status callbacks.

    Args:
        request: HTTP request
        background_tasks: FastAPI background tasks
        db: Database session
    """
    try:
        # Get form data from Twilio
        form_data = await request.form()
        data = dict(form_data)

        call_sid = data.get("CallSid")
        call_status = data.get("CallStatus")
        call_duration = data.get("CallDuration")

        logger.info(
            "Twilio call status callback",
            call_sid=call_sid,
            status=call_status,
            duration=call_duration
        )

        # Find call by Twilio SID
        result = await db.execute(
            select(models.CallRecord).where(models.CallRecord.twilio_call_sid == call_sid)
        )
        call = result.scalar_one_or_none()

        if call:
            # Map Twilio status to our status
            status_mapping = {
                "queued": "queued",
                "initiated": "initiated",
                "ringing": "ringing",
                "answered": "answered",
                "completed": "completed",
                "busy": "busy",
                "no-answer": "no_answer",
                "failed": "failed",
                "canceled": "canceled"
            }

            mapped_status = status_mapping.get(call_status, "unknown")

            # Update call record
            call.status = mapped_status
            if call_duration:
                call.duration_seconds = int(call_duration)

            await db.commit()

            # Handle call completion
            if call_status == "completed":
                voice_service = VoiceService(db)
                background_tasks.add_task(
                    voice_service.handle_call_event,
                    call.id,
                    "completed",
                    {"duration": call_duration}
                )

        return {"status": "received"}

    except Exception as e:
        logger.error("Failed to handle Twilio callback", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process callback")


@router.post("/twilio/whatsapp")
async def twilio_whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Handle incoming WhatsApp messages from Twilio.

    Args:
        request: HTTP request
        background_tasks: FastAPI background tasks
    """
    try:
        # Get form data from Twilio
        form_data = await request.form()
        data = dict(form_data)

        from_number = data.get("From")
        to_number = data.get("To")
        message_body = data.get("Body")
        message_sid = data.get("MessageSid")

        logger.info(
            "WhatsApp message received",
            from_number=from_number,
            to_number=to_number,
            message_sid=message_sid,
            message_length=len(message_body) if message_body else 0
        )

        # Handle incoming message
        if message_body and from_number:
            whatsapp_service = WhatsAppService()
            background_tasks.add_task(
                whatsapp_service.handle_incoming_message,
                from_number,
                message_body
            )

        return {"status": "received"}

    except Exception as e:
        logger.error("Failed to handle WhatsApp webhook", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process webhook")


@router.post("/twilio/voice")
async def twilio_voice_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Twilio voice call webhooks.

    Args:
        request: HTTP request
        background_tasks: FastAPI background tasks
        db: Database session
    """
    try:
        # Get form data from Twilio
        form_data = await request.form()
        data = dict(form_data)

        call_sid = data.get("CallSid")
        speech_result = data.get("SpeechResult")
        confidence = data.get("Confidence")

        logger.info(
            "Voice webhook received",
            call_sid=call_sid,
            speech_result_length=len(speech_result) if speech_result else 0,
            confidence=confidence
        )

        # Find call by Twilio SID
        result = await db.execute(
            select(models.CallRecord).where(models.CallRecord.twilio_call_sid == call_sid)
        )
        call = result.scalar_one_or_none()

        if call and speech_result:
            # Process speech input
            voice_service = VoiceService(db)
            background_tasks.add_task(
                voice_service.process_audio_input,
                call.id,
                speech_result.encode(),  # Convert to bytes
                call.detected_language or "en"
            )

        return {"status": "received"}

    except Exception as e:
        logger.error("Failed to handle voice webhook", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process webhook")


@router.get("/health")
async def webhook_health_check():
    """
    Health check endpoint for webhooks.

    Returns:
        Health status
    """
    return {"status": "healthy", "service": "webhooks"}