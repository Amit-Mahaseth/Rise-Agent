"""
Demo mode simulation engine.
Runs the full conversation pipeline with Claude, simulating lead responses
based on persona personality. No real phone calls needed.
"""

from __future__ import annotations

import json
import logging
import asyncio
import random
from pathlib import Path
from datetime import datetime, timezone

from services.llm import get_llm_response

from config import get_settings
from database import db_insert, db_update
from services.conversation import ConversationSession, generate_call_summary
from services.language import LanguageState, LANGUAGE_MAP
from services.objection_handler import ObjectionTracker, classify_objection, get_rebuttal
from services.memory import store_call_memory, retrieve_lead_memory, get_call_count
from services.scoring import score_lead
from services.rm_handoff import route_lead_post_call
from services.call_service import initiate_call, end_call
from prompts.system_prompt import build_lead_simulation_prompt

logger = logging.getLogger("riseagent.demo")

PERSONAS_FILE = Path(__file__).parent / "personas.json"


def load_personas() -> list[dict]:
    """Load demo personas from JSON file."""
    with open(PERSONAS_FILE, "r") as f:
        return json.load(f)


def get_persona_by_phone(phone: str) -> dict | None:
    """Find a persona matching the given phone number."""
    personas = load_personas()
    for p in personas:
        if p["phone"] == phone:
            return p
    return None


async def simulate_call(lead_id: str, persona: dict) -> dict:
    """
    Run a full simulated conversation for a demo persona.
    Returns the complete result with transcript, score, and routing action.
    """
    settings = get_settings()
    lead_name = persona["name"]
    language_code = persona["language"]
    personality = persona["personality"]
    planned_objections = persona["objections"]
    language_name = LANGUAGE_MAP.get(language_code, "English")

    logger.info("Starting demo simulation for %s [%s, %s]", lead_name, language_name, personality)

    # 1. Get lead memory from previous calls
    lead_memory = await retrieve_lead_memory(lead_id)
    call_number = await get_call_count(lead_id) + 1

    # 2. Create call record
    call_record = await initiate_call(lead_id, persona["phone"])
    call_id = call_record["id"]

    # 3. Initialize conversation session
    session = ConversationSession(
        lead_id=lead_id,
        lead_name=lead_name,
        language=language_name,
        lead_memory=lead_memory,
    )

    # 4. Initialize objection tracker
    objection_tracker = ObjectionTracker()
    language_state = LanguageState(initial_hint=language_code)

    # 5. Language state
    language_state = LanguageState(initial_hint=language_code)

    # 6. Run conversation loop
    # Determine number of turns based on personality
    max_turns = {"enthusiastic": 8, "interested": 7, "neutral": 6, "skeptical": 7, "disengaged": 5}
    num_turns = max_turns.get(personality, 6)

    # Agent opening
    # We don't get the provider from the get_opening() method directly right now,
    # but we added it to session.transcript. We can pull it from there.
    agent_text = await session.get_opening()
    opening_provider = session.transcript[-1].get("provider", "unknown")
    await _log_event(call_id, 1, "agent", agent_text, language_code, provider=opening_provider)

    interest_signals: list[str] = []
    all_events = [{"turn": 1, "speaker": "agent", "text": agent_text, "language": language_code}]
    start_time = datetime.now(timezone.utc)

    for turn in range(2, num_turns + 1):
        # Simulate lead response
        lead_prompt = build_lead_simulation_prompt(
            persona_name=lead_name,
            personality=personality,
            language=language_code,
            objections=planned_objections,
            turn_number=turn,
            agent_message=agent_text,
        )
        try:
            response_data = await get_llm_response(
                system_prompt="You are simulating a lead in a sales call. Respond briefly and naturally.",
                user_message=lead_prompt
            )
            lead_text = response_data["text"].strip()
            lead_provider = response_data["provider"]
        except Exception as exc:
            logger.error("Lead simulation failed: %s", exc)
            lead_text = "Hmm, okay."
            lead_provider = "none"

        await _log_event(call_id, turn, "lead", lead_text, language_code, provider=lead_provider)
        all_events.append({"turn": turn, "speaker": "lead", "text": lead_text, "language": language_code, "provider": lead_provider})

        # Detect objections
        objection_type = await classify_objection(lead_text)
        if objection_type != "none":
            rebuttal = await get_rebuttal(objection_type, objection_tracker)
            if rebuttal:
                logger.info("Objection [%s] → rebuttal injected", objection_type)

        # Check for interest signals
        lead_lower = lead_text.lower()
        for signal in ["interested", "tell me more", "sounds good", "yes", "haan", "bilkul"]:
            if signal in lead_lower and signal not in interest_signals:
                interest_signals.append(signal)

        # Agent response
        agent_text = await session.process_turn(lead_text)
        agent_provider = session.transcript[-1].get("provider", "unknown")
        turn_num = turn + 1
        await _log_event(call_id, turn_num, "agent", agent_text, language_code, provider=agent_provider)
        all_events.append({"turn": turn_num, "speaker": "agent", "text": agent_text, "language": language_code, "provider": agent_provider})

        # Small delay for realism
        await asyncio.sleep(0.1)

    # 7. End call
    end_time = datetime.now(timezone.utc)
    duration = max(30, int((end_time - start_time).total_seconds()) + random.randint(45, 180))
    await end_call(call_id, duration)

    # 8. Generate transcript and summary
    full_transcript = session.get_full_transcript()
    summary = await generate_call_summary(full_transcript)

    # 9. Score the lead
    score_result = await score_lead(
        lead_id=lead_id,
        call_id=call_id,
        transcript=full_transcript,
        objection_count=len(objection_tracker.objections_raised),
        duration_seconds=duration,
    )

    # 10. Store memory
    await store_call_memory(
        lead_id=lead_id,
        call_number=call_number,
        language_detected=language_code,
        objections_raised=objection_tracker.objections_raised,
        rebuttals_used=objection_tracker.rebuttals_used,
        interest_signals=interest_signals,
        conversation_summary=summary,
        classification=score_result["classification"],
    )

    # 11. Update lead record
    await db_update("leads", lead_id, {
        "language": language_code,
        "status": score_result["classification"],
    })

    # 12. Route based on score
    routing = await route_lead_post_call(
        lead_id=lead_id,
        lead_name=lead_name,
        lead_phone=persona["phone"],
        call_id=call_id,
        classification=score_result["classification"],
        score=score_result["total_score"],
        transcript=full_transcript,
        objections_raised=objection_tracker.objections_raised,
        rebuttals_used=objection_tracker.rebuttals_used,
        language=language_name,
    )

    logger.info(
        "Demo simulation complete: %s → %s (score: %d) → %s",
        lead_name, score_result["classification"],
        score_result["total_score"], routing["action"],
    )

    return {
        "lead_id": lead_id,
        "lead_name": lead_name,
        "call_id": call_id,
        "language": language_name,
        "duration_seconds": duration,
        "transcript": all_events,
        "summary": summary,
        "score": score_result,
        "routing": routing,
        "objections_raised": objection_tracker.objections_raised,
        "rebuttals_used": objection_tracker.rebuttals_used,
        "interest_signals": interest_signals,
    }


async def _log_event(call_id: str, turn: int, speaker: str, text: str, language: str, provider: str = None) -> None:
    """Log a conversation turn to the database."""
    try:
        event_data = {
            "call_id": call_id,
            "turn_number": turn,
            "speaker": speaker,
            "text": text,
            "language": language,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if provider:
            event_data["provider"] = provider

        await db_insert("call_events", event_data)
    except Exception as exc:
        logger.warning("Failed to log call event: %s", exc)
