"""
Conversation model for RiseAgent AI.
Stores chat history and conversation context per lead.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base
from app.utils.time import utcnow


class Conversation(Base):
    """
    Conversation model storing individual messages and context.
    """
    __tablename__ = "conversations"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key to lead
    lead_id: Mapped[str] = mapped_column(String(64), ForeignKey("leads.lead_id"), nullable=False, index=True)

    # Session and message details
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    message_id: Mapped[str] = mapped_column(String(64), default=lambda: str(uuid.uuid4()), unique=True)
    message_type: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Language and processing
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    language_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Analysis results
    intent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    intent_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sentiment: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # positive, negative, neutral
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Objections
    objection_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    objection_handled: Mapped[bool] = mapped_column(default=False)

    # Audio metadata (for voice messages)
    audio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    transcription_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Response metadata
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Context and memory
    context_window: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    memory_retrieved: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Timestamps
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    # Relationships
    lead = relationship("Lead", back_populates="conversations")

    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id={self.session_id}, type={self.message_type}, intent={self.intent})>"

    @property
    def is_user_message(self) -> bool:
        """Check if this is a user message."""
        return self.message_type == "user"

    @property
    def is_assistant_message(self) -> bool:
        """Check if this is an assistant message."""
        return self.message_type == "assistant"

    @property
    def is_system_message(self) -> bool:
        """Check if this is a system message."""
        return self.message_type == "system"

    @property
    def has_objection(self) -> bool:
        """Check if message contains an objection."""
        return self.objection_type is not None

    @property
    def word_count(self) -> int:
        """Get word count of the message."""
        return len(self.content.split()) if self.content else 0