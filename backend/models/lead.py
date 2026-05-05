"""Lead Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LeadCreate(BaseModel):
    """Payload for POST /leads/new."""
    name: str = Field(..., min_length=1, max_length=200, description="Lead's full name")
    phone: str = Field(..., pattern=r"^\+?\d{10,15}$", description="Phone number with optional country code")
    language_hint: Optional[str] = Field(default=None, description="Optional language hint e.g. hi-IN")
    source: Optional[str] = Field(default="manual", description="Lead source e.g. landing-page, referral")


class LeadResponse(BaseModel):
    """Lead as returned from API."""
    id: str
    name: str
    phone: str
    language: str = "unknown"
    source: Optional[str] = None
    status: str = "pending"
    created_at: Optional[str] = None
    re_engage_after: Optional[str] = None


class LeadListResponse(BaseModel):
    """Paginated lead list."""
    leads: list[LeadResponse]
    total: int
