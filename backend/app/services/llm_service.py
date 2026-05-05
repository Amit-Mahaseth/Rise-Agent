from __future__ import annotations

import re
from functools import lru_cache

from app.models.call import CallRecord
from app.models.lead import Lead
from app.services.conversation_engine import ConversationEngine
from app.services.intent_classifier import IntentClassifier
from app.services.persona import get_persona_pack
from app.services.strategy_engine import StrategyEngine


class LLMService:
    def __init__(self, conversation_engine: ConversationEngine) -> None:
        self._engine = conversation_engine
        self._intent_classifier = IntentClassifier()
        self._strategy_engine = StrategyEngine()
        self._response_cache: dict[str, str] = {}

    def _trim_to_1_2_sentences(self, text: str) -> str:
        cleaned = (text or "").replace("\n", " ").strip()
        if not cleaned:
            return cleaned
        # Split on sentence terminators and keep the first 2.
        parts = re.split(r"(?<=[.!?])\s+", cleaned)
        parts = [p.strip() for p in parts if p.strip()]
        if not parts:
            return cleaned[:160]
        return " ".join(parts[:2])

    @staticmethod
    def _is_low_priority(intent: str, stage: str) -> bool:
        # Conservative: only use rule-based bypass for low-impact intents/stages.
        return intent in {"not_interested", "callback_later"} or stage in {"closing"}

    @lru_cache(maxsize=256)
    def _build_bypass_response(self, intent: str, language: str, persona: str) -> str:
        _ = get_persona_pack(persona)
        # Keep bypass responses as 1–2 sentences to control cost and improve voice naturalness.
        # Minimal multilingual templates (romanized/script-light) for voice consistency.
        # If Sarvam language is detected, this keeps the prompt aligned.
        is_eng = language == "English"
        if intent == "not_interested":
            if is_eng:
                return "No worries. If you want Rupeezy options later, I can share details anytime."
            if language == "Hindi" or language == "Hinglish":
                return "Samajh gaya. Jab zarurat ho, main Rupeezy options details share kar dunga."
            if language == "Tamil":
                return "Purindhukonden. Appo Rupeezy options venumna, details jederzeit share panren."
            if language == "Telugu":
                return "Arthamayyindi. Taruvatha Rupeezy options kavali ante details share chestanu."
            return "Samajh gaya. Baad mein zarurat ho to main details share kar dunga."
        if intent == "callback_later":
            if is_eng:
                return "Sure-what day and time should I call you back?"
            if language == "Hindi" or language == "Hinglish":
                return "Bilkul-kis din aur kis time par main call karun?"
            if language == "Tamil":
                return "Sarile. Enna naalum, enna neramum meendum call panren?"
            if language == "Telugu":
                return "Okay-e roju nunchi/next eppudu, ela time lo call cheyyali?"
            return "Bilkul-kis din aur kis time par main call karun?"
        if intent == "pricing":
            if is_eng:
                return "Got it. For EMI estimates, what loan amount are you considering?"
            if language == "Hindi" or language == "Hinglish":
                return "Samajh gaya. EMI estimate ke liye, aap kitna loan soch rahe hain?"
            if language == "Tamil":
                return "Puriyudhu. EMI estimate-kku, neenga eththa loan amount paakkareenga?"
            if language == "Telugu":
                return "Arthamayyindi. EMI estimate kosam, meeru entha loan amount consider chestunnaru?"
            return "Samajh gaya. EMI estimate ke liye, aap kitna loan soch rahe hain?"
        if intent == "objection":
            if is_eng:
                return "I understand your concern. Would you like a quick breakdown of eligibility and rates based on your details?"
            if language == "Hindi" or language == "Hinglish":
                return "Aapki concern samajh aayi. Kya main aapke details ke basis par eligibility aur rates ka quick breakdown de doon?"
            if language == "Tamil":
                return "Ungal kavala puriyuthu. Details adippadai-la eligibility & rates quick breakdown venuma?"
            if language == "Telugu":
                return "Meeru concerned anukunta. Mi details batti eligibility & rates ni quick breakdown cheppana?"
            return "Aapki concern samajh aayi. Kya main details ke basis par quick breakdown de doon?"
        if intent == "confused":
            if is_eng:
                return "No problem-I can explain. Are you asking about eligibility, documents, or the application process?"
            if language == "Hindi" or language == "Hinglish":
                return "Koi baat nahi-main samjha deta hoon. Aapko eligibility, documents, ya process mein se kya chahiye?"
            if language == "Tamil":
                return "Problem illa. Eligibility, documents, illa application process-ethukkaaga kekkureenga?"
            if language == "Telugu":
                return "Tappu ledu. Eligibility, documents, leka application process lo edhi kavali?"
            return "Koi baat nahi-main samjha deta hoon."
        # Default interested
        if is_eng:
            return "Great-next, can you share your monthly income and preferred loan tenure?"
        if language == "Hindi" or language == "Hinglish":
            return "Achha-abhi aap apni monthly income aur loan tenure bata dijiye."
        if language == "Tamil":
            return "Semma-next, neenga monthly income & loan tenure edhu?"
        if language == "Telugu":
            return "Super-next, monthly income & loan tenure cheppandi."
        return "Achha-abhi aap monthly income aur loan tenure bata dijiye."

    async def generate_response(self, input_text: str, lead_context: dict) -> dict:
        lead: Lead = lead_context["lead"]
        call: CallRecord = lead_context["call"]

        # Session-aware fields are passed from RealtimeCallService.
        current_stage: str = str(lead_context.get("strategy_stage") or "opening")
        persona: str = str(lead_context.get("persona") or "professional")
        turn_index: int = int(lead_context.get("turn_index") or 1)

        # 1) Intent classification: cheap + deterministic.
        intent_result = self._intent_classifier.classify(input_text)
        intent = intent_result.intent

        # 2) Strategy engine: update stage and cost priority.
        strategy_update = self._strategy_engine.update(
            current_stage=current_stage, intent=intent, turn_index=turn_index
        )
        stage = strategy_update.stage

        # 3) First-round cost control: bypass LLM for low-priority intents.
        detected_language = self._engine.detect_language(input_text, call.detected_language or lead.preferred_language)
        store_to_memory = bool(lead_context.get("store_to_memory", True))
        if strategy_update.llm_priority == "low" or self._is_low_priority(intent, stage):
            bypass = self._build_bypass_response(intent=intent, language=detected_language, persona=persona)
            return {
                "text": self._trim_to_1_2_sentences(bypass),
                "detected_language": detected_language,
                "intent": intent,
                "strategy_stage": stage,
                "emotion": self._emotion_for(intent, stage),
                "knowledge_hits": [],
                "memory_hits": [],
            }

        # 4) LLM path: stage- and persona-aware prompt.
        cache_key = f"{persona}:{stage}:{intent}:{detected_language}:{input_text[:80]}"
        if cache_key in self._response_cache:
            cached = self._response_cache[cache_key]
            return {
                "text": cached,
                "detected_language": detected_language,
                "intent": intent,
                "strategy_stage": stage,
                "emotion": self._emotion_for(intent, stage),
                "knowledge_hits": [],
                "memory_hits": [],
            }

        result = self._engine.generate_reply(
            lead=lead,
            call=call,
            user_text=input_text,
            strategy_stage=stage,
            persona=persona,
            store_to_memory=store_to_memory,
        )
        assistant_text = self._trim_to_1_2_sentences(result["assistant_text"])

        self._response_cache[cache_key] = assistant_text

        return {
            "text": assistant_text,
            "detected_language": result["detected_language"],
            "intent": intent,
            "strategy_stage": stage,
            "emotion": self._emotion_for(intent, stage),
            "knowledge_hits": result.get("knowledge_hits", []),
            "memory_hits": result.get("memory_hits", []),
        }

    def prepare_likely_responses(self, input_text: str, lead_context: dict) -> list[str]:
        """
        Pre-emptive response candidates for early turn prediction.
        Kept lightweight to avoid additional latency.
        """
        call: CallRecord = lead_context["call"]
        persona: str = str(lead_context.get("persona") or "professional")
        detected_language = self._engine.detect_language(input_text, call.detected_language)
        intent = self._intent_classifier.classify(input_text).intent
        primary = self._trim_to_1_2_sentences(
            self._build_bypass_response(intent=intent, language=detected_language, persona=persona)
        )
        secondary = self._trim_to_1_2_sentences(
            "Thanks, got it. Should I continue with the next step?"
            if detected_language == "English"
            else "Theek hai, samajh gaya. Kya main agla step continue karun?"
        )
        return [primary, secondary]

    def _emotion_for(self, intent: str, stage: str) -> str:
        if intent in {"objection", "confused"}:
            return "reassuring"
        if stage in {"pitch", "closing"} and intent in {"interested", "pricing"}:
            return "energetic"
        if intent in {"not_interested", "callback_later"}:
            return "calm"
        return "neutral"

    @staticmethod
    def build_lead_context(lead: Lead, call: CallRecord) -> dict:
        return {"lead": lead, "call": call}
