"""Research domain schemas — the single source of truth for the shape of
everything the pipeline produces. The frontend mirrors these types."""
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ResearchDepth(str, Enum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    depth: ResearchDepth = ResearchDepth.STANDARD
    language: Literal["en", "hi"] = "en"


# --- Retrieved evidence -----------------------------------------------------

class SourceDocument(BaseModel):
    """A normalized document returned by any source adapter."""

    source: str  # adapter name, e.g. "wikipedia", "arxiv"
    title: str
    url: str = ""
    content: str = ""
    metadata: dict = Field(default_factory=dict)


# --- Result building blocks -------------------------------------------------

class TimelineEvent(BaseModel):
    date: str
    event: str
    source: str = ""


class NewsItem(BaseModel):
    title: str
    url: str = ""
    source: str = ""
    published_at: str = ""
    summary: str = ""


class Paper(BaseModel):
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    url: str = ""
    citations: int | None = None
    abstract: str = ""
    source: str = ""


class GitHubRepo(BaseModel):
    name: str
    url: str = ""
    stars: int = 0
    description: str = ""
    language: str | None = None


class HFModel(BaseModel):
    id: str
    url: str = ""
    downloads: int = 0
    likes: int = 0
    task: str | None = None


class Dataset(BaseModel):
    name: str
    url: str = ""
    source: str = ""
    description: str = ""


class Statistic(BaseModel):
    label: str
    value: str
    source: str = ""


class ChartDataset(BaseModel):
    label: str
    data: list[float]


class ChartSpec(BaseModel):
    id: str
    type: Literal["bar", "pie", "line", "doughnut"]
    title: str
    labels: list[str]
    datasets: list[ChartDataset]


class GraphNode(BaseModel):
    id: str
    label: str
    group: str = "concept"


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str = ""


class KnowledgeGraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class Citation(BaseModel):
    id: int
    source: str
    title: str
    url: str = ""


class ClaimScore(BaseModel):
    claim: str
    score: float = Field(ge=0, le=100)
    sources: list[str] = Field(default_factory=list)


class Confidence(BaseModel):
    overall: float = Field(ge=0, le=100)
    rationale: str = ""
    claim_scores: list[ClaimScore] = Field(default_factory=list)


class ConflictPosition(BaseModel):
    statement: str
    sources: list[str] = Field(default_factory=list)


class Conflict(BaseModel):
    claim: str
    positions: list[ConflictPosition] = Field(default_factory=list)
    likely_correct: str = ""
    evidence: str = ""


# --- Final result -----------------------------------------------------------

class ResearchResult(BaseModel):
    topic: str
    executive_summary: str = ""
    report_markdown: str = ""
    key_insights: list[str] = Field(default_factory=list)
    timeline: list[TimelineEvent] = Field(default_factory=list)
    news: list[NewsItem] = Field(default_factory=list)
    papers: list[Paper] = Field(default_factory=list)
    github_repos: list[GitHubRepo] = Field(default_factory=list)
    huggingface_models: list[HFModel] = Field(default_factory=list)
    datasets: list[Dataset] = Field(default_factory=list)
    statistics: list[Statistic] = Field(default_factory=list)
    charts: list[ChartSpec] = Field(default_factory=list)
    knowledge_graph: KnowledgeGraph = Field(default_factory=KnowledgeGraph)
    mindmap_mermaid: str = ""
    citations: list[Citation] = Field(default_factory=list)
    confidence: Confidence = Field(default_factory=lambda: Confidence(overall=0))
    conflicts: list[Conflict] = Field(default_factory=list)
    podcast_available: bool = False


class ResearchJobOut(BaseModel):
    job_id: str
    topic: str
    status: JobStatus
    progress: int = 0
    current_stage: str = ""
    error: str | None = None
    result: ResearchResult | None = None
    created_at: str = ""


class ResearchJobCreated(BaseModel):
    job_id: str
    status: JobStatus = JobStatus.QUEUED
