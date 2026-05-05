"""
Call record model for RiseAgent AI.
Tracks voice call sessions with comprehensive metadata.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import JSON, DateTime, Integer, String, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.time import utcnow


class CallRecord(Base):
    """
    Call record model for tracking voice conversations.
    """
    __tablename__ = "calls"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to lead
    lead_id: Mapped[str] = mapped_column(String(64), ForeignKey("leads.lead_id"), nullable=False, index=True)

    # Twilio/provider details
    provider_call_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    twilio_call_sid: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Call status and lifecycle
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    direction: Mapped[str] = mapped_column(String(20), default="outbound")  # inbound, outbound

    # Language and communication
    detected_language: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    language_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Conversation analysis
    intent: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    intent_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Content
    transcript: Mapped[str] = mapped_column(Text, nullable=False, default="")
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    key_points: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Objections and responses
    objections: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    objection_responses: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)

    # Scoring and classification
    score_breakdown: Mapped[Dict] = mapped_column(JSON, nullable=False, default=dict)
    overall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    classification: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)

    # Actions and routing
    next_action: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    routed_to_rm: Mapped[bool] = mapped_column(Boolean, default=False)
    rm_id: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)

    # Call quality metrics
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    call_quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dropped_call: Mapped[bool] = mapped_column(Boolean, default=False)
    user_hangup: Mapped[bool] = mapped_column(Boolean, default=False)

    # Audio metadata
    recording_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    audio_format: Mapped[str] = mapped_column(String(20), default="wav")

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    # Relationships
    lead = relationship("Lead", back_populates="calls")

    def __repr__(self):
        return f"<CallRecord(id={self.id}, lead_id={self.lead_id}, status={self.status}, duration={self.duration_seconds}s)>"

    @property
    def is_completed(self) -> bool:
        """Check if call is completed."""
        return self.status in ["completed", "answered", "failed"]

    @property
    def is_successful(self) -> bool:
        """Check if call was successful (answered and not dropped)."""
        return self.status == "completed" and not self.dropped_call

    @property
    def has_recording(self) -> bool:
        """Check if call has a recording."""
        return self.recording_url is not None

    @property
    def objection_count(self) -> int:
        """Get count of objections raised."""
        return len(self.objections) if self.objections else 0

