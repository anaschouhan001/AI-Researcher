"""NewsAPI adapter — alternative news source."""
from app.core.config import get_settings
from app.core.http import request_json
from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter


class NewsAPISource(SourceAdapter):
    name = "newsapi"
    category = "news"
    cache_ttl = 3600

    def is_configured(self) -> bool:
        return bool(get_settings().news_api_key)

    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        data = await request_json(
            "GET",
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": limit,
            },
            headers={"X-Api-Key": get_settings().news_api_key},
        )
        docs = []
        for article in data.get("articles", [])[:limit]:
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=article.get("title", ""),
                    url=article.get("url", ""),
                    content=article.get("description") or "",
                    metadata={
                        "published_at": article.get("publishedAt", ""),
                        "outlet": (article.get("source") or {}).get("name", ""),
                    },
                )
            )
        return docs
