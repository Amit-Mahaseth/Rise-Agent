"""
Sarvam AI client for STT and TTS services.
"""

from typing import Optional, List
import aiohttp
import structlog

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SarvamClient:
    """
    Client for Sarvam AI STT and TTS services.
    """

    def __init__(self):
        self.api_key = settings.sarvam_api_key
        self.base_url = settings.sarvam_base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def speech_to_text(
        self,
        audio_data: bytes,
        language: str = "en"
    ) -> Optional[str]:
        """
        Convert speech to text.

        Args:
            audio_data: Raw audio bytes
            language: Language code

        Returns:
            Transcribed text or None
        """
        await self._ensure_session()

        try:
            # Prepare request
            url = f"{self.base_url}/speech-to-text"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "audio/wav"
            }

            data = aiohttp.FormData()
            data.add_field('audio', audio_data, filename='audio.wav')
            data.add_field('language', language)

            async with self.session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    transcription = result.get('transcription', '')
                    logger.debug(
                        "STT successful",
                        language=language,
                        text_length=len(transcription)
                    )
                    return transcription
                else:
                    logger.error(
                        "STT failed",
                        status=response.status,
                        response=await response.text()
                    )
                    return None

        except Exception as e:
            logger.error("STT error", error=str(e), language=language)
            return None

    async def text_to_speech(
        self,
        text: str,
        language: str = "en"
    ) -> Optional[bytes]:
        """
        Convert text to speech.

        Args:
            text: Text to convert
            language: Language code

        Returns:
            Audio bytes or None
        """
        await self._ensure_session()

        try:
            # Prepare request
            url = f"{self.base_url}/text-to-speech"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "text": text,
                "language": language,
                "voice": self._get_voice_for_language(language)
            }

            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    logger.debug(
                        "TTS successful",
                        language=language,
                        text_length=len(text),
                        audio_size=len(audio_data)
                    )
                    return audio_data
                else:
                    logger.error(
                        "TTS failed",
                        status=response.status,
                        response=await response.text()
                    )
                    return None

        except Exception as e:
            logger.error("TTS error", error=str(e), language=language)
            return None

    async def detect_language(self, audio_data: bytes) -> Optional[str]:
        """
        Detect language from audio sample.

        Args:
            audio_data: Audio bytes

        Returns:
            Detected language code or None
        """
        await self._ensure_session()

        try:
            # Prepare request
            url = f"{self.base_url}/language-detection"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "audio/wav"
            }

            data = aiohttp.FormData()
            data.add_field('audio', audio_data, filename='audio.wav')

            async with self.session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    detected_lang = result.get('language')
                    confidence = result.get('confidence', 0)

                    if confidence > 0.7:  # Confidence threshold
                        logger.debug(
                            "Language detected",
                            language=detected_lang,
                            confidence=confidence
                        )
                        return detected_lang

                logger.warning(
                    "Language detection failed or low confidence",
                    status=response.status
                )
                return None

        except Exception as e:
            logger.error("Language detection error", error=str(e))
            return None

    def _get_voice_for_language(self, language: str) -> str:
        """
        Get appropriate voice for language.

        Args:
            language: Language code

        Returns:
            Voice identifier
        """
        voice_map = {
            "en": "en-US-Neural2-D",
            "hi": "hi-IN-Neural2-D",
            "mr": "mr-IN-Neural2-D",
            "ta": "ta-IN-Neural2-D",
            "te": "te-IN-Neural2-D",
            "gu": "gu-IN-Neural2-D",
            "bn": "bn-IN-Neural2-D",
        }

        return voice_map.get(language, "en-US-Neural2-D")

    async def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages.

        Returns:
            List of language codes
        """
        # Return configured supported languages
        return settings.SUPPORTED_LANGUAGES

    async def health_check(self) -> bool:
        """
        Check if Sarvam API is accessible.

        Returns:
            True if healthy
        """
        await self._ensure_session()

        try:
            url = f"{self.base_url}/health"
            async with self.session.get(url) as response:
                return response.status == 200
        except Exception:
            return False