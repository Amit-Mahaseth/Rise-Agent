"""
Scoring model for RiseAgent AI.
Tracks lead qualification scores and metrics.
"""

from datetime import datetime
from typing import Optional, Dict
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base
from app.utils.time import utcnow


class Scoring(Base):
    """
    Scoring model for lead qualification and performance metrics.
    """
    __tablename__ = "scoring"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key to lead
    lead_id: Mapped[str] = mapped_column(String(64), ForeignKey("leads.lead_id"), nullable=False, index=True)

    # Session reference
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Individual scoring components (0-1 scale)
    intent_score: Mapped[float] = mapped_column(Float, default=0.0)  # Purchase intent
    engagement_score: Mapped[float] = mapped_column(Float, default=0.0)  # Engagement level
    objection_score: Mapped[float] = mapped_column(Float, default=0.0)  # Objection handling
    tone_score: Mapped[float] = mapped_column(Float, default=0.0)  # Tone analysis

    # Derived scores
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)  # Weighted overall score
    classification: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # hot, warm, cold

    # Conversation metrics
    conversation_length_seconds: Mapped[int] = mapped_column(Integer, default=0)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    user_message_count: Mapped[int] = mapped_column(Integer, default=0)
    assistant_message_count: Mapped[int] = mapped_column(Integer, default=0)

    # Objection tracking
    objection_count: Mapped[int] = mapped_column(Integer, default=0)
    objections_handled: Mapped[int] = mapped_column(Integer, default=0)
    objection_types: Mapped[Optional[Dict[str, int]]] = mapped_column(JSON, nullable=True)

    # Positive signals
    positive_signals: Mapped[int] = mapped_column(Integer, default=0)
    positive_keywords: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Language and communication quality
    language_consistency_score: Mapped[float] = mapped_column(Float, default=0.0)
    communication_clarity_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Scoring metadata
    scoring_model_version: Mapped[str] = mapped_column(String(20), default="v1.0")
    scoring_metadata: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    confidence_intervals: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    # Relationships
    lead = relationship("Lead", back_populates="scores")

    def __repr__(self):
        return f"<Scoring(id={self.id}, lead_id={self.lead_id}, overall_score={self.overall_score:.2f}, classification={self.classification})>"

    @property
    def is_hot(self) -> bool:
        """Check if scoring indicates hot lead."""
        return self.classification == "hot"

    @property
    def is_warm(self) -> bool:
        """Check if scoring indicates warm lead."""
        return self.classification == "warm"

    @property
    def is_cold(self) -> bool:
        """Check if scoring indicates cold lead."""
        return self.classification == "cold"

    @property
    def objection_resolution_rate(self) -> float:
        """Calculate objection resolution rate."""
        if self.objection_count == 0:
            return 1.0
        return self.objections_handled / self.objection_count

    @property
    def engagement_rate(self) -> float:
        """Calculate engagement rate based on message counts."""
        total_messages = self.user_message_count + self.assistant_message_count
        if total_messages == 0:
            return 0.0
        return self.user_message_count / total_messages

    def calculate_overall_score(self) -> float:
        """
        Calculate overall score using weighted components.

        Weights:
        - Intent: 40%
        - Engagement: 30%
        - Objection handling: 20%
        - Tone: 10%
        """
        weights = {
            'intent': 0.4,
            'engagement': 0.3,
            'objection': 0.2,
            'tone': 0.1
        }

        overall = (
            self.intent_score * weights['intent'] +
            self.engagement_score * weights['engagement'] +
            self.objection_score * weights['objection'] +
            self.tone_score * weights['tone']
        )

        self.overall_score = round(overall, 3)
        return self.overall_score

    def determine_classification(self) -> str:
        """
        Determine lead classification based on overall score.

        Returns:
            str: Classification (hot, warm, cold)
        """
        from app.core.config import settings

        if self.overall_score >= settings.HOT_LEAD_THRESHOLD:
            classification = "hot"
        elif self.overall_score >= settings.WARM_LEAD_THRESHOLD:
            classification = "warm"
        else:
            classification = "cold"

        self.classification = classification
        return classification