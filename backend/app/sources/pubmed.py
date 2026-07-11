"""PubMed adapter — medical/biomedical literature (NCBI E-utilities)."""
from app.core.config import get_settings
from app.core.http import request_json
from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


class PubMedSource(SourceAdapter):
    name = "pubmed"
    category = "medical"

    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        params: dict = {"db": "pubmed", "term": query, "retmax": limit, "retmode": "json"}
        key = get_settings().pubmed_api_key
        if key:
            params["api_key"] = key

        search = await request_json("GET", f"{BASE}/esearch.fcgi", params=params)
        ids = search.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []

        summary_params: dict = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "json",
        }
        if key:
            summary_params["api_key"] = key
        summaries = await request_json(
            "GET", f"{BASE}/esummary.fcgi", params=summary_params
        )

        docs = []
        result = summaries.get("result", {})
        for pmid in ids:
            item = result.get(pmid)
            if not item:
                continue
            authors = [a.get("name", "") for a in item.get("authors", [])[:8]]
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=item.get("title", ""),
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    content=f"{item.get('title', '')} — {item.get('source', '')} "
                    f"({item.get('pubdate', '')}). Authors: {', '.join(authors)}.",
                    metadata={
                        "pmid": pmid,
                        "journal": item.get("source", ""),
                        "pubdate": item.get("pubdate", ""),
                        "authors": authors,
                    },
                )
            )
        return docs
