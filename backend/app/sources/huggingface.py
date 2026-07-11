"""HuggingFace adapter — models and datasets."""
from app.core.config import get_settings
from app.core.http import request_json
from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter


class HuggingFaceSource(SourceAdapter):
    name = "huggingface"
    category = "ml"
    cache_ttl = 6 * 3600

    def _headers(self) -> dict[str, str]:
        token = get_settings().huggingface_token
        return {"Authorization": f"Bearer {token}"} if token else {}

    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        docs: list[SourceDocument] = []

        models = await request_json(
            "GET",
            "https://huggingface.co/api/models",
            params={"search": query, "limit": limit, "sort": "downloads"},
            headers=self._headers(),
        )
        for model in models[:limit]:
            model_id = model.get("modelId") or model.get("id", "")
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=model_id,
                    url=f"https://huggingface.co/{model_id}",
                    content=f"HuggingFace model for '{query}'. "
                    f"Task: {model.get('pipeline_tag', 'unknown')}.",
                    metadata={
                        "kind": "model",
                        "downloads": model.get("downloads", 0),
                        "likes": model.get("likes", 0),
                        "task": model.get("pipeline_tag"),
                    },
                )
            )

        datasets = await request_json(
            "GET",
            "https://huggingface.co/api/datasets",
            params={"search": query, "limit": max(3, limit // 2)},
            headers=self._headers(),
        )
        for ds in datasets[: max(3, limit // 2)]:
            ds_id = ds.get("id", "")
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=ds_id,
                    url=f"https://huggingface.co/datasets/{ds_id}",
                    content=f"HuggingFace dataset relevant to '{query}'.",
                    metadata={
                        "kind": "dataset",
                        "downloads": ds.get("downloads", 0),
                        "likes": ds.get("likes", 0),
                    },
                )
            )
        return docs
