"""
Pydantic schemas for Conversation model.
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict


class ConversationBase(BaseModel):
    """Base schema for Conversation."""
    lead_id: str = Field(..., description="Lead identifier")
    session_id: str = Field(..., description="Conversation session identifier")
    message_type: str = Field(..., description="Message type (user, assistant, system)")
    content: str = Field(..., description="Message content")


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation message."""
    language: Optional[str] = None
    audio_url: Optional[str] = None


class ConversationUpdate(BaseModel):
    """Schema for updating conversation message."""
    content: Optional[str] = None
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    objection_type: Optional[str] = None
    objection_handled: Optional[bool] = None


class ConversationResponse(ConversationBase):
    """Schema for Conversation API responses."""
    id: int
    message_id: str
    language: Optional[str]
    language_confidence: Optional[float]
    intent: Optional[str]
    intent_confidence: Optional[float]
    sentiment: Optional[str]
    sentiment_score: Optional[float]
    objection_type: Optional[str]
    objection_handled: bool
    audio_url: Optional[str]
    transcription_confidence: Optional[float]
    response_time_ms: Optional[int]
    tokens_used: Optional[int]
    context_window: Optional[Dict]
    memory_retrieved: Optional[List]
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationSummary(BaseModel):
    """Simplified conversation summary."""
    session_id: str
    message_count: int
    user_messages: int
    assistant_messages: int
    objection_count: int
    average_response_time_ms: Optional[float]
    languages_used: List[str]
    last_message_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationThread(BaseModel):
    """Conversation thread with messages."""
    session_id: str
    lead_id: str
    messages: List[ConversationResponse]
    summary: ConversationSummary

    model_config = ConfigDict(from_attributes=True)