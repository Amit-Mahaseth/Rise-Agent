import asyncio
import contextlib
import logging
import random
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy.orm import Session, sessionmaker

from app.core.websocket_manager import ws_manager
from app.models.call import CallRecord
from app.repositories.call_repository import CallRepository
from app.repositories.lead_repository import LeadRepository
from app.services.llm_service import LLMService
from app.services.persona import get_persona_pack
from app.services.memory_service import MemoryService
from app.services.scoring_service_v2 import ScoringServiceV2
from app.services.stt_service import STTService
from app.services.telephony.base import BaseCallProvider
from app.services.tts_service import TTSService
from app.services.whatsapp_service_v2 import WhatsAppTemplateService

logger = logging.getLogger(__name__)


@dataclass
class CallSessionContext:
    call_id: str
    lead_id: str
    provider_call_sid: str | None = None
    state: str = "LISTENING"
    call_active: bool = True
    interrupt_flag: bool = False
    # Conversation intelligence
    strategy_stage: str = "opening"
    persona: str = "professional"
    turn_index: int = 0
    last_intent: str | None = None
    opening_sent: bool = False
    silence_ms: int = 0
    silence_retries: int = 0
    partial_confidence: float = 0.0
    rolling_audio_energy: float = 0.0
    silence_mode: str = "thinking_pause"
    user_chars_seen: int = 0
    user_speech_rate_cps: float = 10.0
    tts_speed: float = 1.0
    language_profile: str = "default"
    micro_response_count: int = 0
    last_agent_message: str = ""
    hangup_timing_ms: int = 0
    ab_opening_variant: str = "A"
    ab_objection_variant: str = "A"
    prepared_candidates: dict[str, list[str]] = field(default_factory=dict)
    early_prediction_enqueued_for_turn: int = 0
    turn_buffer: list[str] = field(default_factory=list)
    transcript_lines: list[str] = field(default_factory=list)
    detected_messages: int = 0
    start_time: float = field(default_factory=time.monotonic)
    current_tts_task: asyncio.Task | None = None
    input_audio_queue: asyncio.Queue[bytes] = field(default_factory=asyncio.Queue)
    transcript_queue: asyncio.Queue[dict] = field(default_factory=asyncio.Queue)
    response_queue: asyncio.Queue[dict] = field(default_factory=asyncio.Queue)
    audio_output_queue: asyncio.Queue[bytes] = field(default_factory=asyncio.Queue)
    metrics: dict[str, list[float]] = field(
        default_factory=lambda: {"stt_ms": [], "llm_ms": [], "tts_ms": [], "roundtrip_ms": []}
    )


class RealtimeCallService:
    def __init__(
        self,
        *,
        session_factory: sessionmaker,
        call_repository: CallRepository,
        lead_repository: LeadRepository,
        call_provider: BaseCallProvider,
        agent_persona: str,
        enable_tuning_debug: bool,
        stt_service: STTService,
        tts_service: TTSService,
        llm_service: LLMService,
        memory_service: MemoryService,
        scoring_service: ScoringServiceV2,
        whatsapp_service: WhatsAppTemplateService,
        handoff_service: object | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.calls = call_repository
        self.leads = lead_repository
        self.call_provider = call_provider
        self.stt = stt_service
        self.tts = tts_service
        self.llm = llm_service
        self.memory = memory_service
        self.scoring = scoring_service
        self.whatsapp = whatsapp_service
        self.agent_persona = agent_persona
        self.enable_tuning_debug = enable_tuning_debug
        self.handoff_service = handoff_service

        self._audio_queues: dict[str, asyncio.Queue[bytes]] = defaultdict(asyncio.Queue)  # Backward compatibility.
        self._active_sessions: dict[str, bool] = {}
        self._sessions: dict[str, CallSessionContext] = {}
        self._sid_to_call_id: dict[str, str] = {}
        self._session_tasks: dict[str, asyncio.Task] = {}

        # Safety controls.
        self._max_call_duration_seconds = 600
        self._max_silence_retries = 3
        self._silence_turn_trigger_ms = 1000
        self._min_silence_ms = 800
        self._max_silence_ms = 1200
        self._min_final_confidence = 0.62

        # Latency and resilience controls.
        self._stt_timeout_seconds = 2.0
        self._llm_timeout_seconds = 2.0
        self._tts_timeout_seconds = 2.0
        self._service_retries = 2
        self._llm_latency_mask_threshold_seconds = 1.2
        self._early_turn_prediction_ms = 260
        self._energy_threshold_mult = 0.55

        self._language_profiles = {
            "english": {"silence_ms": 900, "confidence_min": 0.62, "micro_freq": 0.22, "energy_mult": 0.55},
            "hindi": {"silence_ms": 1000, "confidence_min": 0.60, "micro_freq": 0.34, "energy_mult": 0.58},
            "hinglish": {"silence_ms": 950, "confidence_min": 0.60, "micro_freq": 0.42, "energy_mult": 0.57},
            "tamil": {"silence_ms": 1050, "confidence_min": 0.58, "micro_freq": 0.30, "energy_mult": 0.60},
            "telugu": {"silence_ms": 1050, "confidence_min": 0.58, "micro_freq": 0.30, "energy_mult": 0.60},
            "default": {"silence_ms": 1000, "confidence_min": 0.62, "micro_freq": 0.28, "energy_mult": 0.55},
        }

    async def initiate_call(self, lead_id: str, phone_number: str) -> dict:
        with self.session_factory() as db:
            call = self.calls.create(db, lead_id=lead_id, status="queued")
            provider_result = self.call_provider.initiate_outbound_call(
                lead_id=lead_id,
                call_id=call.id,
                phone_number=phone_number,
            )
            call.provider_call_id = provider_result.provider_call_id
            call.status = provider_result.status
            call.started_at = datetime.utcnow()
            self.calls.update(db, call)
            self._active_sessions[call.id] = True
            self._sessions[call.id] = CallSessionContext(
                call_id=call.id,
                lead_id=lead_id,
                provider_call_sid=provider_result.provider_call_id,
                persona=self.agent_persona,
            )
            if provider_result.provider_call_id:
                self._sid_to_call_id[provider_result.provider_call_id] = call.id

        await ws_manager.emit("dashboard", "call_started", {"call_id": call.id, "lead_id": lead_id, "status": call.status})
        return {"call_id": call.id, "provider_status": provider_result.status, "provider_call_id": provider_result.provider_call_id}

    async def initialize_media_stream(self, call_sid: str) -> dict:
        call_id = self._resolve_call_id(call_sid)
        if not call_id:
            return {"status": "unknown_call_sid", "call_sid": call_sid}
        session = self._sessions.get(call_id)
        if not session:
            with self.session_factory() as db:
                call = self.calls.get(db, call_id)
                if not call:
                    return {"status": "unknown_call", "call_sid": call_sid}
                session = CallSessionContext(call_id=call_id, lead_id=call.lead_id, provider_call_sid=call_sid)
                self._sessions[call_id] = session
        session.provider_call_sid = call_sid
        self._sid_to_call_id[call_sid] = call_id
        await self.ensure_session_runner(call_id)
        # First 5-second optimization: speak an opening immediately.
        if not session.opening_sent:
            with self.session_factory() as db:
                lead = self.leads.get(db, session.lead_id)
                if lead:
                    session.persona = session.persona or self.agent_persona
                    language = lead.preferred_language or lead.language or "English"
                    persona_pack = get_persona_pack(session.persona)
                    greeting = (
                        persona_pack.greeting_overrides.get(language)
                        or persona_pack.greeting_overrides.get("English")
                    )

                    first_name = (lead.full_name or "").split(" ")[0] or "there"
                    opening = greeting.format(name=first_name) if "{name}" in greeting else greeting
                    if random.random() < 0.5:
                        session.ab_opening_variant = "A"
                        opening = (
                            f"{opening}-what loan amount are you considering?"
                            if language != "English"
                            else f"{opening}-to guide you, what loan amount are you considering?"
                        )
                    else:
                        session.ab_opening_variant = "B"
                        opening = (
                            f"{opening}-should we check eligibility first?"
                            if language != "English"
                            else f"{opening}-would you like to start with eligibility or EMI estimate?"
                        )

                    session.opening_sent = True
                    session.strategy_stage = "opening"
                    await session.response_queue.put(
                        {
                            "user_text": "__opening__",
                            "response_text": opening,
                            "language": language,
                            "started_at": time.perf_counter(),
                            "is_opening": True,
                            "turn_index": session.turn_index,
                        }
                    )
                    await ws_manager.emit(
                        "dashboard",
                        "transcript_update",
                        {"call_id": call_id, "text": opening, "phase": "assistant"},
                    )

        return {"status": "initialized", "call_id": call_id, "call_sid": call_sid}

    async def ensure_session_runner(self, call_id: str) -> None:
        existing = self._session_tasks.get(call_id)
        if existing and not existing.done():
            return
        with self.session_factory() as db:
            call = self.calls.get(db, call_id)
            if not call:
                return
            self._session_tasks[call_id] = asyncio.create_task(self.handle_call_session(call.id, call.lead_id))

    async def enqueue_audio_chunk(self, call_sid: str, audio_chunk: bytes) -> None:
        call_id = self._resolve_call_id(call_sid)
        if not call_id:
            return
        session = self._sessions.get(call_id)
        if not session:
            with self.session_factory() as db:
                call = self.calls.get(db, call_id)
                if not call:
                    return
                session = CallSessionContext(call_id=call.id, lead_id=call.lead_id, provider_call_sid=call_sid)
                self._sessions[call_id] = session

        # Interruption: user speaks while TTS is active -> cancel immediately.
        if session.state in {"SPEAKING", "PERSISTING"}:
            session.interrupt_flag = True
            await self._cancel_tts_and_flush_output(session)
            session.state = "LISTENING"
            await ws_manager.emit("dashboard", "transcript_update", {"call_id": call_id, "phase": "interrupt", "text": "[user interrupted assistant]"})
        await session.input_audio_queue.put(audio_chunk)
        await self._audio_queues[call_id].put(audio_chunk)

    async def end_session(self, call_id: str) -> None:
        call_id = self._resolve_call_id(call_id) or call_id
        self._active_sessions[call_id] = False
        session = self._sessions.get(call_id)
        if session:
            session.call_active = False
            session.hangup_timing_ms = int((time.monotonic() - session.start_time) * 1000.0)
            await session.input_audio_queue.put(b"")
            await session.transcript_queue.put({"type": "shutdown"})
            await session.response_queue.put({"type": "shutdown"})
            await session.audio_output_queue.put(b"")
        await self._audio_queues[call_id].put(b"")  # Backward compatibility.

    async def handle_call_session(self, call_id: str, lead_id: str) -> dict:
        with self.session_factory() as db:
            call = self.calls.get(db, call_id)
            lead = self.leads.get(db, lead_id)
            if not call or not lead:
                return {"status": "not_found"}
            call.status = "in_progress"
            self.calls.update(db, call)
        session = self._sessions.get(call_id) or CallSessionContext(call_id=call_id, lead_id=lead_id, provider_call_sid=call.provider_call_id)
        self._sessions[call_id] = session
        self._active_sessions[call_id] = True
        self._apply_language_tuning(session, call.detected_language or lead.preferred_language or "default")

        workers = [
            asyncio.create_task(self._stt_worker(session)),
            asyncio.create_task(self._llm_worker(session)),
            asyncio.create_task(self._tts_worker(session)),
            asyncio.create_task(self._audio_sender_worker(session)),
        ]

        try:
            while self._active_sessions.get(call_id, True) and session.call_active:
                if time.monotonic() - session.start_time > self._max_call_duration_seconds:
                    await ws_manager.emit(
                        "dashboard",
                        "transcript_update",
                        {"call_id": call_id, "phase": "system", "text": "Maximum call duration reached. Ending call gracefully."},
                    )
                    break
                await asyncio.sleep(0.1)
        finally:
            session.call_active = False
            for task in workers:
                task.cancel()
            await asyncio.gather(*workers, return_exceptions=True)

        duration = int(time.monotonic() - session.start_time)
        transcript = "\n".join(session.transcript_lines)
        scoring = await self.scoring.score_lead(transcript=transcript, duration_seconds=duration)
        await self._route_lead(lead_id=lead_id, call_id=call_id, scoring=scoring, transcript=transcript)

        # Memory compression after call ends: store only key insights.
        with self.session_factory() as db:
            call = self.calls.get(db, call_id)
            detected_language = call.detected_language if call else None
        await self.memory.compress_and_store_after_call(
            lead_id=lead_id,
            call_id=call_id,
            scoring=scoring,
            detected_language=detected_language,
        )

        with self.session_factory() as db:
            call = self.calls.get(db, call_id)
            lead = self.leads.get(db, lead_id)
            if call and lead:
                call.status = "completed"
                call.ended_at = datetime.utcnow()
                call.duration_seconds = max(call.duration_seconds, duration)
                call.classification = scoring["category"]
                call.overall_score = float(scoring["score"])
                call.summary = scoring["summary"]
                call.intent = scoring.get("intent")
                call.objections = scoring.get("objections") or []
                call.next_action = scoring.get("next_action")
                call.score_breakdown = {
                    **(scoring.get("breakdown") or {}),
                    "engagement_level": scoring.get("engagement_level"),
                    "objection_count": scoring.get("objection_count"),
                    "conversion_probability": scoring.get("conversion_probability"),
                    "hangup_timing_ms": session.hangup_timing_ms,
                    "last_agent_message": session.last_agent_message[:220],
                    "last_objection_type": (scoring.get("objections") or [None])[0],
                    "ab_opening_variant": session.ab_opening_variant,
                    "ab_objection_variant": session.ab_objection_variant,
                    "micro_response_count": session.micro_response_count,
                }
                lead.classification = scoring["category"]
                lead.score = float(scoring["score"])
                # Keep route-specific follow-up status set by _route_lead.
                if lead.status not in {"assigned", "followup_sent", "nurture_scheduled"}:
                    lead.status = "completed"
                self.calls.update(db, call)
                self.leads.update(db, lead)

        await ws_manager.emit("dashboard", "lead_scored", {"lead_id": lead_id, **scoring})
        await ws_manager.emit("dashboard", "call_ended", {"call_id": call_id, "lead_id": lead_id, "duration": duration})
        self._active_sessions[call_id] = False
        logger.info(
            "call.metrics",
            extra={
                "call_id": call_id,
                "stt_ms_avg": self._avg(session.metrics["stt_ms"]),
                "llm_ms_avg": self._avg(session.metrics["llm_ms"]),
                "tts_ms_avg": self._avg(session.metrics["tts_ms"]),
                "roundtrip_ms_avg": self._avg(session.metrics["roundtrip_ms"]),
                "ab_opening_variant": session.ab_opening_variant,
                "micro_response_count": session.micro_response_count,
            },
        )
        if scoring.get("category") == "HOT":
            logger.info("optimization.best_response", extra={"call_id": call_id, "message": session.last_agent_message[:180]})
        if scoring.get("category") == "COLD":
            logger.info("optimization.failed_interaction", extra={"call_id": call_id, "last_intent": session.last_intent})
        return {"status": "completed", "score": scoring}

    async def _route_lead(self, lead_id: str, call_id: str, scoring: dict, transcript: str) -> None:
        category = scoring["category"]
        with self.session_factory() as db:
            lead = self.leads.get(db, lead_id)
            call = self.calls.get(db, call_id)

            phone_number = lead.phone_number if lead else ""
            customer_name = lead.full_name if lead else lead_id
            language = (call.detected_language if call else None) or (lead.preferred_language if lead else None) or "English"

            if category == "HOT" and self.handoff_service and lead and call:
                rm_name = self.handoff_service.assign_rm(lead, call)
                lead.assigned_rm = rm_name
                lead.status = "assigned"
                self.leads.update(db, lead)
                self.handoff_service.notify(lead, call)

                await ws_manager.emit(
                    "dashboard",
                    "lead_routed",
                    {"lead_id": lead_id, "route": "rm_queue", "rm_name": rm_name},
                )
                return

            if category == "WARM" and lead:
                objections = scoring.get("objections") or []
                intent = scoring.get("intent")
                await self.whatsapp.send_warm_personalized_followup(
                    phone=phone_number,
                    customer_name=customer_name,
                    summary=scoring.get("summary"),
                    objections=objections,
                    intent=intent,
                    language=language,
                )
                lead.status = "followup_sent"
                self.leads.update(db, lead)

                await ws_manager.emit(
                    "dashboard",
                    "lead_routed",
                    {"lead_id": lead_id, "route": "whatsapp", "intent": intent},
                )
                return

            if category == "COLD" and lead:
                # Adaptive follow-up: delayed retry schedule.
                next_retry_at = (datetime.utcnow() + timedelta(days=30)).isoformat()
                lead.status = "nurture_scheduled"
                lead.extra_metadata = {**(lead.extra_metadata or {}), "next_retry_at": next_retry_at}
                self.leads.update(db, lead)

                await ws_manager.emit(
                    "dashboard",
                    "lead_routed",
                    {"lead_id": lead_id, "route": "nurture_30_days", "next_retry_at": next_retry_at},
                )
                return

        # Fallback emit for any unknown combination.
        await ws_manager.emit(
            "dashboard",
            "lead_routed",
            {"lead_id": lead_id, "route": category.lower(), "summary": scoring.get("summary"), "transcript": transcript},
        )

    async def _stt_worker(self, session: CallSessionContext) -> None:
        while session.call_active:
            audio = await session.input_audio_queue.get()
            if not audio:
                break

            audio_energy = self._estimate_audio_energy(audio)
            session.rolling_audio_energy = (session.rolling_audio_energy * 0.7) + (audio_energy * 0.3)

            if self._is_silence(audio, session.rolling_audio_energy):
                session.silence_ms += 200
                session.silence_mode = self._classify_silence(session)

                if (
                    session.silence_ms >= self._early_turn_prediction_ms
                    and session.turn_buffer
                    and session.partial_confidence >= max(self._min_final_confidence, 0.68)
                    and session.early_prediction_enqueued_for_turn != session.turn_index
                ):
                    predicted_text = " ".join(session.turn_buffer).strip()
                    if predicted_text:
                        session.early_prediction_enqueued_for_turn = session.turn_index
                        await session.transcript_queue.put(
                            {
                                "type": "predictive",
                                "text": predicted_text,
                                "started_at": time.perf_counter(),
                                "turn_index": session.turn_index,
                            }
                        )

                # Micro-response layer for short thinking pauses.
                if (
                    self._min_silence_ms <= session.silence_ms <= self._max_silence_ms
                    and session.silence_mode == "thinking_pause"
                    and session.state == "LISTENING"
                    and session.turn_buffer
                ):
                    micro = self._micro_response(session)
                    persona_pack = get_persona_pack(session.persona)
                    micro_freq = self._language_profiles.get(session.language_profile, self._language_profiles["default"])["micro_freq"]
                    micro_freq = min(0.8, micro_freq * (1.0 + persona_pack.filler_frequency))
                    if micro and random.random() <= micro_freq:
                        session.micro_response_count += 1
                        await session.response_queue.put(
                            {
                                "user_text": "__micro__",
                                "response_text": micro,
                                "language": "English",
                                "started_at": time.perf_counter(),
                                "is_opening": False,
                                "is_micro": True,
                                "turn_index": session.turn_index,
                            }
                        )

                # Hybrid turn detection: silence window + transcript confidence.
                if (
                    session.silence_ms >= self._silence_turn_trigger_ms
                    and session.turn_buffer
                    and session.partial_confidence >= self._min_final_confidence
                ):
                    utterance = " ".join(session.turn_buffer).strip()
                    session.turn_buffer.clear()
                    session.silence_ms = 0
                    session.turn_index += 1
                    session.detected_messages += 1
                    await session.transcript_queue.put(
                        {
                            "type": "final",
                            "text": utterance,
                            "started_at": time.perf_counter(),
                            "turn_index": session.turn_index,
                            "confidence": session.partial_confidence,
                            "silence_mode": session.silence_mode,
                        }
                    )
                    session.partial_confidence = 0.0
                elif session.silence_ms > self._max_silence_ms and not session.turn_buffer:
                    # Silence handling when no clear content arrived.
                    await self._handle_dynamic_silence(session)
                continue

            session.silence_ms = 0
            stt_start = time.perf_counter()
            stt_events = await self._with_retries(
                lambda: self._collect_stt_events(audio), timeout=self._stt_timeout_seconds, fallback=[{"type": "partial", "text": "..."}]
            )
            for stt_event in stt_events:
                text = stt_event.get("text", "").strip()
                if not text:
                    continue
                if stt_event["type"] == "partial":
                    # True streaming: keep emitting partial transcripts.
                    session.partial_confidence = max(session.partial_confidence, float(stt_event.get("confidence", 0.4)))
                    await ws_manager.emit(
                        "dashboard", "transcript_update", {"call_id": session.call_id, "text": text, "phase": "partial"}
                    )
                else:
                    session.partial_confidence = max(session.partial_confidence, float(stt_event.get("confidence", 0.5)))
                    session.turn_buffer.append(text)
                    session.user_chars_seen += len(text)
                    # Approximate user speech rate in chars/sec.
                    elapsed = max(1e-3, time.monotonic() - session.start_time)
                    session.user_speech_rate_cps = session.user_chars_seen / elapsed
                    await ws_manager.emit(
                        "dashboard", "transcript_update", {"call_id": session.call_id, "text": text, "phase": "final"}
                    )
            session.metrics["stt_ms"].append((time.perf_counter() - stt_start) * 1000.0)

    async def _llm_worker(self, session: CallSessionContext) -> None:
        while session.call_active:
            item = await session.transcript_queue.get()
            if item.get("type") == "shutdown":
                break
            if item.get("type") == "predictive":
                user_text = item.get("text", "").strip()
                if user_text:
                    await self._prepare_candidates(session, user_text)
                continue
            user_text = item.get("text", "").strip()
            if not user_text:
                continue

            # Ensure we're generating for the correct user turn (important after interrupts).
            session.turn_index = int(item.get("turn_index") or session.turn_index)

            # Race-condition guard: wait until persistence finishes so call.transcript is consistent.
            while session.state != "LISTENING" and session.call_active:
                await asyncio.sleep(0.02)

            llm_start = time.perf_counter()

            # Latency masking: send short filler while LLM is being prepared.
            prepared = self._select_prepared_candidates(session, user_text)
            if prepared:
                response_payload = {
                    "text": prepared[0],
                    "detected_language": "English",
                    "intent": session.last_intent,
                    "strategy_stage": session.strategy_stage,
                    "emotion": "neutral",
                }
                session.metrics["llm_ms"].append((time.perf_counter() - llm_start) * 1000.0)
                await session.response_queue.put(
                    {
                        "user_text": user_text,
                        "response_text": response_payload["text"],
                        "language": response_payload.get("detected_language", "English"),
                        "started_at": item.get("started_at", llm_start),
                        "turn_index": session.turn_index,
                        "intent": response_payload.get("intent"),
                        "strategy_stage": session.strategy_stage,
                        "emotion": response_payload.get("emotion", "neutral"),
                    }
                )
                continue

            llm_task = asyncio.create_task(
                self._with_retries(
                    lambda: self._generate_llm_response(session, user_text),
                    timeout=self._llm_timeout_seconds,
                    fallback={"text": "Please give me a second while I process that.", "detected_language": "English"},
                )
            )
            try:
                response_payload = await asyncio.wait_for(llm_task, timeout=self._llm_latency_mask_threshold_seconds)
            except asyncio.TimeoutError:
                filler = self._filler_response(session)
                await session.response_queue.put(
                    {
                        "user_text": "__filler__",
                        "response_text": filler,
                        "language": "English",
                        "started_at": item.get("started_at", llm_start),
                        "turn_index": session.turn_index,
                        "is_micro": True,
                    }
                )
                response_payload = await llm_task

            session.strategy_stage = str(response_payload.get("strategy_stage") or session.strategy_stage)
            session.last_intent = response_payload.get("intent")
            session.metrics["llm_ms"].append((time.perf_counter() - llm_start) * 1000.0)
            await self._emit_tuning_debug(
                session,
                phase="intent_classified",
                emotion=response_payload.get("emotion", "neutral"),
                llm_ms=session.metrics["llm_ms"][-1] if session.metrics["llm_ms"] else 0.0,
            )
            await session.response_queue.put(
                {
                    "user_text": user_text,
                    "response_text": response_payload["text"],
                    "language": response_payload.get("detected_language", "English"),
                    "started_at": item.get("started_at", llm_start),
                    "turn_index": session.turn_index,
                    "intent": response_payload.get("intent"),
                    "strategy_stage": session.strategy_stage,
                    "emotion": response_payload.get("emotion", "neutral"),
                }
            )
            await self._emit_tuning_debug(
                session,
                phase="llm_generated",
                emotion=response_payload.get("emotion", "neutral"),
                llm_ms=session.metrics["llm_ms"][-1] if session.metrics["llm_ms"] else 0.0,
            )

    async def _tts_worker(self, session: CallSessionContext) -> None:
        while session.call_active:
            item = await session.response_queue.get()
            if item.get("type") == "shutdown":
                break

            user_text = item["user_text"]
            response_text = item["response_text"]
            language = item["language"]
            is_opening = bool(item.get("is_opening"))
            is_micro = bool(item.get("is_micro"))
            emotion = item.get("emotion", "neutral")
            session.state = "SPEAKING"
            session.interrupt_flag = False
            tts_start = time.perf_counter()

            shaped_text = self._shape_for_speech(response_text, stage=session.strategy_stage, is_micro=is_micro)
            chunks = self._chunk_response(shaped_text)
            session.tts_speed = self._adaptive_tts_speed(session, emotion=emotion)
            persona_pack = get_persona_pack(session.persona)
            await self._emit_tuning_debug(
                session,
                phase="tts_selected",
                emotion=emotion,
                tts_ms=session.metrics["tts_ms"][-1] if session.metrics["tts_ms"] else 0.0,
            )
            await asyncio.sleep(max(0.0, persona_pack.response_delay_ms / 1000.0))

            async def _run_stream() -> None:
                for spoken_chunk in chunks:
                    async for chunk in self.tts.text_to_speech_stream(spoken_chunk, language, speed=session.tts_speed):
                        if session.interrupt_flag or not session.call_active:
                            break
                        cleaned_chunk = self._cleanup_audio_chunk(chunk)
                        if cleaned_chunk:
                            await session.audio_output_queue.put(cleaned_chunk)
                    # Natural break between idea chunks.
                    if not session.interrupt_flag:
                        await session.audio_output_queue.put(b"[pause:120ms]")

            session.current_tts_task = asyncio.create_task(_run_stream())
            interrupted = False
            try:
                await asyncio.wait_for(session.current_tts_task, timeout=self._tts_timeout_seconds)
            except asyncio.TimeoutError:
                await session.audio_output_queue.put(b"filler:One moment please.")
            except asyncio.CancelledError:
                interrupted = True
            finally:
                session.current_tts_task = None
                session.state = "PERSISTING"

            session.metrics["tts_ms"].append((time.perf_counter() - tts_start) * 1000.0)
            session.metrics["roundtrip_ms"].append((time.perf_counter() - item["started_at"]) * 1000.0)
            # If we were interrupted mid-TTS, skip persistence + memory updates for context reconciliation.
            if not interrupted and not session.interrupt_flag and not is_opening and not is_micro:
                await self._persist_turn(session, user_text=user_text, response_text=response_text, language=language)
            elif is_opening and not interrupted and not session.interrupt_flag and not is_micro:
                # Opening line: persist as assistant-only for call transcript continuity.
                await self._persist_turn(
                    session, user_text=user_text, response_text=response_text, language=language, is_opening=True
                )
            else:
                # Clear interrupt flag after discarding.
                session.interrupt_flag = False

            # Only after persistence (or intentional discard) do we accept new user turns.
            session.state = "LISTENING"
            session.last_agent_message = response_text

    async def _audio_sender_worker(self, session: CallSessionContext) -> None:
        while session.call_active:
            chunk = await session.audio_output_queue.get()
            if not chunk:
                break
            await ws_manager.emit(
                "dashboard",
                "transcript_update",
                {"call_id": session.call_id, "phase": "assistant_audio", "audio_chunk_size": len(chunk)},
            )

    async def _persist_turn(
        self,
        session: CallSessionContext,
        *,
        user_text: str,
        response_text: str,
        language: str,
        is_opening: bool = False,
    ) -> None:
        with self.session_factory() as db:
            call = self.calls.get(db, session.call_id)
            lead = self.leads.get(db, session.lead_id)
            if not call or not lead:
                return
            lead.preferred_language = language
            lead.language = language
            call.detected_language = language
            self._apply_language_tuning(session, language)

            # Opening line is assistant-only; no customer utterance to persist.
            if not is_opening and user_text and user_text != "__opening__":
                session.transcript_lines.append(f"customer: {user_text}")
            session.transcript_lines.append(f"assistant: {response_text}")
            call.transcript = "\n".join(session.transcript_lines)
            self.calls.update(db, call)
            self.leads.update(db, lead)

        # Only store to memory for completed user turns (helps interruption reconciliation).
        if not is_opening and user_text and user_text != "__opening__":
            await self.memory.update_memory(
                session.lead_id,
                {"call_id": session.call_id, "customer_text": user_text, "assistant_text": response_text, "language": language},
            )

    async def _generate_llm_response(self, session: CallSessionContext, user_text: str) -> dict:
        with self.session_factory() as db:
            call = self.calls.get(db, session.call_id)
            lead = self.leads.get(db, session.lead_id)
            if not call or not lead:
                return {"text": "I lost context for this call. Please repeat that.", "detected_language": "English"}
            lead_context = self.llm.build_lead_context(lead, call)
            # Important: for realtime interruption safety we disable "store turns" during generation.
            # We persist only after the TTS successfully completes.
            return await self.llm.generate_response(
                user_text,
                {
                    **lead_context,
                    "strategy_stage": session.strategy_stage,
                    "persona": session.persona,
                    "turn_index": session.turn_index,
                    "store_to_memory": False,
                },
            )

    async def _collect_stt_events(self, audio: bytes) -> list[dict]:
        events: list[dict] = []
        async for item in self.stt.stream_audio_to_text(audio):
            events.append(item)
        return events

    async def _with_retries(self, func, *, timeout: float, fallback):
        last_error: Exception | None = None
        for _ in range(self._service_retries + 1):
            try:
                return await asyncio.wait_for(func(), timeout=timeout)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        logger.warning("service.retry_exhausted", exc_info=last_error)
        return fallback

    async def _cancel_tts_and_flush_output(self, session: CallSessionContext) -> None:
        if session.current_tts_task and not session.current_tts_task.done():
            session.current_tts_task.cancel()
            with contextlib.suppress(Exception):
                await session.current_tts_task
        while not session.audio_output_queue.empty():
            with contextlib.suppress(asyncio.QueueEmpty):
                session.audio_output_queue.get_nowait()

        # Post-interrupt reconciliation:
        # - Discard unfinished assistant response
        # - Drop any queued LLM outputs that belong to the unfinished turn
        # - Keep only the new user intent (which will arrive as the next STT final)
        while not session.transcript_queue.empty():
            with contextlib.suppress(asyncio.QueueEmpty):
                session.transcript_queue.get_nowait()
        while not session.response_queue.empty():
            with contextlib.suppress(asyncio.QueueEmpty):
                session.response_queue.get_nowait()
        # Flush any buffered audio chunks so the next STT turn is "fresh".
        while not session.input_audio_queue.empty():
            with contextlib.suppress(asyncio.QueueEmpty):
                session.input_audio_queue.get_nowait()

        session.turn_buffer.clear()
        session.silence_ms = 0
        session.silence_retries = 0
        session.strategy_stage = "qualification"
        session.last_intent = None

    def _resolve_call_id(self, call_sid_or_id: str | None) -> str | None:
        if not call_sid_or_id:
            return None
        if call_sid_or_id in self._sessions:
            return call_sid_or_id
        if call_sid_or_id in self._sid_to_call_id:
            return self._sid_to_call_id[call_sid_or_id]
        with self.session_factory() as db:
            call = self.calls.get(db, call_sid_or_id) or self.calls.get_by_provider_call_id(db, call_sid_or_id)
            if not call:
                return None
            if call.provider_call_id:
                self._sid_to_call_id[call.provider_call_id] = call.id
            return call.id

    async def _handle_dynamic_silence(self, session: CallSessionContext) -> None:
        if session.silence_retries >= self._max_silence_retries:
            await session.response_queue.put(
                {
                    "user_text": "__silence_exit__",
                    "response_text": "I will follow up later. Thank you for your time.",
                    "language": "English",
                    "started_at": time.perf_counter(),
                    "is_micro": True,
                }
            )
            session.call_active = False
            return

        session.silence_retries += 1
        mode = self._classify_silence(session)
        if mode == "thinking_pause":
            # Wait silently; no intrusive prompt.
            return
        if mode == "confusion":
            text = "I can repeat that briefly. Are you asking about eligibility or EMI?"
        else:
            text = "Just checking if you are still there. Should I continue?"
        await session.response_queue.put(
            {
                "user_text": "__silence__",
                "response_text": text,
                "language": "English",
                "started_at": time.perf_counter(),
                "is_micro": True,
            }
        )

    def _classify_silence(self, session: CallSessionContext) -> str:
        # Dynamic silence handling based on stage + intent + duration.
        if session.silence_ms < self._min_silence_ms:
            return "thinking_pause"
        if session.last_intent in {"confused", "objection"} or session.strategy_stage == "qualification":
            return "confusion"
        if session.silence_ms >= self._max_silence_ms:
            return "disengagement"
        return "thinking_pause"

    def _micro_response(self, session: CallSessionContext) -> str | None:
        persona = (session.persona or "professional").lower()
        if persona == "friendly":
            return "hmm, got it."
        if persona == "high-energy closer":
            return "right, makes sense."
        # professional default with multilingual touch
        return "samajh gaya."

    def _filler_response(self, session: CallSessionContext) -> str:
        if (session.last_intent or "") in {"pricing", "objection"}:
            if random.random() < 0.5:
                session.ab_objection_variant = "A"
                return "One sec, checking the exact details."
            session.ab_objection_variant = "B"
            return "Got it, let me quickly verify that for you."
        return "hmm, just a second."

    def _shape_for_speech(self, text: str, *, stage: str, is_micro: bool = False) -> str:
        compact = " ".join((text or "").split())
        if is_micro:
            return compact

        # Prosody shaping: subtle fillers + pause hints.
        if stage in {"objection_handling", "qualification"} and not compact.lower().startswith(("hmm", "right", "sure")):
            compact = f"hmm, {compact}"

        # Prefer short spoken clauses.
        compact = compact.replace(" and ", ", and ")
        compact = compact.replace(" but ", ", but ")
        if len(compact) > 120 and "." not in compact:
            split_at = compact.find(",", 60)
            if split_at != -1:
                compact = compact[: split_at + 1] + " ... " + compact[split_at + 1 :].strip()

        return compact

    def _chunk_response(self, text: str) -> list[str]:
        # Response chunking: one idea per chunk.
        separators = [". ", "? ", "! ", " ... ", ", and ", ", but "]
        chunks = [text]
        for sep in separators:
            if len(chunks) == 1 and sep in chunks[0]:
                parts = [p.strip() for p in chunks[0].split(sep) if p.strip()]
                if len(parts) > 1:
                    chunks = [parts[0], " ".join(parts[1:])]
                    break
        return [c[:130].strip() for c in chunks if c.strip()]

    def _adaptive_tts_speed(self, session: CallSessionContext, emotion: str = "neutral") -> float:
        # Adaptive pacing: user speech-rate + stage.
        base = get_persona_pack(session.persona).speaking_pace
        if session.user_speech_rate_cps > 16:
            base += 0.08
        elif session.user_speech_rate_cps < 8:
            base -= 0.08

        if session.strategy_stage in {"closing", "objection_handling"}:
            base -= 0.03
        elif session.strategy_stage == "pitch":
            base += 0.02
        if emotion == "energetic":
            base += 0.05
        elif emotion in {"calm", "reassuring"}:
            base -= 0.04

        return max(0.85, min(1.15, base))

    def _cleanup_audio_chunk(self, chunk: bytes) -> bytes:
        # Audio cleanup shim for transport payloads.
        # - trims extra silence markers
        # - smooth transitions by avoiding empty chunks
        if not chunk:
            return b""
        cleaned = chunk.strip()
        return cleaned

    def _estimate_audio_energy(self, audio: bytes) -> float:
        if not audio:
            return 0.0
        return sum(abs(b - 128) for b in audio[:400]) / max(1, min(len(audio), 400))

    def _is_silence(self, audio: bytes, rolling_energy: float) -> bool:
        if not audio:
            return True
        avg_energy = self._estimate_audio_energy(audio)
        # Hybrid threshold includes rolling context to avoid false positives.
        dynamic_threshold = max(1.8, min(3.8, rolling_energy * self._energy_threshold_mult))
        return avg_energy < dynamic_threshold

    def _apply_language_tuning(self, session: CallSessionContext, language: str) -> None:
        key = (language or "default").lower()
        if key not in self._language_profiles:
            key = "default"
        session.language_profile = key
        profile = self._language_profiles[key]
        persona_pack = get_persona_pack(session.persona)

        self._silence_turn_trigger_ms = int((profile["silence_ms"] * 0.7) + (persona_pack.silence_tolerance_ms * 0.3))
        self._min_silence_ms = max(700, self._silence_turn_trigger_ms - 180)
        self._max_silence_ms = min(1400, self._silence_turn_trigger_ms + 180)
        self._min_final_confidence = float(profile["confidence_min"])
        self._energy_threshold_mult = float(profile.get("energy_mult", 0.55))

    async def _prepare_candidates(self, session: CallSessionContext, user_text: str) -> None:
        with self.session_factory() as db:
            call = self.calls.get(db, session.call_id)
            lead = self.leads.get(db, session.lead_id)
            if not call or not lead:
                return
            lead_context = self.llm.build_lead_context(lead, call)
            candidates = self.llm.prepare_likely_responses(
                user_text,
                {
                    **lead_context,
                    "strategy_stage": session.strategy_stage,
                    "persona": session.persona,
                    "turn_index": session.turn_index,
                },
            )
            if candidates:
                session.prepared_candidates[user_text[:60].lower()] = candidates[:2]

    def _select_prepared_candidates(self, session: CallSessionContext, user_text: str) -> list[str] | None:
        key = user_text[:60].lower()
        if key in session.prepared_candidates:
            return session.prepared_candidates.pop(key, None)
        for k in list(session.prepared_candidates.keys()):
            if key.startswith(k[:20]) or k.startswith(key[:20]):
                return session.prepared_candidates.pop(k, None)
        return None

    async def _emit_tuning_debug(
        self,
        session: CallSessionContext,
        *,
        phase: str,
        emotion: str,
        llm_ms: float = 0.0,
        tts_ms: float = 0.0,
    ) -> None:
        if not self.enable_tuning_debug:
            return
        payload = {
            "call_id": session.call_id,
            "phase": phase,
            "language_profile": session.language_profile,
            "persona": session.persona,
            "emotion": emotion,
            "intent": session.last_intent,
            "stage": session.strategy_stage,
            "silence_ms": session.silence_ms,
            "confidence": round(session.partial_confidence, 3),
            "ab_variant": session.ab_opening_variant,
            "latency_ms": {
                "stt": round(session.metrics["stt_ms"][-1], 2) if session.metrics["stt_ms"] else 0.0,
                "llm": round(llm_ms, 2),
                "tts": round(tts_ms, 2),
            },
        }
        await ws_manager.emit("dashboard", "tuning_debug", payload)

    @staticmethod
    def _avg(values: list[float]) -> float:
        return round(sum(values) / len(values), 2) if values else 0.0
