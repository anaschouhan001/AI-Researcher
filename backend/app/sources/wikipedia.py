"""Wikipedia adapter — background, history, definitions.

Two-step retrieval (no API key required):
1. MediaWiki search API finds the best-matching page titles for the
   query (an exact-title lookup alone fails for compound topics like
   "Quantum Computing in Healthcare").
2. `wikipedia-api` loads each page's summary and section structure.
"""
import asyncio

from app.core.http import request_json
from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter


class WikipediaSource(SourceAdapter):
    name = "wikipedia"
    category = "background"

    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        titles = await self._search_titles(query, limit)
        if not titles:
            titles = [query]  # fall back to an exact-title attempt
        return await asyncio.to_thread(self._load_pages, titles, limit)

    @staticmethod
    async def _search_titles(query: str, limit: int) -> list[str]:
        data = await request_json(
            "GET",
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": limit,
                "format": "json",
            },
        )
        return [
            item["title"] for item in data.get("query", {}).get("search", [])
        ]

    def _load_pages(self, titles: list[str], limit: int) -> list[SourceDocument]:
        import wikipediaapi

        wiki = wikipediaapi.Wikipedia(
            user_agent="ResearchGPT/1.0 (research assistant)", language="en"
        )
        docs: list[SourceDocument] = []
        for title in titles[:limit]:
            page = wiki.page(title)
            if not page.exists() or not page.summary:
                continue
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=page.title,
                    url=page.fullurl,
                    content=page.summary[:4000],
                    metadata={"sections": [s.title for s in page.sections[:10]]},
                )
            )
        return docs
