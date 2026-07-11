"""Source adapter contract.

Every research source (Wikipedia, arXiv, GitHub, ...) implements
`SourceAdapter`. The pipeline only ever calls `search()`, which adds
caching, retry-safe error handling and latency logging around the
adapter-specific `_fetch()`.

Adding a new source = one new file subclassing SourceAdapter + one line
in registry.py.
"""
from abc import ABC, abstractmethod

from app.core.cache import cache_get, cache_set
from app.core.logging import get_logger, log_timing
from app.schemas.research import SourceDocument

logger = get_logger("sources")


class SourceAdapter(ABC):
    """One external research source."""

    name: str = "base"
    category: str = "general"  # background | web | academic | code | ml | data | news | medical
    cache_ttl: int | None = None  # None -> global default

    def is_configured(self) -> bool:
        """Override when the source needs credentials."""
        return True

    @abstractmethod
    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        """Source-specific retrieval. May raise; search() handles errors."""

    async def search(self, query: str, limit: int = 8) -> list[SourceDocument]:
        """Cached, fault-isolated entry point used by the pipeline."""
        if not self.is_configured():
            logger.info("source.skipped_unconfigured", source=self.name)
            return []

        cache_key = {"source": self.name, "query": query.lower(), "limit": limit}
        cached_docs = await cache_get("source", cache_key)
        if cached_docs is not None:
            return [SourceDocument(**d) for d in cached_docs]

        try:
            with log_timing(logger, "source.fetch", source=self.name, query=query):
                docs = await self._fetch(query, limit)
        except Exception as exc:
            # One failing source must never sink the whole research run.
            logger.error("source.failed", source=self.name, error=str(exc))
            return []

        await cache_set(
            "source", cache_key, [d.model_dump() for d in docs], self.cache_ttl
        )
        return docs
