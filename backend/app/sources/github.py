"""GitHub adapter — repositories, stars, activity."""
from app.core.config import get_settings
from app.core.http import request_json
from app.schemas.research import SourceDocument
from app.sources.base import SourceAdapter


class GitHubSource(SourceAdapter):
    name = "github"
    category = "code"
    cache_ttl = 6 * 3600  # repo stats go stale faster than papers

    async def _fetch(self, query: str, limit: int) -> list[SourceDocument]:
        headers = {"Accept": "application/vnd.github+json"}
        token = get_settings().github_token
        if token:
            headers["Authorization"] = f"Bearer {token}"
        data = await request_json(
            "GET",
            "https://api.github.com/search/repositories",
            params={"q": query, "sort": "stars", "order": "desc", "per_page": limit},
            headers=headers,
        )
        docs = []
        for repo in data.get("items", [])[:limit]:
            docs.append(
                SourceDocument(
                    source=self.name,
                    title=repo.get("full_name", ""),
                    url=repo.get("html_url", ""),
                    content=repo.get("description") or "",
                    metadata={
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "open_issues": repo.get("open_issues_count", 0),
                        "language": repo.get("language"),
                        "updated_at": repo.get("updated_at"),
                        "topics": repo.get("topics", [])[:10],
                    },
                )
            )
        return docs
