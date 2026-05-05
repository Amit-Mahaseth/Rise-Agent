from dataclasses import dataclass


SUPPORTED_TONES = {"positive", "neutral", "hesitant", "frustrated"}

HOT_INTENT_PATTERNS = (
    "interested",
    "send link",
    "apply now",
    "call me today",
    "need loan urgently",
    "eligible",
    "what documents",
    "how soon can i get",
)
WARM_INTENT_PATTERNS = (
    "thinking",
    "maybe",
    "compare",
    "call later",
    "share details",
    "whatsapp me",
)
NEGATIVE_PATTERNS = (
    "not interested",
    "don't call",
    "stop calling",
    "already taken",
    "wrong number",
)
OBJECTION_KEYWORDS = {
    "interest_rate": ("rate", "interest", "expensive"),
    "trust": ("safe", "fraud", "genuine"),
    "eligibility": ("eligible", "salary", "cibil"),
    "documents": ("documents", "paperwork", "kyc"),
    "timing": ("busy", "later", "tomorrow"),
}


@dataclass(slots=True)
class LeadScoreResult:
    total_score: float
    classification: str
    next_action: str
    intent: str
    objections: list[str]
    summary: str
    breakdown: dict


class LeadScoringService:
    def score(self, transcript: str, duration_seconds: int, tone: str | None) -> LeadScoreResult:
        lower_text = transcript.lower()
        objections = self._extract_objections(lower_text)

        intent_score, intent = self._score_intent(lower_text)
        engagement_score = min(duration_seconds / 12, 20)
        tone_score = self._score_tone(tone)
        objection_score = max(0.0, 20 - (len(objections) * 4))

        total_score = round(intent_score + engagement_score + tone_score + objection_score, 2)
        classification = "HOT" if total_score >= 75 else "WARM" if total_score >= 50 else "COLD"
        next_action = {
            "HOT": "handoff_to_rm",
            "WARM": "send_whatsapp_followup",
            "COLD": "reengagement_pool",
        }[classification]

        summary = (
            f"Lead shows {intent} intent with {duration_seconds}s engagement, "
            f"tone marked as {tone or 'neutral'}, and objections: {', '.join(objections) or 'none'}."
        )
        breakdown = {
            "intent_score": round(intent_score, 2),
            "engagement_score": round(engagement_score, 2),
            "tone_score": round(tone_score, 2),
            "objection_score": round(objection_score, 2),
            "total_score": total_score,
        }
        return LeadScoreResult(
            total_score=total_score,
            classification=classification,
            next_action=next_action,
            intent=intent,
            objections=objections,
            summary=summary,
            breakdown=breakdown,
        )

    def _score_intent(self, text: str) -> tuple[float, str]:
        if any(pattern in text for pattern in NEGATIVE_PATTERNS):
            return 5.0, "low"
        if sum(pattern in text for pattern in HOT_INTENT_PATTERNS) >= 2:
            return 40.0, "high"
        if any(pattern in text for pattern in WARM_INTENT_PATTERNS):
            return 28.0, "medium"
        return 15.0, "exploratory"

    def _score_tone(self, tone: str | None) -> float:
        normalized = (tone or "neutral").lower()
        if normalized not in SUPPORTED_TONES:
            normalized = "neutral"
        return {
            "positive": 18.0,
            "neutral": 12.0,
            "hesitant": 8.0,
            "frustrated": 3.0,
        }[normalized]

    def _extract_objections(self, text: str) -> list[str]:
        objections: list[str] = []
        for key, keywords in OBJECTION_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                objections.append(key)
        return objections

