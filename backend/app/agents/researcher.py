"""Research Agent — fans queries out across all relevant source adapters
concurrently and normalizes the evidence pool."""
import asyncio

from app.agents.base import BaseAgent
from app.agents.state import PipelineState
from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter
from app.sources.registry import sources_by_category

_DEPTH_LIMITS = {"quick": 4, "standard": 8, "deep": 14}


class ResearchAgent(BaseAgent):
    name = "researcher"

    async def run(self, state: PipelineState) -> dict:
        plan = state["plan"]
        limit = _DEPTH_LIMITS.get(state.get("depth", "standard"), 8)
        adapters = sources_by_category(plan["source_categories"])

        # Web/news adapters benefit from query diversity; heavier academic
        # APIs get only the primary topic to respect rate limits.
        tasks: list[asyncio.Task] = []
        for adapter in adapters:
            queries = self._queries_for(adapter, state["topic"], plan["search_queries"])
            for query in queries:
                tasks.append(asyncio.create_task(adapter.search(query, limit)))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        documents: list[SourceDocument] = []
        seen: set[str] = set()
        for result in results:
            if isinstance(result, Exception):
                self.logger.error("researcher.task_failed", error=str(result))
                continue
            for doc in result:
                key = doc.url or f"{doc.source}:{doc.title}"
                if key in seen or not (doc.content or doc.title):
                    continue
                seen.add(key)
                documents.append(doc)

        self.logger.info(
            "researcher.done",
            documents=len(documents),
            sources=sorted({d.source for d in documents}),
        )
        return {"documents": documents}

    @staticmethod
    def _queries_for(
        adapter: SourceAdapter, topic: str, queries: list[str]
    ) -> list[str]:
        if adapter.category in ("web", "news"):
            return queries[:3]
        return [topic]
