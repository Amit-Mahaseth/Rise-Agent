from collections.abc import AsyncGenerator


class STTService:
    async def stream_audio_to_text(self, audio_chunk: bytes) -> AsyncGenerator[dict, None]:
        text = audio_chunk.decode("utf-8", errors="ignore").strip() or "[audio]"
        # Rough energy estimate used by hybrid turn detection.
        avg_energy = sum(abs(b - 128) for b in audio_chunk[:400]) / max(1, min(len(audio_chunk), 400))
        confidence = self._estimate_confidence(text, avg_energy)
        stride = max(1, len(text) // 3)
        cursor = stride
        while cursor < len(text):
            partial_text = text[:cursor]
            yield {
                "type": "partial",
                "text": partial_text,
                "confidence": round(max(0.25, confidence - 0.15), 3),
                "audio_energy": round(avg_energy, 3),
            }
            cursor += stride
        yield {
            "type": "final",
            "text": text,
            "confidence": round(confidence, 3),
            "audio_energy": round(avg_energy, 3),
        }

    def _estimate_confidence(self, text: str, avg_energy: float) -> float:
        # Lightweight confidence heuristic for low-latency pipelines.
        if not text:
            return 0.3
        token_count = len(text.split())
        confidence = 0.45
        if token_count >= 4:
            confidence += 0.25
        if any(ch in text for ch in ".?!"):
            confidence += 0.12
        if avg_energy > 3.0:
            confidence += 0.1
        return min(confidence, 0.95)
