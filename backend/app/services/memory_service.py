from app.services.memory.chroma_memory import ChromaMemoryService


class MemoryService:
    def __init__(self, vector_memory: ChromaMemoryService) -> None:
        self._vector_memory = vector_memory
        # Cost control: don't store unlimited per-call raw turns.
        self._turn_store_counts: dict[str, int] = {}
        self._max_turns_to_store_per_call = 6

    async def get_memory(self, lead_id: str) -> dict:
        # Keep context window tight for low-latency/token-efficient prompts.
        docs = self._vector_memory.retrieve_memories(lead_id=lead_id, query="latest lead context", k=3)
        objections = [d.page_content for d in docs if "objection" in d.page_content.lower()]
        preferred_language = next(
            (d.metadata.get("language") for d in docs if isinstance(d.metadata, dict) and d.metadata.get("language")),
            None,
        )
        return {
            "past_objections": objections[:5],
            "interest_level": "high" if len(docs) >= 5 else "medium" if len(docs) >= 3 else "low",
            "preferred_language": preferred_language,
            "raw_memories": [d.page_content for d in docs[:6]],
        }

    async def update_memory(self, lead_id: str, new_data: dict) -> None:
        call_id = str(new_data.get("call_id", "session"))
        customer_text = str(new_data.get("customer_text", "")).strip()
        assistant_text = str(new_data.get("assistant_text", "")).strip()
        language = str(new_data.get("language", "")).strip()

        # Only store a limited number of raw turns per call.
        prev = self._turn_store_counts.get(call_id, 0)
        self._turn_store_counts[call_id] = prev + 1
        if prev >= self._max_turns_to_store_per_call:
            # Still update language preference summary (cheap).
            if language:
                self._vector_memory.store_summary(
                    lead_id=lead_id,
                    call_id=call_id,
                    summary=f"preferred_language={language}",
                )
            return

        if customer_text:
            self._vector_memory.store_turn(lead_id=lead_id, call_id=call_id, speaker="customer", text=customer_text)
        if assistant_text:
            self._vector_memory.store_turn(lead_id=lead_id, call_id=call_id, speaker="assistant", text=assistant_text)
        if language:
            self._vector_memory.store_summary(
                lead_id=lead_id,
                call_id=call_id,
                summary=f"preferred_language={language}",
            )

    async def compress_and_store_after_call(
        self,
        *,
        lead_id: str,
        call_id: str,
        scoring: dict,
        detected_language: str | None = None,
    ) -> None:
        """
        Post-call memory compression:
        - store only key insights (objections, interest level, outcome)
        - avoid long transcript persistence
        """
        category = str(scoring.get("category") or "COLD")
        objections = scoring.get("objections") or []
        if not isinstance(objections, list):
            objections = [str(objections)]

        interest_level = "high" if category == "HOT" else "medium" if category == "WARM" else "low"
        objection_str = ", ".join(o[:80] for o in objections[:5]) if objections else "none"
        next_action = scoring.get("next_action") or "follow_up"

        compressed = (
            f"outcome={category}; interest={interest_level}; objections={objection_str}; "
            f"next_action={next_action}. "
            f"verbatim_summary={str(scoring.get('summary') or '')[:220]}"
        )
        self._vector_memory.store_summary(
            lead_id=lead_id,
            call_id=call_id,
            summary=compressed[:500],
        )
