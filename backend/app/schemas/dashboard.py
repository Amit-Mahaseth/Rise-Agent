from pydantic import BaseModel


class FunnelMetrics(BaseModel):
    total_leads: int
    hot: int
    warm: int
    cold: int
    hot_rate: float


class CallSummaryItem(BaseModel):
    call_id: str
    lead_id: str
    customer_name: str
    classification: str | None
    language: str | None
    intent: str | None
    next_action: str | None
    summary: str | None
    duration_seconds: int


class RMTrackingItem(BaseModel):
    rm_name: str
    assigned_leads: int
    hot_leads: int
    warm_leads: int


class DashboardResponse(BaseModel):
    funnel: FunnelMetrics
    call_summaries: list[CallSummaryItem]
    rm_tracking: list[RMTrackingItem]
    language_distribution: dict[str, int]

