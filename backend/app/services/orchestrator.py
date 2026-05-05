import logging

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session, sessionmaker

from app.models.call import CallRecord
from app.models.lead import Lead
from app.repositories.call_repository import CallRepository
from app.repositories.lead_repository import LeadRepository
from app.schemas.call import CallCompleteResponse, CallTurnRequest, CallTurnResponse, TurnArtifact
from app.schemas.lead import LeadCreate, LeadCreateResponse, LeadResponse
from app.services.conversation_engine import ConversationEngine
from app.services.handoff import HumanHandoffService
from app.services.memory.chroma_memory import ChromaMemoryService
from app.services.messaging.whatsapp import WhatsAppService
from app.services.scoring import LeadScoringService
from app.services.telephony.base import BaseCallProvider
from app.utils.time import utcnow

logger = logging.getLogger(__name__)


class RiseAgentOrchestrator:
    def __init__(
        self,
        *,
        settings,
        session_factory: sessionmaker,
        lead_repository: LeadRepository,
        call_repository: CallRepository,
        call_provider: BaseCallProvider,
        conversation_engine: ConversationEngine,
        memory_service: ChromaMemoryService,
        scoring_service: LeadScoringService,
        whatsapp_service: WhatsAppService,
        handoff_service: HumanHandoffService,
    ) -> None:
        self.settings = settings
        self.session_factory = session_factory
        self.leads = lead_repository
        self.calls = call_repository
        self.call_provider = call_provider
        self.conversation_engine = conversation_engine
        self.memory_service = memory_service
        self.scoring_service = scoring_service
        self.whatsapp_service = whatsapp_service
        self.handoff_service = handoff_service

    def register_lead(self, db: Session, payload: LeadCreate, background_tasks: BackgroundTasks) -> LeadCreateResponse:
        if self.leads.get(db, payload.lead_id):
            raise HTTPException(status_code=409, detail=f"Lead {payload.lead_id} already exists.")

        lead = self.leads.create(db, payload)
        call = self.calls.create(db, lead_id=lead.lead_id, status="queued")
        background_tasks.add_task(self.start_outbound_call, lead.lead_id, call.id)
        return LeadCreateResponse(
            lead=LeadResponse.model_validate(lead),
            call_id=call.id,
            message="Lead created and outbound call queued.",
        )

    def start_outbound_call(self, lead_id: str, call_id: str) -> None:
        with self.session_factory() as db:
            lead = self.leads.get(db, lead_id)
            call = self.calls.get(db, call_id)
            if not lead or not call:
                logger.warning("Unable to start outbound call for lead=%s call=%s", lead_id, call_id)
                return

            try:
                provider_response = self.call_provider.initiate_outbound_call(
                    lead_id=lead.lead_id,
                    call_id=call.id,
                    phone_number=lead.phone_number,
                )
                call.provider_call_id = provider_response.provider_call_id
                call.status = provider_response.status
                call.started_at = call.started_at or utcnow()
                lead.status = "dialing"
                lead.last_contacted_at = utcnow()
                self.calls.update(db, call)
                self.leads.update(db, lead)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Outbound call initiation failed for call=%s: %s", call_id, exc)
                call.status = "failed"
                self.calls.update(db, call)

    def process_turn(self, db: Session, call_id: str, payload: CallTurnRequest) -> CallTurnResponse:
        call = self._require_call(db, call_id)
        lead = self._require_lead(db, call.lead_id)

        call.status = "in_progress"
        call.started_at = call.started_at or utcnow()
        artifact_data = self.conversation_engine.generate_reply(lead=lead, call=call, user_text=payload.user_text)
        artifact = TurnArtifact(**artifact_data)

        call.detected_language = artifact.detected_language
        call.tone = payload.tone or call.tone
        call.duration_seconds += payload.duration_seconds
        call.updated_at = utcnow()
        lead.preferred_language = artifact.detected_language
        lead.status = "engaged"
        lead.last_contacted_at = utcnow()

        self.calls.append_transcript(db, call, "customer", payload.user_text)
        self.calls.append_transcript(db, call, "assistant", artifact.assistant_text)
        self.leads.update(db, lead)

        return CallTurnResponse(call_id=call.id, status=call.status, artifact=artifact)

    def finalize_call(self, db: Session, call_id: str) -> CallCompleteResponse:
        call = self._require_call(db, call_id)
        lead = self._require_lead(db, call.lead_id)

        result = self.scoring_service.score(
            transcript=call.transcript,
            duration_seconds=call.duration_seconds,
            tone=call.tone,
        )

        call.classification = result.classification
        call.next_action = result.next_action
        call.summary = result.summary
        call.intent = result.intent
        call.objections = result.objections
        call.score_breakdown = result.breakdown
        call.status = "completed"
        call.ended_at = utcnow()

        lead.classification = result.classification
        lead.score = result.total_score
        lead.status = "completed"

        try:
            if result.classification == "HOT":
                lead.assigned_rm = self.handoff_service.assign_rm(lead, call)
                self.handoff_service.notify(lead, call)
            elif result.classification == "WARM":
                self.whatsapp_service.send_warm_followup(lead, result.summary)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Post-call routing failed for lead=%s: %s", lead.lead_id, exc)

        self.memory_service.store_summary(lead_id=lead.lead_id, call_id=call.id, summary=result.summary)
        self.calls.update(db, call)
        self.leads.update(db, lead)

        return CallCompleteResponse(
            call_id=call.id,
            status=call.status,
            classification=result.classification,
            next_action=result.next_action,
            score_breakdown=result.breakdown,
            summary=result.summary,
        )

    def sync_provider_status(self, db: Session, provider_call_id: str, status: str) -> None:
        call = self.calls.get_by_provider_call_id(db, provider_call_id)
        if not call:
            logger.warning("Provider callback received for unknown call sid=%s", provider_call_id)
            return

        call.status = status
        if status == "completed":
            call.ended_at = call.ended_at or utcnow()
        self.calls.update(db, call)

    def _require_call(self, db: Session, call_id: str) -> CallRecord:
        call = self.calls.get(db, call_id)
        if not call:
            raise HTTPException(status_code=404, detail=f"Call {call_id} not found.")
        return call

    def _require_lead(self, db: Session, lead_id: str) -> Lead:
        lead = self.leads.get(db, lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found.")
        return lead
