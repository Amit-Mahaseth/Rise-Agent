"""
Call management API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app import schemas
from app.core.database import get_db
from app.services.voice_service import VoiceService
from app.services.conversation_service import ConversationService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/initiate/{lead_id}", response_model=schemas.CallResponse)
async def initiate_call(
    lead_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate outbound call to lead.

    Args:
        lead_id: Lead identifier
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Call response
    """
    try:
        voice_service = VoiceService(db)

        # Generate call ID
        import uuid
        call_id = str(uuid.uuid4())

        # Initiate call in background
        background_tasks.add_task(voice_service.initiate_outbound_call, lead_id, call_id)

        return schemas.CallResponse(
            call_id=call_id,
            status="queued",
            message="Call initiated successfully"
        )

    except Exception as e:
        logger.error("Failed to initiate call", error=str(e), lead_id=lead_id)
        raise HTTPException(status_code=500, detail="Failed to initiate call")


@router.post("/{call_id}/process-speech")
async def process_speech_input(
    call_id: str,
    audio_data: bytes,
    language: str = "en",
    db: AsyncSession = Depends(get_db),
):
    """
    Process speech input from call.

    Args:
        call_id: Call session identifier
        audio_data: Raw audio bytes
        language: Language code
        db: Database session

    Returns:
        Processing response
    """
    try:
        voice_service = VoiceService(db)
        conversation_service = ConversationService(db)

        # Process audio input
        transcription = await voice_service.process_audio_input(
            call_id, audio_data, language
        )

        if not transcription:
            return {"error": "Failed to transcribe audio"}

        # Process conversation
        response = await conversation_service.process_user_input(
            call_id, transcription, language
        )

        # Generate audio response
        audio_response = await voice_service.generate_audio_response(
            call_id, response["message"], language
        )

        return {
            "transcription": transcription,
            "response": response,
            "audio_url": response.get("audio_url"),
            "audio_data": audio_response,
            "actions": response.get("actions", [])
        }

    except Exception as e:
        logger.error("Failed to process speech", error=str(e), call_id=call_id)
        raise HTTPException(status_code=500, detail="Failed to process speech")


@router.post("/{call_id}/events")
async def handle_call_event(
    call_id: str,
    event_type: str,
    event_data: dict = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle call lifecycle events.

    Args:
        call_id: Call session identifier
        event_type: Type of event
        event_data: Event data
        db: Database session
    """
    try:
        voice_service = VoiceService(db)
        await voice_service.handle_call_event(call_id, event_type, event_data)

        return {"status": "event_processed"}

    except Exception as e:
        logger.error("Failed to handle call event", error=str(e), call_id=call_id)
        raise HTTPException(status_code=500, detail="Failed to handle event")


@router.get("/{call_id}", response_model=schemas.CallDetailResponse)
async def get_call_details(
    call_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get call details.

    Args:
        call_id: Call identifier
        db: Database session

    Returns:
        Call details
    """
    try:
        voice_service = VoiceService(db)

        # Get call record
        from sqlalchemy import select
        from app import models

        result = await db.execute(
            select(models.CallRecord).where(models.CallRecord.id == call_id)
        )
        call = result.scalar_one_or_none()

        if not call:
            raise HTTPException(status_code=404, detail="Call not found")

        # Get associated lead
        lead_result = await db.execute(
            select(models.Lead).where(models.Lead.lead_id == call.lead_id)
        )
        lead = lead_result.scalar_one_or_none()

        return schemas.CallDetailResponse(
            call_id=call.id,
            lead_id=call.lead_id,
            status=call.status,
            duration_seconds=call.duration_seconds,
            transcript=call.transcript,
            detected_language=call.detected_language,
            call_quality_score=call.call_quality_score,
            lead_name=lead.full_name if lead else None,
            lead_phone=lead.phone_number if lead else None,
            created_at=call.created_at,
            answered_at=call.answered_at,
            ended_at=call.ended_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get call details", error=str(e), call_id=call_id)
        raise HTTPException(status_code=500, detail="Failed to get call details")


@router.get("/lead/{lead_id}", response_model=List[schemas.CallDetailResponse])
async def get_lead_calls(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all calls for a lead.

    Args:
        lead_id: Lead identifier
        db: Database session

    Returns:
        List of call details
    """
    try:
        from sqlalchemy import select
        from app import models

        result = await db.execute(
            select(models.CallRecord).where(models.CallRecord.lead_id == lead_id)
        )
        calls = result.scalars().all()

        # Get lead info
        lead_result = await db.execute(
            select(models.Lead).where(models.Lead.lead_id == lead_id)
        )
        lead = lead_result.scalar_one_or_none()

        return [
            schemas.CallDetailResponse(
                call_id=call.id,
                lead_id=call.lead_id,
                status=call.status,
                duration_seconds=call.duration_seconds,
                transcript=call.transcript,
                detected_language=call.detected_language,
                call_quality_score=call.call_quality_score,
                lead_name=lead.full_name if lead else None,
                lead_phone=lead.phone_number if lead else None,
                created_at=call.created_at,
                answered_at=call.answered_at,
                ended_at=call.ended_at
            )
            for call in calls
        ]

    except Exception as e:
        logger.error("Failed to get lead calls", error=str(e), lead_id=lead_id)
        raise HTTPException(status_code=500, detail="Failed to get lead calls")