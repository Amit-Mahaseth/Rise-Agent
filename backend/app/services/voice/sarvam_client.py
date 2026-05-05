import logging

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)

VOICE_BY_LANGUAGE = {
    "Hindi": "meera",
    "English": "arya",
    "Hinglish": "meera",
    "Marathi": "meera",
    "Tamil": "anika",
    "Telugu": "arjun",
    "Gujarati": "meera",
    "Bengali": "anika",
}


class SarvamVoiceClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def synthesize(self, text: str, language: str) -> dict | None:
        if not self.settings.sarvam_api_key:
            return {
                "provider": "sarvam",
                "mode": "text-only",
                "language": language,
                "text": text,
            }

        payload = {
            "text": text,
            "language": language.lower(),
            "voice": VOICE_BY_LANGUAGE.get(language, "arya"),
        }
        headers = {"Authorization": f"Bearer {self.settings.sarvam_api_key}"}
        endpoint = f"{self.settings.sarvam_base_url}{self.settings.sarvam_tts_endpoint}"

        try:
            response = httpx.post(endpoint, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.warning("Sarvam TTS failed: %s", exc)
            return None

