"""CrossRef adapter — DOI lookup, journal metadata verification."""
from app.core.http import request_json
from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter


class CrossRefSource(SourceAdapter):
    name = "crossref"
    category = "academic"

    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        data = await request_json(
            "GET",
            "https://api.crossref.org/works",
            params={"query": query, "rows": limit, "sort": "relevance"},
        )
        docs = []
        for item in data.get("message", {}).get("items", [])[:limit]:
            title = "; ".join(item.get("title", [])) or "(untitled)"
            year = None
            issued = item.get("issued", {}).get("date-parts", [[None]])
            if issued and issued[0]:
                year = issued[0][0]
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=title,
                    url=item.get("URL", ""),
                    content=(item.get("abstract") or "")[:4000],
                    metadata={
                        "doi": item.get("DOI"),
                        "journal": "; ".join(item.get("container-title", [])),
                        "year": year,
                        "publisher": item.get("publisher"),
                        "type": item.get("type"),
                        "citations": item.get("is-referenced-by-count"),
                    },
                )
            )
        return docs
