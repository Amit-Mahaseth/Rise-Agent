from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CallTurnRequest(BaseModel):
    user_text: str = Field(min_length=1)
    tone: str | None = Field(default=None, description="positive, neutral, hesitant, frustrated")
    duration_seconds: int = Field(default=0, ge=0)


class TurnArtifact(BaseModel):
    assistant_text: str
    detected_language: str
    knowledge_hits: list[str]
    memory_hits: list[str]
    audio_payload: dict | None = None


class CallTurnResponse(BaseModel):
    call_id: str
    status: str
    artifact: TurnArtifact


class CallCompleteResponse(BaseModel):
    call_id: str
    status: str
    classification: str
    next_action: str
    score_breakdown: dict
    summary: str


class CallResponse(BaseModel):
    call_id: str
    status: str
    message: str


class CallDetailResponse(BaseModel):
    call_id: str
    lead_id: str
    status: str
    duration_seconds: int | None
    transcript: str | None
    detected_language: str | None
    call_quality_score: float | None
    lead_name: str | None
    lead_phone: str | None
    created_at: datetime
    answered_at: datetime | None
    ended_at: datetime | None


class CallEventRequest(BaseModel):
    event_type: str = Field(description="Type of call event")
    event_data: dict | None = Field(default=None, description="Additional event data")


class CallRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lead_id: str
    provider_call_id: str | None
    status: str
    detected_language: str | None
    intent: str | None
    tone: str | None
    transcript: str
    summary: str | None
    objections: list[str]
    score_breakdown: dict
    classification: str | None
    next_action: str | None
    duration_seconds: int
    started_at: datetime | None
    ended_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

