"""Sarvam AI text-to-speech client (bulbul model, English + Hindi)."""
import base64

from app.core.config import get_settings
from app.core.exceptions import AudioGenerationError
from app.core.http import request_json
from app.core.logging import get_logger

logger = get_logger("audio.sarvam")

_LANGUAGE_CODES = {"en": "en-IN", "hi": "hi-IN"}
# Alternate voices so the two podcast hosts sound distinct.
_SPEAKERS = {"ALEX": "abhilash", "PRIYA": "anushka"}
_MAX_CHUNK = 450  # Sarvam per-request text limit ~500 chars


class SarvamTTS:
    def __init__(self) -> None:
        self._settings = get_settings()

    def is_configured(self) -> bool:
        return bool(self._settings.sarvam_api_key)

    async def synthesize(
        self, text: str, language: str = "en", speaker: str = "anushka"
    ) -> bytes:
        """Synthesize one passage; returns raw WAV bytes."""
        if not self.is_configured():
            raise AudioGenerationError("SARVAM_API_KEY not configured")

        audio_parts: list[bytes] = []
        for chunk in _split_text(text, _MAX_CHUNK):
            data = await request_json(
                "POST",
                "https://api.sarvam.ai/text-to-speech",
                json={
                    "text": chunk,
                    "target_language_code": _LANGUAGE_CODES.get(language, "en-IN"),
                    "speaker": speaker,
                    "model": "bulbul:v2",
                },
                headers={"api-subscription-key": self._settings.sarvam_api_key},
            )
            audios = data.get("audios") or []
            if not audios:
                raise AudioGenerationError("Sarvam returned no audio")
            audio_parts.extend(base64.b64decode(a) for a in audios)
        return _concat_wav(audio_parts)

    async def synthesize_dialogue(
        self, script: str, language: str = "en"
    ) -> bytes:
        """Synthesize an ALEX:/PRIYA: dialogue script with per-host voices."""
        parts: list[bytes] = []
        for line in script.splitlines():
            line = line.strip()
            if not line:
                continue
            speaker_name, _, content = line.partition(":")
            speaker = _SPEAKERS.get(speaker_name.strip().upper())
            if speaker is None or not content.strip():
                continue
            parts.append(
                await self.synthesize(content.strip(), language, speaker)
            )
        if not parts:
            raise AudioGenerationError("no dialogue lines synthesized")
        return _concat_wav(parts)


def _split_text(text: str, limit: int) -> list[str]:
    words = text.split()
    chunks, current = [], ""
    for word in words:
        if current and len(current) + len(word) + 1 > limit:
            chunks.append(current)
            current = word
        else:
            current = f"{current} {word}" if current else word
    if current:
        chunks.append(current)
    return chunks


def _concat_wav(parts: list[bytes]) -> bytes:
    """Concatenate WAV files (same format) by stripping headers after the first."""
    if len(parts) == 1:
        return parts[0]
    import io
    import wave

    output = io.BytesIO()
    with wave.open(io.BytesIO(parts[0]), "rb") as first:
        params = first.getparams()
        frames = [first.readframes(first.getnframes())]
    for part in parts[1:]:
        with wave.open(io.BytesIO(part), "rb") as w:
            frames.append(w.readframes(w.getnframes()))
    with wave.open(output, "wb") as out:
        out.setparams(params)
        for frame in frames:
            out.writeframes(frame)
    return output.getvalue()
