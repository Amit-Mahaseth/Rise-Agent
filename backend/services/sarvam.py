"""
Sarvam AI STT + TTS wrapper.
Handles real-time speech-to-text and text-to-speech via Sarvam REST API.
"""

from __future__ import annotations

import base64
import logging
from typing import Optional

import httpx

from config import get_settings

logger = logging.getLogger("riseagent.sarvam")

SARVAM_BASE_URL = "https://api.sarvam.ai"


async def speech_to_text(
    audio_data: bytes,
    language_code: str = "hi-IN",
    model: str = "saarika:v2",
) -> dict:
    """
    Convert speech audio to text using Sarvam STT.

    Args:
        audio_data: Raw audio bytes (WAV/MP3)
        language_code: Language code e.g. hi-IN, en-IN, ta-IN
        model: STT model to use

    Returns:
        dict with 'transcript' and 'language_code' keys
    """
    settings = get_settings()
    audio_b64 = base64.b64encode(audio_data).decode("utf-8")

    headers = {
        "api-subscription-key": settings.sarvam_api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "audio": audio_b64,
        "language_code": language_code,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{SARVAM_BASE_URL}/speech-to-text",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            transcript = data.get("transcript", "")
            detected_lang = data.get("language_code", language_code)
            logger.info("STT result [%s]: %s", detected_lang, transcript[:80])
            return {
                "transcript": transcript,
                "language_code": detected_lang,
            }
    except httpx.HTTPStatusError as exc:
        logger.error("Sarvam STT HTTP error: %s — %s", exc.response.status_code, exc.response.text)
        raise
    except Exception as exc:
        logger.error("Sarvam STT error: %s", exc)
        raise


async def text_to_speech(
    text: str,
    target_language_code: str = "hi-IN",
    speaker: str = "meera",
    model: str = "bulbul:v1",
) -> bytes:
    """
    Convert text to speech audio using Sarvam TTS.

    Args:
        text: Text to synthesize
        target_language_code: Target language code
        speaker: Voice to use (meera, arvind, pavithra, mahi)
        model: TTS model to use

    Returns:
        Audio bytes (WAV format)
    """
    settings = get_settings()

    headers = {
        "api-subscription-key": settings.sarvam_api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": [text],
        "target_language_code": target_language_code,
        "speaker": speaker,
        "model": model,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{SARVAM_BASE_URL}/text-to-speech",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            # Sarvam returns base64-encoded audio in 'audios' array
            audios = data.get("audios", [])
            if audios:
                audio_bytes = base64.b64decode(audios[0])
                logger.info("TTS generated %d bytes for [%s]", len(audio_bytes), target_language_code)
                return audio_bytes
            logger.warning("Sarvam TTS returned empty audios array")
            return b""
    except httpx.HTTPStatusError as exc:
        logger.error("Sarvam TTS HTTP error: %s — %s", exc.response.status_code, exc.response.text)
        raise
    except Exception as exc:
        logger.error("Sarvam TTS error: %s", exc)
        raise


async def translate_text(
    text: str,
    source_language_code: str = "auto",
    target_language_code: str = "en-IN",
) -> dict:
    """
    Translate text and detect language using Sarvam Translate API.

    Returns:
        dict with 'translated_text', 'source_language', 'target_language'
    """
    settings = get_settings()

    headers = {
        "api-subscription-key": settings.sarvam_api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "input": text,
        "source_language_code": source_language_code,
        "target_language_code": target_language_code,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{SARVAM_BASE_URL}/translate",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info(
                "Translation [%s→%s]: %s",
                data.get("source_language_code", "?"),
                target_language_code,
                data.get("translated_text", "")[:60],
            )
            return {
                "translated_text": data.get("translated_text", ""),
                "source_language": data.get("source_language_code", source_language_code),
                "target_language": target_language_code,
            }
    except httpx.HTTPStatusError as exc:
        logger.error("Sarvam Translate HTTP error: %s — %s", exc.response.status_code, exc.response.text)
        raise
    except Exception as exc:
        logger.error("Sarvam Translate error: %s", exc)
        raise


def get_tts_speaker(language_code: str) -> str:
    """Select appropriate TTS speaker voice for a language."""
    speaker_map = {
        "hi-IN": "meera",
        "en-IN": "meera",
        "ta-IN": "pavithra",
        "te-IN": "mahi",
        "mr-IN": "meera",
        "gu-IN": "meera",
        "bn-IN": "meera",
    }
    return speaker_map.get(language_code, "meera")
