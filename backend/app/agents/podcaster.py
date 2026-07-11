"""Podcast Agent — writes a two-host script and voices it with Sarvam AI."""
from pathlib import Path

from app.agents.base import BaseAgent
from app.agents.state import PipelineState
from app.audio.sarvam import SarvamTTS
from app.core.config import get_settings
from app.prompts.templates import PODCAST_PROMPT, PODCAST_SYSTEM

_LANG_NAMES = {"en": "English", "hi": "Hindi"}


class PodcastAgent(BaseAgent):
    name = "podcaster"

    async def run(self, state: PipelineState) -> dict:
        tts = SarvamTTS()
        if not tts.is_configured():
            self.logger.info("podcaster.skipped", reason="no SARVAM_API_KEY")
            return {"podcast_path": ""}

        draft = state.get("draft", {})
        language = state.get("language", "en")
        try:
            script = await self.ask(
                PODCAST_PROMPT.format(
                    topic=state["topic"],
                    language=language,
                    language_name=_LANG_NAMES.get(language, "English"),
                    summary=draft.get("executive_summary", "")[:2000],
                    insights="\n".join(draft.get("key_insights", [])[:8]),
                ),
                system=PODCAST_SYSTEM,
                temperature=0.7,
                max_tokens=2048,
            )
            audio = await tts.synthesize_dialogue(script, language)

            storage = get_settings().storage_path / state["job_id"]
            storage.mkdir(parents=True, exist_ok=True)
            path = storage / f"podcast_{language}.wav"
            path.write_bytes(audio)
            (storage / f"podcast_{language}.txt").write_text(
                script, encoding="utf-8"
            )
            self.logger.info("podcaster.done", path=str(path), bytes=len(audio))
            return {"podcast_path": str(path)}
        except Exception as exc:
            # Podcast is a bonus artifact; never fail the run over it.
            self.logger.error("podcaster.failed", error=str(exc))
            return {"podcast_path": ""}
