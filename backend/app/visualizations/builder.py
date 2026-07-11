"""Deterministic chart construction from real source data.

Charts derived from actual API payloads (publication years, GitHub stars,
model downloads, source distribution) are built here in plain Python —
no LLM in the loop, so the numbers are always real. The LLM only adds
the knowledge graph / mind map and optional narrative charts on top.
"""
from collections import Counter

from app.schemas.research import ChartDataset, ChartSpec, SourceDocument


def publication_trend_chart(docs: list[SourceDocument]) -> ChartSpec | None:
    years: list[int] = []
    for doc in docs:
        year = doc.metadata.get("year")
        if not year and doc.metadata.get("published"):
            try:
                year = int(str(doc.metadata["published"])[:4])
            except ValueError:
                year = None
        if isinstance(year, int) and 1980 <= year <= 2100:
            years.append(year)
    if len(years) < 3:
        return None
    counts = Counter(years)
    ordered = sorted(counts)
    return ChartSpec(
        id="publication_trend",
        type="line",
        title="Publication Trend (papers per year)",
        labels=[str(y) for y in ordered],
        datasets=[
            ChartDataset(label="Papers", data=[float(counts[y]) for y in ordered])
        ],
    )


def github_stars_chart(docs: list[SourceDocument]) -> ChartSpec | None:
    repos = [
        (d.title, d.metadata.get("stars", 0))
        for d in docs
        if d.source == "github" and d.metadata.get("stars")
    ]
    repos.sort(key=lambda r: r[1], reverse=True)
    repos = repos[:8]
    if len(repos) < 2:
        return None
    return ChartSpec(
        id="github_stars",
        type="bar",
        title="Top GitHub Repositories by Stars",
        labels=[name.split("/")[-1][:24] for name, _ in repos],
        datasets=[ChartDataset(label="Stars", data=[float(s) for _, s in repos])],
    )


def source_distribution_chart(docs: list[SourceDocument]) -> ChartSpec | None:
    counts = Counter(d.source for d in docs)
    if len(counts) < 2:
        return None
    ordered = counts.most_common()
    return ChartSpec(
        id="source_distribution",
        type="doughnut",
        title="Evidence by Source",
        labels=[name for name, _ in ordered],
        datasets=[
            ChartDataset(label="Documents", data=[float(c) for _, c in ordered])
        ],
    )


def model_downloads_chart(docs: list[SourceDocument]) -> ChartSpec | None:
    models = [
        (d.title, d.metadata.get("downloads", 0))
        for d in docs
        if d.source == "huggingface"
        and d.metadata.get("kind") == "model"
        and d.metadata.get("downloads")
    ]
    models.sort(key=lambda m: m[1], reverse=True)
    models = models[:6]
    if len(models) < 2:
        return None
    return ChartSpec(
        id="model_downloads",
        type="bar",
        title="Top HuggingFace Models by Downloads",
        labels=[name.split("/")[-1][:24] for name, _ in models],
        datasets=[ChartDataset(label="Downloads", data=[float(d) for _, d in models])],
    )


def build_data_charts(docs: list[SourceDocument]) -> list[ChartSpec]:
    charts = [
        publication_trend_chart(docs),
        github_stars_chart(docs),
        model_downloads_chart(docs),
        source_distribution_chart(docs),
    ]
    return [c for c in charts if c is not None]


def chart_aggregates_summary(charts: list[ChartSpec]) -> str:
    """Human-readable dump of the deterministic chart data for LLM prompts."""
    lines = []
    for chart in charts:
        pairs = ", ".join(
            f"{label}={value:g}"
            for label, value in zip(chart.labels, chart.datasets[0].data)
        )
        lines.append(f"{chart.title}: {pairs}")
    return "\n".join(lines) if lines else "(no numeric aggregates available)"
