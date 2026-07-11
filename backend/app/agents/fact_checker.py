"""Fact Checker Agent — cross-source verification, conflict detection,
confidence scoring. Never trusts a single source."""
from app.agents.base import BaseAgent
from app.agents.state import PipelineState
from app.prompts.templates import FACT_CHECKER_PROMPT, FACT_CHECKER_SYSTEM
from app.utils.text import format_evidence


class FactCheckerAgent(BaseAgent):
    name = "fact_checker"

    async def run(self, state: PipelineState) -> dict:
        evidence = format_evidence(
            state.get("context_blocks", []), state.get("documents", []), max_chars=14000
        )
        distinct_sources = {
            b["metadata"].get("source", "?") for b in state.get("context_blocks", [])
        }

        raw = await self.ask_structured(
            FACT_CHECKER_PROMPT.format(topic=state["topic"], evidence=evidence),
            system=FACT_CHECKER_SYSTEM,
            max_tokens=4096,
        )

        overall = float(raw.get("overall", 50))
        # Guardrail: an LLM can't be >70% confident on single-source evidence.
        if len(distinct_sources) <= 1:
            overall = min(overall, 70.0)

        fact_check = {
            "claim_scores": raw.get("claim_scores", [])[:12],
            "conflicts": raw.get("conflicts", [])[:6],
            "overall": max(0.0, min(100.0, overall)),
            "rationale": raw.get("rationale", ""),
            "distinct_sources": sorted(distinct_sources),
        }
        self.logger.info(
            "fact_checker.done",
            overall=fact_check["overall"],
            conflicts=len(fact_check["conflicts"]),
            sources=len(distinct_sources),
        )
        return {"fact_check": fact_check}
