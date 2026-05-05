from app.services.scoring import LeadScoringService


class ScoringServiceV2:
    def __init__(self) -> None:
        self._scoring = LeadScoringService()

    async def score_lead(self, transcript: str, duration_seconds: int, tone: str | None = None) -> dict:
        result = self._scoring.score(transcript=transcript, duration_seconds=duration_seconds, tone=tone)
        objections = result.objections or []
        objection_count = len(objections)
        conversion_probability = round(max(0.0, min(1.0, result.total_score / 100.0)), 3)
        engagement_score = float((result.breakdown or {}).get("engagement_score", 0.0))
        if engagement_score >= 12:
            engagement_level = "high"
        elif engagement_score >= 7:
            engagement_level = "medium"
        else:
            engagement_level = "low"
        return {
            "score": int(round(result.total_score)),
            "category": result.classification,
            "intent": result.intent,
            "objections": objections,
            "objection_count": objection_count,
            "summary": result.summary,
            "breakdown": result.breakdown,
            "next_action": result.next_action,
            "engagement_level": engagement_level,
            "conversion_probability": conversion_probability,
        }
