import re
from typing import Any

from app.models.call import CallRecord
from app.models.lead import Lead
from app.services.llm.prompt_builder import build_conversation_prompt
from app.services.memory.chroma_memory import ChromaMemoryService
from app.services.rag.knowledge_base import KnowledgeBaseService
from app.services.voice.sarvam_client import SarvamVoiceClient

SUPPORTED_LANGUAGES = (
    "Hindi",
    "English",
    "Hinglish",
    "Marathi",
    "Tamil",
    "Telugu",
    "Gujarati",
    "Bengali",
)


class ConversationEngine:
    def __init__(
        self,
        *,
        settings: Any,
        model: Any,
        knowledge_base: KnowledgeBaseService,
        memory_service: ChromaMemoryService,
        voice_client: SarvamVoiceClient,
    ) -> None:
        self.settings = settings
        self.model = model
        self.knowledge_base = knowledge_base
        self.memory_service = memory_service
        self.voice_client = voice_client
        self.prompt = build_conversation_prompt()

    def generate_reply(
        self,
        *,
        lead: Lead,
        call: CallRecord,
        user_text: str,
        strategy_stage: str | None = None,
        persona: str | None = None,
        store_to_memory: bool = True,
    ) -> dict:
        detected_language = self.detect_language(user_text, call.detected_language or lead.preferred_language)
        stage = strategy_stage or "qualification"
        persona_name = persona or "professional"

        # Stage-aware retrieval (token/cost control).
        if stage in {"opening", "closing"}:
            knowledge_k = 2
            memory_k = 1
        elif stage in {"qualification"}:
            knowledge_k = 3
            memory_k = 2
        elif stage in {"pitch"}:
            knowledge_k = 4
            memory_k = 3
        else:
            # objection_handling
            knowledge_k = 4
            memory_k = 3

        knowledge_docs = self.knowledge_base.retrieve(user_text, k=knowledge_k)
        memory_docs = self.memory_service.retrieve_memories(lead_id=lead.lead_id, query=user_text, k=memory_k)

        lead_context = (
            f"lead_id={lead.lead_id}, name={lead.full_name}, source={lead.source}, "
            f"product_interest={lead.product_interest}, notes={lead.notes or 'none'}"
        )
        transcript = call.transcript or "No earlier turns in this call."
        knowledge_context = "\n\n".join(doc.page_content for doc in knowledge_docs) or "No knowledge snippets found."
        memory_context = "\n".join(doc.page_content for doc in memory_docs) or "No prior memory available."

        prompt_value = self.prompt.invoke(
            {
                "lead_context": lead_context,
                "language": detected_language,
                "persona": persona_name,
                "strategy_stage": stage,
                "knowledge_context": knowledge_context,
                "memory_context": memory_context,
                "transcript": transcript,
                "user_text": user_text,
            }
        )
        response = self.model.invoke(prompt_value)
        assistant_text = self._normalize_content(response)

        # Store turns after the assistant response has been generated.
        # In realtime mode, we can disable this and let the orchestration layer
        # store only successfully-spoken turns (important for interruptions).
        if store_to_memory:
            self.memory_service.store_turn(lead_id=lead.lead_id, call_id=call.id, speaker="customer", text=user_text)
            self.memory_service.store_turn(
                lead_id=lead.lead_id,
                call_id=call.id,
                speaker="assistant",
                text=assistant_text,
            )

        return {
            "assistant_text": assistant_text,
            "detected_language": detected_language,
            "knowledge_hits": [f"{doc.metadata.get('source')}: {doc.page_content[:120]}" for doc in knowledge_docs],
            "memory_hits": [doc.page_content[:120] for doc in memory_docs],
            "audio_payload": self.voice_client.synthesize(assistant_text, detected_language),
        }

    def detect_language(self, text: str, current_language: str | None = None) -> str:
        stripped = text.strip()
        if not stripped:
            return current_language or "English"

        if re.search(r"[\u0B80-\u0BFF]", stripped):
            return "Tamil"
        if re.search(r"[\u0C00-\u0C7F]", stripped):
            return "Telugu"
        if re.search(r"[\u0A80-\u0AFF]", stripped):
            return "Gujarati"
        if re.search(r"[\u0980-\u09FF]", stripped):
            return "Bengali"
        if re.search(r"[\u0900-\u097F]", stripped):
            marathi_tokens = ("आहे", "तुम्हाला", "कर्ज", "पाहिजे")
            return "Marathi" if any(token in stripped for token in marathi_tokens) else "Hindi"

        lowercase = stripped.lower()
        hinglish_tokens = ("haan", "nahi", "chahiye", "abhi", "kal", "paisa", "loan", "kitna", "samjhao")
        if any(token in lowercase for token in hinglish_tokens):
            return "Hinglish"

        return current_language or "English"

    def _normalize_content(self, response: Any) -> str:
        content = getattr(response, "content", response)
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            text_blocks: list[str] = []
            for item in content:
                if isinstance(item, str):
                    text_blocks.append(item)
                elif isinstance(item, dict) and item.get("type") == "text":
                    text_blocks.append(item.get("text", ""))
                else:
                    text = getattr(item, "text", "")
                    if text:
                        text_blocks.append(text)
            return " ".join(part.strip() for part in text_blocks if part.strip())
        return str(content).strip()

