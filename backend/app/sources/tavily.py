"""Tavily adapter — AI-optimized search with answer extraction."""
from app.core.config import get_settings
from app.core.http import request_json
from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter


class TavilySource(SourceAdapter):
    name = "tavily"
    category = "web"

    def is_configured(self) -> bool:
        return bool(get_settings().tavily_api_key)

    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        data = await request_json(
            "POST",
            "https://api.tavily.com/search",
            json={
                "api_key": get_settings().tavily_api_key,
                "query": query,
                "search_depth": "advanced",
                "max_results": limit,
                "include_answer": True,
            },
        )
        docs = []
        if data.get("answer"):
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=f"Tavily answer: {query}",
                    content=data["answer"],
                    metadata={"kind": "answer"},
                )
            )
        for item in data.get("results", [])[:limit]:
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    metadata={"score": item.get("score")},
                )
            )
        return docs
