"""
Lead model for RiseAgent AI.
Enhanced with comprehensive lead tracking and qualification features.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base
from app.utils.time import utcnow


class Lead(Base):
    """
    Lead model representing potential customers with comprehensive tracking.
    """
    __tablename__ = "leads"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Unique lead identifier
    lead_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    # Basic information
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Lead source and context
    source: Mapped[str] = mapped_column(String(80), nullable=False, default="website")
    product_interest: Mapped[str] = mapped_column(String(80), nullable=False, default="personal-loan")
    initial_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status and classification
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="new")
    classification: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # hot, warm, cold
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Language and communication preferences
    language: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    preferred_language: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    communication_preference: Mapped[str] = mapped_column(String(20), default="voice")  # voice, whatsapp, sms

    # Assignment and follow-up
    assigned_rm: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    rm_handoff_reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # WhatsApp follow-up
    whatsapp_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    whatsapp_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    qualified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Metadata
    extra_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    conversations = relationship("Conversation", back_populates="lead", cascade="all, delete-orphan")
    calls = relationship("CallRecord", back_populates="lead", cascade="all, delete-orphan")
    scores = relationship("Scoring", back_populates="lead", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lead(id={self.id}, lead_id={self.lead_id}, name={self.full_name}, status={self.status}, classification={self.classification})>"

    @property
    def is_hot(self) -> bool:
        """Check if lead is classified as hot."""
        return self.classification == "hot"

    @property
    def is_warm(self) -> bool:
        """Check if lead is classified as warm."""
        return self.classification == "warm"

    @property
    def is_cold(self) -> bool:
        """Check if lead is classified as cold."""
        return self.classification == "cold"

    @property
    def days_since_creation(self) -> int:
        """Calculate days since lead creation."""
        return (datetime.utcnow() - self.created_at).days

    @property
    def days_since_last_contact(self) -> Optional[int]:
        """Calculate days since last contact."""
        if self.last_contacted_at:
            return (datetime.utcnow() - self.last_contacted_at).days
        return None

    @property
    def lead_metadata(self) -> Optional[dict]:
        """Compatibility accessor for business metadata attached to a lead."""
        return self.extra_metadata
