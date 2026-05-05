"""Call session Pydantic models."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CallInitiate(BaseModel):
    """Payload for POST /calls/initiate."""
    lead_id: str = Field(..., description="UUID of the lead to call")
    phone: Optional[str] = Field(default=None, description="Override phone if different from lead record")


class CallResponse(BaseModel):
    """Call record as returned from API."""
    id: str
    lead_id: str
    call_sid: Optional[str] = None
    provider: Optional[str] = None
    status: str = "initiated"
    duration_seconds: int = 0
    language_used: Optional[str] = None
    call_number: int = 1
    started_at: Optional[str] = None
    ended_at: Optional[str] = None


class CallEventResponse(BaseModel):
    """Single conversation turn."""
    id: str
    call_id: str
    turn_number: int
    speaker: str  # 'agent' or 'lead'
    text: str
    language: Optional[str] = None
    timestamp: Optional[str] = None


class CallDetailResponse(BaseModel):
    """Full call detail with transcript."""
    call: CallResponse
    events: list[CallEventResponse] = []
    score: Optional[dict] = None
    lead: Optional[dict] = None
