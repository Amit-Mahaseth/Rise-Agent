from functools import lru_cache
from typing import Any

from app.core.config import Settings, get_settings
from app.db.session import SessionLocal


@lru_cache
def get_app_settings() -> Settings:
    return get_settings()


@lru_cache
def get_knowledge_base() -> Any:
    from app.services.rag.knowledge_base import KnowledgeBaseService

    return KnowledgeBaseService(get_app_settings())


@lru_cache
def get_memory_service() -> Any:
    from app.services.memory.chroma_memory import ChromaMemoryService

    return ChromaMemoryService(get_app_settings())


@lru_cache
def get_voice_client() -> Any:
    from app.services.voice.sarvam_client import SarvamVoiceClient

    return SarvamVoiceClient(get_app_settings())


@lru_cache
def get_conversation_engine() -> Any:
    from app.services.conversation_engine import ConversationEngine
    from app.services.llm.factory import build_chat_model

    settings = get_app_settings()
    return ConversationEngine(
        settings=settings,
        model=build_chat_model(settings),
        knowledge_base=get_knowledge_base(),
        memory_service=get_memory_service(),
        voice_client=get_voice_client(),
    )


@lru_cache
def get_orchestrator() -> Any:
    from app.repositories.call_repository import CallRepository
    from app.repositories.lead_repository import LeadRepository
    from app.services.handoff import HumanHandoffService
    from app.services.messaging.whatsapp import WhatsAppService
    from app.services.orchestrator import RiseAgentOrchestrator
    from app.services.scoring import LeadScoringService
    from app.services.telephony.twilio_provider import TwilioCallProvider

    settings = get_app_settings()
    return RiseAgentOrchestrator(
        settings=settings,
        session_factory=SessionLocal,
        lead_repository=LeadRepository(),
        call_repository=CallRepository(),
        call_provider=TwilioCallProvider(settings),
        conversation_engine=get_conversation_engine(),
        memory_service=get_memory_service(),
        scoring_service=LeadScoringService(),
        whatsapp_service=WhatsAppService(settings),
        handoff_service=HumanHandoffService(settings),
    )
