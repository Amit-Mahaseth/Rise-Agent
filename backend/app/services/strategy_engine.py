from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StrategyUpdate:
    stage: str
    # How aggressively we should use LLM/context (cost control).
    llm_priority: str  # high | low


class StrategyEngine:
    """
    Conversation strategy (opening -> qualification -> pitch -> objection -> closing).

    We keep this intentionally simple to avoid latency and complexity.
    """

    def initial_stage(self) -> str:
        return "opening"

    def update(self, *, current_stage: str, intent: str, turn_index: int) -> StrategyUpdate:
        # Hard stops first.
        if intent == "not_interested":
            return StrategyUpdate(stage="closing", llm_priority="low")
        if intent == "callback_later":
            return StrategyUpdate(stage="closing", llm_priority="low")

        if intent == "objection":
            return StrategyUpdate(stage="objection_handling", llm_priority="high")
        if intent == "confused":
            return StrategyUpdate(stage="qualification", llm_priority="high")

        if intent == "pricing":
            return StrategyUpdate(stage="pitch", llm_priority="high")

        if intent == "interested":
            # First qualified interest is usually still qualification; later becomes pitch.
            if turn_index <= 1 or current_stage in {"opening"}:
                return StrategyUpdate(stage="qualification", llm_priority="high")
            return StrategyUpdate(stage="pitch", llm_priority="high")

        # Default progression.
        if current_stage in {"opening", "qualification"}:
            if turn_index >= 2:
                return StrategyUpdate(stage="pitch", llm_priority="high")
            return StrategyUpdate(stage="qualification", llm_priority="high")

        if current_stage == "pitch" and turn_index >= 3:
            return StrategyUpdate(stage="closing", llm_priority="low")

        return StrategyUpdate(stage=current_stage, llm_priority="high")

