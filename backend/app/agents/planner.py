"""Planner Agent — decomposes a topic into a research plan."""
from app.agents.base import BaseAgent
from app.agents.state import PipelineState, ResearchPlan
from app.prompts.templates import PLANNER_PROMPT, PLANNER_SYSTEM

VALID_CATEGORIES = {"background", "web", "academic", "code", "ml", "data", "news", "medical"}


class PlannerAgent(BaseAgent):
    name = "planner"

    async def run(self, state: PipelineState) -> dict:
        topic = state["topic"]
        raw = await self.ask_structured(
            PLANNER_PROMPT.format(topic=topic, depth=state.get("depth", "standard")),
            system=PLANNER_SYSTEM,
        )

        categories = [
            c for c in raw.get("source_categories", []) if c in VALID_CATEGORIES
        ]
        plan: ResearchPlan = {
            "sub_questions": raw.get("sub_questions", [])[:6] or [topic],
            "search_queries": raw.get("search_queries", [])[:8] or [topic],
            # Always keep the foundational categories in play.
            "source_categories": sorted(
                set(categories) | {"background", "web", "academic", "news"}
            ),
            "key_entities": raw.get("key_entities", [])[:12],
        }
        if topic not in plan["search_queries"]:
            plan["search_queries"].insert(0, topic)

        self.logger.info(
            "planner.done",
            queries=len(plan["search_queries"]),
            categories=plan["source_categories"],
        )
        return {"plan": plan}
