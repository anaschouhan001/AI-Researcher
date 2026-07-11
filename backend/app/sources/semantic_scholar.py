"""Semantic Scholar adapter — citations, influential papers."""
from app.core.config import get_settings
from app.core.http import request_json
from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter


class SemanticScholarSource(SourceAdapter):
    name = "semantic_scholar"
    category = "academic"

    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        headers = {}
        key = get_settings().semantic_scholar_key
        if key:
            headers["x-api-key"] = key
        data = await request_json(
            "GET",
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={
                "query": query,
                "limit": limit,
                "fields": "title,abstract,year,citationCount,influentialCitationCount,"
                "authors,url,externalIds",
            },
            headers=headers,
        )
        docs = []
        for paper in data.get("data", [])[:limit]:
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=paper.get("title", ""),
                    url=paper.get("url", ""),
                    content=(paper.get("abstract") or "")[:4000],
                    metadata={
                        "year": paper.get("year"),
                        "citations": paper.get("citationCount"),
                        "influential_citations": paper.get("influentialCitationCount"),
                        "authors": [
                            a.get("name", "") for a in paper.get("authors", [])[:8]
                        ],
                        "doi": (paper.get("externalIds") or {}).get("DOI"),
                    },
                )
            )
        return docs
