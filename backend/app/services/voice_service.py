"""
Voice service for call management and STT/TTS integration.
"""

from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app import models
from app.core.stt_tts.sarvam_client import SarvamClient
from app.core.telephony.twilio_client import TwilioClient
from app.services.conversation_service import ConversationService
from app.services.scoring_service import ScoringService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VoiceService:
    """
    Service for managing voice calls, STT, and TTS.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.sarvam_client = SarvamClient()
        self.twilio_client = TwilioClient()
        self.conversation_service = ConversationService(db)
        self.scoring_service = ScoringService(db)

    async def initiate_outbound_call(
        self,
        lead_id: str,
        call_id: str
    ) -> bool:
        """
        Initiate outbound call to lead.

        Args:
            lead_id: Lead identifier
            call_id: Call session identifier

        Returns:
            True if call initiated successfully
        """
        try:
            # Get lead information
            lead = await self._get_lead(lead_id)
            if not lead:
                logger.error("Lead not found for call", lead_id=lead_id)
                return False

            # Create call record
            call = models.CallRecord(
                id=call_id,
                lead_id=lead.lead_id,
                status="queued",
                direction="outbound",
                detected_language=lead.preferred_language or "en"
            )

            self.db.add(call)
            await self.db.commit()

            # Initiate Twilio call
            success, call_sid = await self.twilio_client.make_call(
                to_number=lead.phone_number,
                call_id=call_id,
                language=lead.preferred_language or "en"
            )

            if success:
                # Update call with Twilio SID
                call.twilio_call_sid = call_sid
                # Update call status
                call.status = "initiated"
                await self.db.commit()

                logger.info(
                    "Outbound call initiated",
                    lead_id=lead_id,
                    call_id=call_id,
                    twilio_sid=call_sid,
                    phone=lead.phone_number
                )
            else:
                call.status = "failed"
                await self.db.commit()
                logger.error("Failed to initiate call", lead_id=lead_id, call_id=call_id)

            return success

        except Exception as e:
            logger.error("Failed to initiate outbound call", error=str(e), lead_id=lead_id)
            return False

    async def process_audio_input(
        self,
        call_id: str,
        audio_data: bytes,
        language: str = "en"
    ) -> Optional[str]:
        """
        Process audio input through STT.

        Args:
            call_id: Call session identifier
            audio_data: Raw audio bytes
            language: Language code

        Returns:
            Transcribed text or None
        """
        try:
            # Transcribe audio using Sarvam
            transcription = await self.sarvam_client.speech_to_text(
                audio_data=audio_data,
                language=language
            )

            if transcription:
                # Update call record with transcription
                await self._update_call_transcript(call_id, transcription, language)

                logger.info(
                    "Audio processed",
                    call_id=call_id,
                    language=language,
                    text_length=len(transcription)
                )

            return transcription

        except Exception as e:
            logger.error("Failed to process audio input", error=str(e), call_id=call_id)
            return None

    async def generate_audio_response(
        self,
        call_id: str,
        text: str,
        language: str = "en"
    ) -> Optional[bytes]:
        """
        Generate audio response through TTS.

        Args:
            call_id: Call session identifier
            text: Text to convert to speech
            language: Language code

        Returns:
            Audio bytes or None
        """
        try:
            # Generate speech using Sarvam
            audio_data = await self.sarvam_client.text_to_speech(
                text=text,
                language=language
            )

            if audio_data:
                logger.info(
                    "Audio response generated",
                    call_id=call_id,
                    language=language,
                    text_length=len(text)
                )

            return audio_data

        except Exception as e:
            logger.error("Failed to generate audio response", error=str(e), call_id=call_id)
            return None

    async def handle_call_event(
        self,
        call_id: str,
        event_type: str,
        event_data: dict = None
    ):
        """
        Handle call lifecycle events.

        Args:
            call_id: Call session identifier
            event_type: Type of event (answered, completed, failed, etc.)
            event_data: Additional event data
        """
        try:
            # Get call record
            call = await self._get_call(call_id)
            if not call:
                logger.error("Call record not found", call_id=call_id)
                return

            # Update call status
            if event_type == "answered":
                call.status = "answered"
                call.answered_at = event_data.get("timestamp")
            elif event_type == "completed":
                call.status = "completed"
                call.ended_at = event_data.get("timestamp")
                call.duration_seconds = event_data.get("duration", 0)
                call.call_quality_score = event_data.get("quality_score")

                # Trigger final qualification
                await self._finalize_call(call)

            elif event_type == "failed":
                call.status = "failed"
                call.ended_at = event_data.get("timestamp")
            elif event_type == "no_answer":
                call.status = "no_answer"
                call.ended_at = event_data.get("timestamp")

            await self.db.commit()

            logger.info(
                "Call event handled",
                call_id=call_id,
                event_type=event_type,
                status=call.status
            )

        except Exception as e:
            logger.error("Failed to handle call event", error=str(e), call_id=call_id)

    async def detect_language(self, audio_data: bytes) -> str:
        """
        Detect language from audio sample.

        Args:
            audio_data: Audio bytes

        Returns:
            Detected language code
        """
        try:
            # Use Sarvam language detection
            detected_lang = await self.sarvam_client.detect_language(audio_data)

            # Fallback to English if detection fails
            return detected_lang or "en"

        except Exception as e:
            logger.error("Failed to detect language", error=str(e))
            return "en"

    async def _get_lead(self, lead_id: str) -> Optional[models.Lead]:
        """Get lead by ID."""
        from sqlalchemy import select
        result = await self.db.execute(
            select(models.Lead).where(models.Lead.lead_id == lead_id)
        )
        return result.scalar_one_or_none()

    async def _get_call(self, call_id: str) -> Optional[models.CallRecord]:
        """Get call by ID."""
        from sqlalchemy import select
        result = await self.db.execute(
            select(models.CallRecord).where(models.CallRecord.id == call_id)
        )
        return result.scalar_one_or_none()

    async def _update_call_transcript(
        self,
        call_id: str,
        transcription: str,
        language: str
    ):
        """Update call record with transcription."""
        call = await self._get_call(call_id)
        if call:
            call.transcript = (call.transcript or "") + transcription + " "
            call.detected_language = language
            await self.db.commit()

    async def _finalize_call(self, call: models.CallRecord):
        """
        Finalize call with qualification and routing.

        Args:
            call: Call record model
        """
        try:
            # Qualify the conversation
            qualification = await self.conversation_service.qualify_conversation(
                call.lead_id, call.session_id or call.id
            )

            # Update lead with final classification
            lead = await self._get_lead(call.lead_id)
            if lead and qualification:
                lead.classification = qualification.get("classification")
                lead.score = qualification.get("overall_score")
                lead.status = "qualified"
                await self.db.commit()

                # Trigger routing
                await self._route_qualified_lead(lead, qualification)

        except Exception as e:
            logger.error("Failed to finalize call", error=str(e), call_id=call.id)

    async def _route_qualified_lead(self, lead: models.Lead, qualification: dict):
        """
        Route qualified lead based on classification.

        Args:
            lead: Lead model
            qualification: Qualification results
        """
        classification = qualification.get("classification")

        if classification == "hot":
            # Handoff to RM
            await self._handoff_to_rm(lead)
        elif classification == "warm":
            # Send WhatsApp follow-up
            await self._send_whatsapp_followup(lead)
        # Cold leads are stored for future re-engagement

    async def _handoff_to_rm(self, lead: models.Lead):
        """Handoff hot lead to Relationship Manager."""
        # Implementation would integrate with RM system
        logger.info("Hot lead handed off to RM", lead_id=lead.lead_id)

    async def _send_whatsapp_followup(self, lead: models.Lead):
        """Send WhatsApp follow-up to warm lead."""
        from app.services.whatsapp_service import WhatsAppService
        whatsapp_service = WhatsAppService()
        await whatsapp_service.send_followup_message(
            lead.phone_number,
            lead.full_name,
            "Check out our loan options: https://rupeezy.com/apply"
        )
        logger.info("WhatsApp follow-up sent", lead_id=lead.lead_id)