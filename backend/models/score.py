"""Lead scoring Pydantic models."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    """Full scoring breakdown with every signal."""
    total_score: int = Field(..., ge=0, le=100)
    verbal_intent: bool = False
    verbal_intent_points: int = 0
    objection_count: int = 0
    objection_points: int = 0
    duration_seconds: int = 0
    duration_points: int = 0
    network_mentioned: bool = False
    network_points: int = 0
    tone_score: int = Field(default=0, ge=0, le=2)
    tone_points: int = 0
    classification: str = Field(..., pattern="^(hot|warm|cold)$")


class ScoreResponse(BaseModel):
    """Score record as returned from API."""
    id: str
    lead_id: str
    call_id: str
    total_score: int
    verbal_intent: bool = False
    objection_count: int = 0
    duration_score: int = 0
    network_mentioned: bool = False
    tone_score: int = 0
    classification: str
    created_at: Optional[str] = None
