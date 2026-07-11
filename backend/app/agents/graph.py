"""LangGraph research pipeline.

Planner → Research → Retriever → Fact Checker → Writer → Visualization
→ Podcast → Report Generator

Each node wraps its agent with retry + progress reporting. A progress
callback (async) receives (stage_name, percent) so the API layer can
stream job status without the graph knowing about persistence.
"""
from typing import Awaitable, Callable

from langgraph.graph import END, StateGraph
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

from app.agents.base import BaseAgent
from app.agents.fact_checker import FactCheckerAgent
from app.agents.planner import PlannerAgent
from app.agents.podcaster import PodcastAgent
from app.agents.reporter import ReportAgent
from app.agents.researcher import ResearchAgent
from app.agents.retriever import RetrieverAgent
from app.agents.state import PipelineState
from app.agents.visualizer import VisualizationAgent
from app.agents.writer import WriterAgent
from app.core.logging import get_logger

logger = get_logger("agents.graph")

ProgressCallback = Callable[[str, int], Awaitable[None]]

# (stage key, agent class, progress % when stage starts, retryable)
_STAGES: list[tuple[str, type[BaseAgent], int, bool]] = [
    ("planner", PlannerAgent, 5, True),
    ("researcher", ResearchAgent, 18, True),
    ("retriever", RetrieverAgent, 40, True),
    ("fact_checker", FactCheckerAgent, 55, True),
    ("writer", WriterAgent, 68, True),
    ("visualizer", VisualizationAgent, 80, False),  # agent degrades internally
    ("podcaster", PodcastAgent, 88, False),          # optional artifact
    ("reporter", ReportAgent, 95, True),
]


def build_research_graph(progress: ProgressCallback | None = None):
    """Compile the LangGraph pipeline. Agents are instantiated per graph
    build so each research run gets fresh agent memory."""

    graph = StateGraph(PipelineState)

    def make_node(stage: str, agent_cls: type[BaseAgent], percent: int, retryable: bool):
        agent = agent_cls()

        async def node(state: PipelineState) -> dict:
            if progress is not None:
                await progress(stage, percent)
            if not retryable:
                return await agent.run(state)
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(2),
                wait=wait_exponential(min=2, max=15),
                reraise=True,
            ):
                with attempt:
                    if attempt.retry_state.attempt_number > 1:
                        logger.warning("stage.retry", stage=stage)
                    return await agent.run(state)
            raise RuntimeError("unreachable")

        return node

    for stage, agent_cls, percent, retryable in _STAGES:
        graph.add_node(stage, make_node(stage, agent_cls, percent, retryable))

    graph.set_entry_point(_STAGES[0][0])
    for (current, *_), (nxt, *_) in zip(_STAGES, _STAGES[1:]):
        graph.add_edge(current, nxt)
    graph.add_edge(_STAGES[-1][0], END)

    return graph.compile()


async def run_research_pipeline(
    job_id: str,
    topic: str,
    depth: str = "standard",
    language: str = "en",
    progress: ProgressCallback | None = None,
) -> PipelineState:
    """Execute the full pipeline and return the final state."""
    pipeline = build_research_graph(progress)
    initial: PipelineState = {
        "job_id": job_id,
        "topic": topic,
        "depth": depth,
        "language": language,
        "errors": [],
    }
    final_state: PipelineState = await pipeline.ainvoke(initial)
    if progress is not None:
        await progress("completed", 100)
    return final_state
