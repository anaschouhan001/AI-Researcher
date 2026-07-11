"""Source registry — the only place that knows every adapter.

The Research Agent asks for adapters by category; the Planner decides
which categories matter for a topic.
"""
from app.sources.arxiv_source import ArxivSource
from app.sources.base import SourceAdapter
from app.sources.crossref import CrossRefSource
from app.sources.github import GitHubSource
from app.sources.gnews import GNewsSource
from app.sources.huggingface import HuggingFaceSource
from app.sources.kaggle import KaggleSource
from app.sources.newsapi import NewsAPISource
from app.sources.openalex import OpenAlexSource
from app.sources.pubmed import PubMedSource
from app.sources.semantic_scholar import SemanticScholarSource
from app.sources.serpapi import SerpAPISource
from app.sources.tavily import TavilySource
from app.sources.wikipedia import WikipediaSource

_ADAPTERS: list[type[SourceAdapter]] = [
    WikipediaSource,
    SerpAPISource,
    TavilySource,
    ArxivSource,
    SemanticScholarSource,
    CrossRefSource,
    GitHubSource,
    HuggingFaceSource,
    KaggleSource,
    GNewsSource,
    NewsAPISource,
    PubMedSource,
    OpenAlexSource,
]

_instances: dict[str, SourceAdapter] | None = None


def all_sources() -> dict[str, SourceAdapter]:
    global _instances
    if _instances is None:
        _instances = {cls.name: cls() for cls in _ADAPTERS}
    return _instances


def sources_by_category(categories: list[str]) -> list[SourceAdapter]:
    return [s for s in all_sources().values() if s.category in categories]


def get_source(name: str) -> SourceAdapter | None:
    return all_sources().get(name)
