"""
Lead scoring engine.
Weighted signal scoring to classify leads as Hot / Warm / Cold.
"""

from __future__ import annotations

import logging
import re

from services.llm import get_llm_response
from config import get_settings
from prompts.system_prompt import build_tone_analysis_prompt
from database import db_insert

logger = logging.getLogger("riseagent.scoring")

# ── Intent detection phrases ──────────────────────────────────────
INTENT_PHRASES_EN = [
    "interested", "tell me more", "how do i join", "sounds good",
    "yes", "sign me up", "let's do it", "count me in",
    "i want to", "i'd like to",
]
INTENT_PHRASES_HI = [
    "haan", "bilkul", "zaroor", "batao", "aur batao",
    "mujhe interest hai", "theek hai", "kaise join karu",
    "accha lagta hai", "haan ji",
]
ALL_INTENT_PHRASES = INTENT_PHRASES_EN + INTENT_PHRASES_HI

# ── Network detection phrases ────────────────────────────────────
NETWORK_PHRASES = [
    "contacts", "clients", "friends", "log", "network",
    "people", "colleagues", "family", "dost", "parichit",
    "jaan-pehchaan", "circle",
]


async def score_lead(
    lead_id: str,
    call_id: str,
    transcript: str,
    objection_count: int,
    duration_seconds: int,
) -> dict:
    """
    Score a lead based on the call and return full breakdown.

    Signals and weights:
    - verbal_intent_detected: +40 points
    - objection_count: -10 per objection (max -40)
    - call_duration: 0 / +10 / +25
    - network_mentioned: +15
    - tone_score (0-2): tone * 5 points

    Classification:
    - >= 70 → HOT
    - 35-69 → WARM
    - < 35 → COLD
    """
    transcript_lower = transcript.lower()

    # ── Signal 1: Verbal intent ──────────────────────────────────
    verbal_intent = _detect_verbal_intent(transcript_lower)
    verbal_intent_points = 40 if verbal_intent else 0

    # ── Signal 2: Objection penalty ──────────────────────────────
    objection_points = min(objection_count * 10, 40) * -1

    # ── Signal 3: Duration score ─────────────────────────────────
    if duration_seconds < 30:
        duration_points = 0
    elif duration_seconds <= 90:
        duration_points = 10
    else:
        duration_points = 25

    # ── Signal 4: Network mentioned ──────────────────────────────
    network_mentioned = _detect_network_mention(transcript_lower)
    network_points = 15 if network_mentioned else 0

    # ── Signal 5: Tone analysis ──────────────────────────────────
    tone_score = await _analyze_tone(transcript)
    tone_points = tone_score * 5

    # ── Total score ──────────────────────────────────────────────
    total_score = max(0, min(100,
        verbal_intent_points
        + objection_points
        + duration_points
        + network_points
        + tone_points
    ))

    # ── Classification ───────────────────────────────────────────
    if total_score >= 70:
        classification = "hot"
    elif total_score >= 35:
        classification = "warm"
    else:
        classification = "cold"

    # ── Build breakdown ──────────────────────────────────────────
    breakdown = {
        "lead_id": lead_id,
        "call_id": call_id,
        "total_score": total_score,
        "verbal_intent": verbal_intent,
        "objection_count": objection_count,
        "duration_score": duration_points,
        "network_mentioned": network_mentioned,
        "tone_score": tone_score,
        "classification": classification,
    }

    # ── Persist to database ──────────────────────────────────────
    try:
        await db_insert("scores", breakdown.copy())
        logger.info(
            "Lead %s scored: %d [%s] (intent=%s, obj=%d, dur=%d, net=%s, tone=%d)",
            lead_id, total_score, classification,
            verbal_intent, objection_count, duration_seconds,
            network_mentioned, tone_score,
        )
    except Exception as exc:
        logger.error("Failed to persist score for lead %s: %s", lead_id, exc)

    # Add display-friendly points to breakdown
    breakdown["verbal_intent_points"] = verbal_intent_points
    breakdown["objection_points"] = objection_points
    breakdown["duration_points"] = duration_points
    breakdown["duration_seconds"] = duration_seconds
    breakdown["network_points"] = network_points
    breakdown["tone_points"] = tone_points

    return breakdown


def _detect_verbal_intent(transcript_lower: str) -> bool:
    """Check if the lead expressed verbal interest."""
    for phrase in ALL_INTENT_PHRASES:
        if phrase in transcript_lower:
            return True
    return False


def _detect_network_mention(transcript_lower: str) -> bool:
    """Check if the lead mentioned having contacts/network."""
    for phrase in NETWORK_PHRASES:
        if phrase in transcript_lower:
            return True
    return False


async def _analyze_tone(transcript: str) -> int:
    """Use the LLM router to rate lead's engagement tone (0-2)."""
    try:
        prompt = build_tone_analysis_prompt(transcript)
        response_data = await get_llm_response(
            system_prompt="You are a helpful assistant that analyzes call transcripts for lead engagement tone.",
            user_message=prompt
        )
        tone_text = response_data["text"].strip()

        # Extract digit
        match = re.search(r"[012]", tone_text)
        if match:
            return int(match.group())
        return 1  # Default neutral
    except Exception as exc:
        logger.error("Tone analysis failed: %s", exc)
        return 1  # Default neutral
