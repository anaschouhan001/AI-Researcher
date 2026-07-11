"""arXiv adapter — research papers, authors, PDF links."""
import asyncio

from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter


class ArxivSource(SourceAdapter):
    name = "arxiv"
    category = "academic"

    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        return await asyncio.to_thread(self._fetch_sync, query, limit)

    def _fetch_sync(self, query: str, limit: int) -> list[SourceDocument]:
        import arxiv

        client = arxiv.Client(page_size=limit, delay_seconds=1, num_retries=3)
        search = arxiv.Search(
            query=query, max_results=limit, sort_by=arxiv.SortCriterion.Relevance
        )
        docs = []
        for result in client.results(search):
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=result.title,
                    url=result.entry_id,
                    content=result.summary[:4000],
                    metadata={
                        "authors": [a.name for a in result.authors],
                        "published": result.published.isoformat()
                        if result.published
                        else "",
                        "pdf_url": result.pdf_url,
                        "categories": list(result.categories),
                    },
                )
            )
        return docs
