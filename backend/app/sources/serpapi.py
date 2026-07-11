"""SerpAPI adapter — primary web search."""
from app.core.config import get_settings
from app.core.http import request_json
from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter


class SerpAPISource(SourceAdapter):
    name = "serpapi"
    category = "web"

    def is_configured(self) -> bool:
        return bool(get_settings().serpapi_key)

    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        data = await request_json(
            "GET",
            "https://serpapi.com/search.json",
            params={
                "q": query,
                "engine": "google",
                "num": limit,
                "api_key": get_settings().serpapi_key,
            },
        )
        docs = []
        for item in data.get("organic_results", [])[:limit]:
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    content=item.get("snippet", ""),
                    metadata={"position": item.get("position")},
                )
            )
        return docs
