from collections.abc import AsyncGenerator


class TTSService:
    async def text_to_speech_stream(
        self,
        text: str,
        language: str,
        speed: float = 1.0,
    ) -> AsyncGenerator[bytes, None]:
        # Audio cleanup + shaping at text payload level for simulated stream.
        cleaned = self._cleanup_text(text)
        payload = f"{language}|speed={round(speed, 2)}:{cleaned}".encode("utf-8")
        chunk_size = 96
        for idx in range(0, len(payload), chunk_size):
            chunk = payload[idx : idx + chunk_size]
            # Trim transport-level silence markers if present.
            chunk = chunk.strip()
            if chunk:
                yield chunk

    def _cleanup_text(self, text: str) -> str:
        compact = " ".join((text or "").split())
        # Avoid repeated punctuation bursts that sound robotic.
        while ".." in compact:
            compact = compact.replace("..", ".")
        compact = compact.replace(" ,", ",").replace(" .", ".")
        return compact.strip()
