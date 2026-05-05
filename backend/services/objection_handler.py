"""
Objection detection and rebuttal service.
Classifies lead statements as objections, retrieves rebuttals via RAG,
and tracks which objections have been handled to avoid repetition.
"""

from __future__ import annotations

import logging
from typing import Optional

from services.llm import get_llm_response
from config import get_settings
from prompts.system_prompt import build_objection_classification_prompt
from knowledge.loader import get_retriever

logger = logging.getLogger("riseagent.objections")

VALID_OBJECTIONS = {
    "already_with_broker",
    "no_contacts",
    "client_issues",
    "trust_concern",
    "not_interested_now",
}


class ObjectionTracker:
    """Tracks objections raised and rebuttals used during a call."""

    def __init__(self, previously_handled: list[str] | None = None):
        self.objections_raised: list[str] = []
        self.rebuttals_used: list[str] = []
        self.previously_handled: set[str] = set(previously_handled or [])

    def has_been_handled(self, objection_type: str) -> bool:
        """Check if this objection was already handled in current or previous calls."""
        return (
            objection_type in self.objections_raised
            or objection_type in self.previously_handled
        )

    def mark_handled(self, objection_type: str, rebuttal: str) -> None:
        """Mark an objection as handled with its rebuttal."""
        if objection_type not in self.objections_raised:
            self.objections_raised.append(objection_type)
        if rebuttal not in self.rebuttals_used:
            self.rebuttals_used.append(rebuttal)


async def classify_objection(lead_text: str) -> str:
    """
    Classify a lead's statement as an objection type.
    Returns one of the VALID_OBJECTIONS or 'none'.
    """
    try:
        prompt = build_objection_classification_prompt(lead_text)
        response_data = await get_llm_response(
            system_prompt="You are a helpful assistant that classifies lead statements into predefined objection types.",
            user_message=prompt
        )
        classification = response_data["text"].strip().lower().replace(" ", "_")

        if classification in VALID_OBJECTIONS:
            logger.info("Objection classified: %s", classification)
            return classification

        logger.debug("No objection detected in: %s", lead_text[:60])
        return "none"
    except Exception as exc:
        logger.error("Objection classification failed: %s", exc)
        return "none"


async def get_rebuttal(
    objection_type: str,
    tracker: ObjectionTracker,
) -> Optional[str]:
    """
    Get a rebuttal for an objection via RAG retrieval.

    If the objection has been handled before, returns a pivot message
    instead of repeating the same rebuttal.
    """
    if objection_type == "none" or objection_type not in VALID_OBJECTIONS:
        return None

    # Check if already handled
    if tracker.has_been_handled(objection_type):
        logger.info(
            "Objection '%s' already handled — pivoting instead of repeating",
            objection_type,
        )
        return _get_pivot_message(objection_type)

    # Retrieve rebuttal from knowledge base
    try:
        retriever = get_retriever(k=2)
        query = f"OBJECTION: {objection_type} REBUTTAL"
        docs = await retriever.ainvoke(query)

        if docs:
            # Find the most relevant rebuttal chunk
            for doc in docs:
                content = doc.page_content
                if "REBUTTAL:" in content:
                    # Extract rebuttal text
                    rebuttal_start = content.index("REBUTTAL:") + len("REBUTTAL:")
                    # Find end (next OBJECTION: or FOLLOW UP: or end of text)
                    rebuttal_text = content[rebuttal_start:].strip()
                    for marker in ["FOLLOW UP:", "OBJECTION:", "\n\n"]:
                        if marker in rebuttal_text:
                            rebuttal_text = rebuttal_text[:rebuttal_text.index(marker)].strip()
                    if rebuttal_text:
                        tracker.mark_handled(objection_type, rebuttal_text)
                        logger.info("Retrieved rebuttal for '%s'", objection_type)
                        return rebuttal_text

        # Fallback rebuttals
        fallback = _get_fallback_rebuttal(objection_type)
        tracker.mark_handled(objection_type, fallback)
        return fallback
    except Exception as exc:
        logger.error("Rebuttal retrieval failed: %s", exc)
        fallback = _get_fallback_rebuttal(objection_type)
        tracker.mark_handled(objection_type, fallback)
        return fallback


def _get_fallback_rebuttal(objection_type: str) -> str:
    """Fallback rebuttals in case RAG retrieval fails."""
    fallbacks = {
        "already_with_broker": (
            "That's great experience. Are you getting 100% brokerage share "
            "and daily payouts? Most brokers cap at 60-70% and pay monthly."
        ),
        "no_contacts": (
            "You don't need a large network to start. Rupeezy provides "
            "starter support and marketing materials. Even 2-3 clients "
            "can generate meaningful monthly income."
        ),
        "client_issues": (
            "You're not alone — Rupeezy's full support team handles client "
            "issues. You focus on relationships, they handle the backend."
        ),
        "trust_concern": (
            "Rupeezy is SEBI registered with thousands of active APs. "
            "You can verify everything on the RISE Portal before committing."
        ),
        "not_interested_now": (
            "Completely understand. Can I send you the details on WhatsApp? "
            "No commitment — just so you have it when the time feels right."
        ),
    }
    return fallbacks.get(objection_type, "I understand your concern. Let me address that.")


def _get_pivot_message(objection_type: str) -> str:
    """
    When an objection has already been handled, return a pivot message
    that acknowledges the concern without repeating the rebuttal.
    """
    pivots = {
        "already_with_broker": (
            "I hear you. Since you already have experience, you'd actually "
            "pick this up very quickly. The main difference is the payout structure."
        ),
        "no_contacts": (
            "I understand. Many of our APs started exactly where you are. "
            "Should I connect you with someone who can share their experience?"
        ),
        "client_issues": (
            "That's a valid concern. I can have our support team lead "
            "walk you through exactly how client management works."
        ),
        "trust_concern": (
            "Your caution is understandable. Would it help if I sent you "
            "some verified AP testimonials and our SEBI registration details?"
        ),
        "not_interested_now": (
            "Of course. I'll make a note and we won't follow up until "
            "you reach out. No pressure at all."
        ),
    }
    return pivots.get(objection_type, "I understand. Let me know if you have any other questions.")
