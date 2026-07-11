"""GNews adapter — latest news."""
from app.core.config import get_settings
from app.core.http import request_json
from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter


class GNewsSource(SourceAdapter):
    name = "gnews"
    category = "news"
    cache_ttl = 3600  # news should stay fresh

    def is_configured(self) -> bool:
        return bool(get_settings().gnews_api_key)

    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        data = await request_json(
            "GET",
            "https://gnews.io/api/v4/search",
            params={
                "q": query,
                "lang": "en",
                "max": min(limit, 10),
                "apikey": get_settings().gnews_api_key,
            },
        )
        docs = []
        for article in data.get("articles", [])[:limit]:
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=article.get("title", ""),
                    url=article.get("url", ""),
                    content=article.get("description") or article.get("content", ""),
                    metadata={
                        "published_at": article.get("publishedAt", ""),
                        "outlet": (article.get("source") or {}).get("name", ""),
                    },
                )
            )
        return docs
