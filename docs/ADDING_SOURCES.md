# Adding a Research Source

A source adapter is ~40 lines. Two steps:

## 1. Create the adapter

`backend/app/sources/my_source.py`:

```python
from app.core.config import get_settings
from app.core.http import request_json
from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter


class MySource(SourceAdapter):
    name = "my_source"          # unique; used in citations and filters
    category = "web"            # background|web|academic|code|ml|data|news|medical
    cache_ttl = 3600            # optional; default is CACHE_TTL_SECONDS

    def is_configured(self) -> bool:          # only if credentials are needed
        return bool(get_settings().my_source_key)

    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        data = await request_json(            # retries + backoff built in
            "GET", "https://api.example.com/search",
            params={"q": query, "n": limit},
        )
        return [
            SourceDocument(
                source=self.name,
                title=item["title"],
                url=item["url"],
                content=item["snippet"],
                metadata={"anything": "useful"},
            )
            for item in data["results"][:limit]
        ]
```

You get for free (from `SourceAdapter.search()`):
- Redis caching
- fault isolation (exceptions → empty result, run continues)
- latency logging
- skip-when-unconfigured behaviour

## 2. Register it

In `backend/app/sources/registry.py` add the import and append `MySource` to
`_ADAPTERS`. Done — the Planner can now route to it via its `category`, its
documents flow into RAG, fact-checking, citations and the report automatically.

## If it needs an API key

Add the field to `Settings` (`core/config.py`), and a line to `.env.example`.

## Adding an LLM provider

Same pattern: subclass `LLMProvider` (or `OpenAICompatibleProvider` if the API
speaks the OpenAI dialect — then it's ~15 lines), register it in
`providers/factory.py` `_REGISTRY`, and add its name to `LLM_PROVIDER_PRIORITY`.
