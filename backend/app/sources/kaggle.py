"""Kaggle adapter — dataset discovery."""
from app.core.config import get_settings
from app.core.http import request_json
from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter


class KaggleSource(SourceAdapter):
    name = "kaggle"
    category = "data"

    def is_configured(self) -> bool:
        s = get_settings()
        return bool(s.kaggle_username and s.kaggle_key)

    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        import base64

        s = get_settings()
        auth = base64.b64encode(f"{s.kaggle_username}:{s.kaggle_key}".encode()).decode()
        data = await request_json(
            "GET",
            "https://www.kaggle.com/api/v1/datasets/list",
            params={"search": query, "pageSize": limit},
            headers={"Authorization": f"Basic {auth}"},
        )
        docs = []
        for ds in (data or [])[:limit]:
            ref = ds.get("ref", "")
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=ds.get("title", ref),
                    url=f"https://www.kaggle.com/datasets/{ref}",
                    content=ds.get("subtitle") or "",
                    metadata={
                        "kind": "dataset",
                        "downloads": ds.get("downloadCount", 0),
                        "votes": ds.get("voteCount", 0),
                        "size": ds.get("totalBytes"),
                    },
                )
            )
        return docs
