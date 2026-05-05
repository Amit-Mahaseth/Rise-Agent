"""
Pydantic schemas for Lead model.
Enhanced with comprehensive lead management fields.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class LeadBase(BaseModel):
    """Base schema for Lead with common fields."""
    lead_id: str = Field(..., min_length=3, max_length=64, description="Unique lead identifier")
    full_name: str = Field(..., min_length=2, max_length=120, description="Full name of the lead")
    phone_number: str = Field(..., min_length=8, max_length=24, description="Phone number with country code")
    email: Optional[str] = Field(None, description="Email address")
    source: str = Field("website", max_length=80, description="Lead source (website, referral, etc.)")
    product_interest: str = Field("personal-loan", max_length=80, description="Product of interest")
    initial_context: Optional[str] = Field(None, description="Initial lead context")
    notes: Optional[str] = Field(None, description="Additional notes")
    preferred_language: Optional[str] = Field(None, description="Preferred language code")
    communication_preference: str = Field("voice", description="Preferred communication method")


class LeadCreate(LeadBase):
    """Schema for creating a new lead."""
    pass


class LeadUpdate(BaseModel):
    """Schema for updating an existing lead."""
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    source: Optional[str] = None
    product_interest: Optional[str] = None
    initial_context: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    preferred_language: Optional[str] = None
    communication_preference: Optional[str] = None
    assigned_rm: Optional[str] = None
    classification: Optional[str] = None
    score: Optional[float] = None


class LeadResponse(LeadBase):
    """Schema for Lead API responses."""
    id: int
    status: str
    classification: Optional[str]
    score: Optional[float]
    assigned_rm: Optional[str]
    rm_handoff_reason: Optional[str]
    whatsapp_sent: bool
    whatsapp_link: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_contacted_at: Optional[datetime]
    qualified_at: Optional[datetime]
    converted_at: Optional[datetime]
    metadata: Optional[dict]

    model_config = ConfigDict(from_attributes=True)


class LeadSummary(BaseModel):
    """Simplified lead summary for listings."""
    id: int
    lead_id: str
    full_name: str
    phone_number: str
    status: str
    classification: Optional[str]
    score: Optional[float]
    created_at: datetime
    last_contacted_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class LeadWithStats(LeadResponse):
    """Lead with conversation and call statistics."""
    total_calls: int = 0
    total_conversations: int = 0
    last_call_duration: Optional[int] = None
    average_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class LeadCreateResponse(BaseModel):
    """Response for lead creation with call initiation."""
    lead: LeadResponse
    call_id: str
    message: str
    estimated_wait_time: int = Field(..., description="Estimated seconds until call starts")

