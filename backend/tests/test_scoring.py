from app.services.scoring import LeadScoringService


def test_hot_lead_scores_high() -> None:
    service = LeadScoringService()
    result = service.score(
        transcript=(
            "customer: I am interested and need loan urgently. "
            "Please send link and tell me what documents are needed."
        ),
        duration_seconds=240,
        tone="positive",
    )
    assert result.classification == "HOT"
    assert result.total_score >= 75


def test_cold_lead_scores_low() -> None:
    service = LeadScoringService()
    result = service.score(
        transcript="customer: Not interested. Please stop calling. Wrong number.",
        duration_seconds=20,
        tone="frustrated",
    )
    assert result.classification == "COLD"
    assert result.next_action == "reengagement_pool"

