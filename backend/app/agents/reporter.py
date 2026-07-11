"""Report Generator Agent — assembles the final ResearchResult from every
upstream artifact and renders the downloadable report files."""
from app.agents.base import BaseAgent
from app.agents.state import PipelineState
from app.reports.generator import write_report_files
from app.schemas.research import (
    ChartSpec,
    Citation,
    ClaimScore,
    Confidence,
    Conflict,
    Dataset,
    GitHubRepo,
    HFModel,
    KnowledgeGraph,
    NewsItem,
    Paper,
    ResearchResult,
    SourceDocument,
    Statistic,
    TimelineEvent,
)


class ReportAgent(BaseAgent):
    name = "reporter"

    async def run(self, state: PipelineState) -> dict:
        docs = state.get("documents", [])
        draft = state.get("draft", {})
        fact_check = state.get("fact_check", {})
        visuals = state.get("visuals", {})

        result = ResearchResult(
            topic=state["topic"],
            executive_summary=draft.get("executive_summary", ""),
            report_markdown=draft.get("report_markdown", ""),
            key_insights=[str(i) for i in draft.get("key_insights", [])],
            timeline=_safe_list(TimelineEvent, draft.get("timeline", [])),
            statistics=_safe_list(Statistic, draft.get("statistics", [])),
            news=_extract_news(docs),
            papers=_extract_papers(docs),
            github_repos=_extract_repos(docs),
            huggingface_models=_extract_models(docs),
            datasets=_extract_datasets(docs),
            charts=_safe_list(ChartSpec, visuals.get("charts", [])),
            knowledge_graph=KnowledgeGraph(**visuals.get("knowledge_graph", {})),
            mindmap_mermaid=visuals.get("mindmap_mermaid", ""),
            citations=_build_citations(docs),
            confidence=Confidence(
                overall=float(fact_check.get("overall", 50)),
                rationale=fact_check.get("rationale", ""),
                claim_scores=_safe_list(ClaimScore, fact_check.get("claim_scores", [])),
            ),
            conflicts=_safe_list(Conflict, fact_check.get("conflicts", [])),
            podcast_available=bool(state.get("podcast_path")),
        )

        write_report_files(state["job_id"], result)
        self.logger.info(
            "reporter.done",
            citations=len(result.citations),
            confidence=result.confidence.overall,
        )
        return {"result": result}


def _safe_list(model_cls, items: list) -> list:
    out = []
    for item in items:
        try:
            out.append(model_cls(**item) if isinstance(item, dict) else item)
        except Exception:
            continue  # skip malformed LLM entries rather than failing the run
    return out


def _extract_news(docs: list[SourceDocument]) -> list[NewsItem]:
    return [
        NewsItem(
            title=d.title,
            url=d.url,
            source=d.metadata.get("outlet") or d.source,
            published_at=d.metadata.get("published_at", ""),
            summary=d.content[:300],
        )
        for d in docs
        if d.source in ("gnews", "newsapi")
    ][:15]


def _extract_papers(docs: list[SourceDocument]) -> list[Paper]:
    papers = []
    for d in docs:
        if d.source not in ("arxiv", "semantic_scholar", "crossref", "pubmed", "openalex"):
            continue
        year = d.metadata.get("year")
        if not year and d.metadata.get("published"):
            try:
                year = int(str(d.metadata["published"])[:4])
            except ValueError:
                year = None
        papers.append(
            Paper(
                title=d.title,
                authors=d.metadata.get("authors", []),
                year=year if isinstance(year, int) else None,
                url=d.metadata.get("pdf_url") or d.url,
                citations=d.metadata.get("citations"),
                abstract=d.content[:500],
                source=d.source,
            )
        )
    # Most-cited first, uncited last
    papers.sort(key=lambda p: p.citations or 0, reverse=True)
    return papers[:20]


def _extract_repos(docs: list[SourceDocument]) -> list[GitHubRepo]:
    return [
        GitHubRepo(
            name=d.title,
            url=d.url,
            stars=d.metadata.get("stars", 0),
            description=d.content[:250],
            language=d.metadata.get("language"),
        )
        for d in docs
        if d.source == "github"
    ][:12]


def _extract_models(docs: list[SourceDocument]) -> list[HFModel]:
    return [
        HFModel(
            id=d.title,
            url=d.url,
            downloads=d.metadata.get("downloads", 0),
            likes=d.metadata.get("likes", 0),
            task=d.metadata.get("task"),
        )
        for d in docs
        if d.source == "huggingface" and d.metadata.get("kind") == "model"
    ][:12]


def _extract_datasets(docs: list[SourceDocument]) -> list[Dataset]:
    return [
        Dataset(
            name=d.title,
            url=d.url,
            source=d.source,
            description=d.content[:250],
        )
        for d in docs
        if d.source == "kaggle"
        or (d.source == "huggingface" and d.metadata.get("kind") == "dataset")
    ][:12]


def _build_citations(docs: list[SourceDocument]) -> list[Citation]:
    citations = []
    seen: set[str] = set()
    for d in docs:
        key = d.url or f"{d.source}:{d.title}"
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            Citation(id=len(citations) + 1, source=d.source, title=d.title, url=d.url)
        )
    return citations[:60]
