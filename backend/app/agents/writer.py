"""Writer Agent — produces the cited report, summary, insights, timeline."""
import json

from app.agents.base import BaseAgent
from app.agents.state import PipelineState
from app.prompts.templates import WRITER_PROMPT, WRITER_SYSTEM
from app.utils.text import format_evidence

_LANG_NAMES = {"en": "English", "hi": "Hindi"}


class WriterAgent(BaseAgent):
    name = "writer"

    async def run(self, state: PipelineState) -> dict:
        fact_check = state.get("fact_check", {})
        fact_summary = json.dumps(
            {
                "overall_confidence": fact_check.get("overall"),
                "verified_claims": fact_check.get("claim_scores", [])[:8],
                "conflicts": fact_check.get("conflicts", []),
            },
            indent=2,
        )
        evidence = format_evidence(
            state.get("context_blocks", []), state.get("documents", []), max_chars=16000
        )

        draft = await self.ask_structured(
            WRITER_PROMPT.format(
                topic=state["topic"],
                language=_LANG_NAMES.get(state.get("language", "en"), "English"),
                fact_summary=fact_summary,
                evidence=evidence,
            ),
            system=WRITER_SYSTEM,
            max_tokens=8192,
            temperature=0.4,
        )
        self.logger.info(
            "writer.done",
            report_chars=len(draft.get("report_markdown", "")),
            insights=len(draft.get("key_insights", [])),
        )
        return {"draft": draft}
