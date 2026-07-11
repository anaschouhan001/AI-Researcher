"""OpenAlex adapter — open academic research graph."""
from app.core.config import get_settings
from app.core.http import request_json
from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter


class OpenAlexSource(SourceAdapter):
    name = "openalex"
    category = "academic"

    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        data = await request_json(
            "GET",
            "https://api.openalex.org/works",
            params={
                "search": query,
                "per-page": limit,
                "sort": "relevance_score:desc",
                "mailto": get_settings().openalex_email,
            },
        )
        docs = []
        for work in data.get("results", [])[:limit]:
            abstract = ""
            inverted = work.get("abstract_inverted_index")
            if inverted:
                # OpenAlex stores abstracts as {word: [positions]}
                positions: list[tuple[int, str]] = []
                for word, idxs in inverted.items():
                    positions.extend((i, word) for i in idxs)
                abstract = " ".join(w for _, w in sorted(positions))[:4000]
            authors = [
                (a.get("author") or {}).get("display_name", "")
                for a in work.get("authorships", [])[:8]
            ]
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=work.get("display_name", ""),
                    url=work.get("doi") or (work.get("ids") or {}).get("openalex", ""),
                    content=abstract,
                    metadata={
                        "year": work.get("publication_year"),
                        "citations": work.get("cited_by_count"),
                        "authors": authors,
                        "open_access": (work.get("open_access") or {}).get("is_oa"),
                    },
                )
            )
        return docs
