"""
Pydantic schemas for Scoring model.
"""

from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field, ConfigDict


class ScoringBase(BaseModel):
    """Base schema for Scoring."""
    lead_id: str = Field(..., description="Lead identifier")
    session_id: str = Field(..., description="Session identifier")


class ScoringCreate(ScoringBase):
    """Schema for creating a new scoring record."""
    intent_score: float = Field(default=0.0, ge=0.0, le=1.0)
    engagement_score: float = Field(default=0.0, ge=0.0, le=1.0)
    objection_score: float = Field(default=0.0, ge=0.0, le=1.0)
    tone_score: float = Field(default=0.0, ge=0.0, le=1.0)


class ScoringUpdate(BaseModel):
    """Schema for updating scoring record."""
    intent_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    engagement_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    objection_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    tone_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    conversation_length_seconds: Optional[int] = Field(None, ge=0)
    message_count: Optional[int] = Field(None, ge=0)
    objection_count: Optional[int] = Field(None, ge=0)
    positive_signals: Optional[int] = Field(None, ge=0)


class ScoringResponse(ScoringBase):
    """Schema for Scoring API responses."""
    id: int
    intent_score: float
    engagement_score: float
    objection_score: float
    tone_score: float
    overall_score: float
    classification: Optional[str]
    conversation_length_seconds: int
    message_count: int
    user_message_count: int
    assistant_message_count: int
    objection_count: int
    objections_handled: int
    objection_types: Optional[Dict[str, int]]
    positive_signals: int
    positive_keywords: Optional[List[str]]
    language_consistency_score: float
    communication_clarity_score: float
    scoring_model_version: str
    scoring_metadata: Optional[Dict]
    confidence_intervals: Optional[Dict]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScoringSummary(BaseModel):
    """Simplified scoring summary."""
    lead_id: str
    session_id: str
    overall_score: float
    classification: Optional[str]
    objection_resolution_rate: float
    engagement_rate: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadQualificationResult(BaseModel):
    """Result of lead qualification process."""
    lead_id: str
    session_id: str
    classification: str
    confidence_score: float
    reasoning: str
    recommended_action: str
    rm_handoff_required: bool
    whatsapp_followup_required: bool

    model_config = ConfigDict(from_attributes=True)