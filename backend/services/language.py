"""
Language detection and switching service.
Uses Sarvam Translate API for detection and maintains language state per lead.
"""

from __future__ import annotations

import logging
from typing import Optional

from services.sarvam import translate_text, get_tts_speaker

logger = logging.getLogger("riseagent.language")

# Language code → human-readable name mapping
LANGUAGE_MAP = {
    "hi-IN": "Hindi",
    "en-IN": "English",
    "ta-IN": "Tamil",
    "te-IN": "Telugu",
    "mr-IN": "Marathi",
    "gu-IN": "Gujarati",
    "bn-IN": "Bengali",
}

# Reverse map for detection
NAME_TO_CODE = {v.lower(): k for k, v in LANGUAGE_MAP.items()}
NAME_TO_CODE.update({
    "hindi": "hi-IN",
    "english": "en-IN",
    "tamil": "ta-IN",
    "telugu": "te-IN",
    "marathi": "mr-IN",
    "gujarati": "gu-IN",
    "bengali": "bn-IN",
    "hinglish": "hi-IN",
})


class LanguageState:
    """Tracks language for a single call session."""

    def __init__(self, initial_hint: Optional[str] = None):
        self.current_language: str = initial_hint or "hi-IN"
        self.detected_count: int = 0
        self.is_code_mixed: bool = False
        self.history: list[str] = []

    @property
    def language_name(self) -> str:
        return LANGUAGE_MAP.get(self.current_language, "Hindi")

    @property
    def tts_speaker(self) -> str:
        return get_tts_speaker(self.current_language)

    def to_dict(self) -> dict:
        return {
            "current_language": self.current_language,
            "language_name": self.language_name,
            "is_code_mixed": self.is_code_mixed,
            "detection_count": self.detected_count,
        }


async def detect_language(text: str) -> str:
    """
    Detect the language of a text using Sarvam Translate API.
    Returns language code like 'hi-IN', 'en-IN', etc.
    """
    if not text or len(text.strip()) < 3:
        return "hi-IN"

    try:
        result = await translate_text(
            text=text,
            source_language_code="auto",
            target_language_code="en-IN",
        )
        detected = result.get("source_language", "hi-IN")
        # Normalize the language code
        if detected in LANGUAGE_MAP:
            return detected
        # Try to match partial codes
        for code in LANGUAGE_MAP:
            if detected.startswith(code[:2]):
                return code
        return "hi-IN"
    except Exception as exc:
        logger.warning("Language detection failed, defaulting to hi-IN: %s", exc)
        return "hi-IN"


async def update_language_state(
    state: LanguageState,
    transcript_text: str,
) -> bool:
    """
    Update language state based on new transcript.
    Returns True if language switched.
    """
    if not transcript_text.strip():
        return False

    detected = await detect_language(transcript_text)
    state.detected_count += 1
    state.history.append(detected)

    # Check for Hinglish (code-mixing)
    if _is_hinglish(transcript_text):
        state.is_code_mixed = True
        detected = "hi-IN"

    if detected != state.current_language:
        old_lang = state.current_language
        state.current_language = detected
        logger.info(
            "Language switch detected: %s → %s",
            LANGUAGE_MAP.get(old_lang, old_lang),
            LANGUAGE_MAP.get(detected, detected),
        )
        return True

    return False


def _is_hinglish(text: str) -> bool:
    """
    Heuristic check for Hinglish (Hindi-English code-mixing).
    Checks if text contains both Devanagari and Latin script.
    """
    has_devanagari = any("\u0900" <= ch <= "\u097F" for ch in text)
    has_latin = any("a" <= ch.lower() <= "z" for ch in text)
    return has_devanagari and has_latin


def get_language_code(hint: Optional[str]) -> str:
    """Normalize a language hint to a standard code."""
    if not hint:
        return "hi-IN"
    hint_lower = hint.lower().strip()
    if hint_lower in NAME_TO_CODE:
        return NAME_TO_CODE[hint_lower]
    if hint_lower in LANGUAGE_MAP:
        return hint_lower
    return "hi-IN"
