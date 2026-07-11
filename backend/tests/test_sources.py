"""Unit tests: source adapters against mocked HTTP APIs (respx)."""
import httpx
import pytest
import respx

from app.sources.crossref import CrossRefSource
from app.sources.github import GitHubSource
from app.sources.openalex import OpenAlexSource
from app.sources.semantic_scholar import SemanticScholarSource


@respx.mock
async def test_github_search_parses_repos():
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(
            200,
            json={
                "items": [
                    {
                        "full_name": "org/repo",
                        "html_url": "https://github.com/org/repo",
                        "description": "A repo",
                        "stargazers_count": 42,
                        "forks_count": 5,
                        "open_issues_count": 3,
                        "language": "Python",
                        "updated_at": "2026-01-01T00:00:00Z",
                        "topics": ["ai"],
                    }
                ]
            },
        )
    )
    docs = await GitHubSource()._fetch("test", 5)
    assert len(docs) == 1
    assert docs[0].title == "org/repo"
    assert docs[0].metadata["stars"] == 42


@respx.mock
async def test_semantic_scholar_parses_papers():
    respx.get("https://api.semanticscholar.org/graph/v1/paper/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "title": "Paper A",
                        "abstract": "Abstract text",
                        "year": 2023,
                        "citationCount": 10,
                        "influentialCitationCount": 2,
                        "authors": [{"name": "Jane Doe"}],
                        "url": "https://sem.sch/p/1",
                        "externalIds": {"DOI": "10.1/abc"},
                    }
                ]
            },
        )
    )
    docs = await SemanticScholarSource()._fetch("test", 5)
    assert docs[0].metadata["citations"] == 10
    assert docs[0].metadata["doi"] == "10.1/abc"


@respx.mock
async def test_crossref_handles_missing_fields():
    respx.get("https://api.crossref.org/works").mock(
        return_value=httpx.Response(
            200,
            json={"message": {"items": [{"URL": "https://doi.org/x", "DOI": "10.2/x"}]}},
        )
    )
    docs = await CrossRefSource()._fetch("test", 5)
    assert docs[0].title == "(untitled)"
    assert docs[0].metadata["doi"] == "10.2/x"


@respx.mock
async def test_openalex_reconstructs_abstract():
    respx.get("https://api.openalex.org/works").mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {
                        "display_name": "Work",
                        "doi": "https://doi.org/10.3/y",
                        "publication_year": 2022,
                        "cited_by_count": 7,
                        "authorships": [],
                        "abstract_inverted_index": {
                            "Quantum": [0],
                            "healthcare": [1],
                            "applications": [2],
                        },
                    }
                ]
            },
        )
    )
    docs = await OpenAlexSource()._fetch("test", 5)
    assert docs[0].content == "Quantum healthcare applications"


@respx.mock
async def test_search_swallows_source_failure():
    """A failing source returns [] instead of raising — fault isolation."""
    respx.get("https://api.crossref.org/works").mock(
        return_value=httpx.Response(500)
    )
    docs = await CrossRefSource().search("test", 5)
    assert docs == []
