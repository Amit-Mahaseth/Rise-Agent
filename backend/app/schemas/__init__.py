"""
Pydantic schemas for RiseAgent AI.
"""

from app.schemas.conversation import (
    ConversationBase,
    ConversationCreate,
    ConversationResponse,
    ConversationSummary,
    ConversationThread,
    ConversationUpdate,
)
from app.schemas.lead import (
    LeadBase,
    LeadCreate,
    LeadCreateResponse,
    LeadResponse,
    LeadSummary,
    LeadUpdate,
    LeadWithStats,
)
from app.schemas.scoring import (
    LeadQualificationResult,
    ScoringBase,
    ScoringCreate,
    ScoringResponse,
    ScoringSummary,
    ScoringUpdate,
)

__all__ = [
    # Lead schemas
    "LeadBase",
    "LeadCreate",
    "LeadUpdate",
    "LeadResponse",
    "LeadSummary",
    "LeadWithStats",
    "LeadCreateResponse",

    # Conversation schemas
    "ConversationBase",
    "ConversationCreate",
    "ConversationUpdate",
    "ConversationResponse",
    "ConversationSummary",
    "ConversationThread",

    # Scoring schemas
    "ScoringBase",
    "ScoringCreate",
    "ScoringUpdate",
    "ScoringResponse",
    "ScoringSummary",
    "LeadQualificationResult",
]

