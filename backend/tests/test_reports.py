"""Unit tests: report generation."""
from app.reports.generator import build_full_markdown, markdown_to_html
from app.schemas.research import (
    Citation,
    Confidence,
    ResearchResult,
    Statistic,
    TimelineEvent,
)


def _result() -> ResearchResult:
    return ResearchResult(
        topic="Quantum Computing in Healthcare",
        executive_summary="Summary paragraph. [wikipedia]",
        report_markdown="## Overview\n\nBody text. [arxiv]",
        key_insights=["Insight one. [github]"],
        timeline=[TimelineEvent(date="2024", event="Milestone", source="arxiv")],
        statistics=[Statistic(label="Papers", value="120", source="openalex")],
        citations=[
            Citation(id=1, source="wikipedia", title="QC", url="https://w.org")
        ],
        confidence=Confidence(overall=88, rationale="Strong agreement."),
    )


def test_full_markdown_contains_all_sections():
    md = build_full_markdown(_result())
    for heading in (
        "# Quantum Computing in Healthcare",
        "## Executive Summary",
        "## Key Insights",
        "## Timeline",
        "## Statistics",
        "## References",
    ):
        assert heading in md
    assert "88%" in md


def test_html_render():
    html = markdown_to_html(build_full_markdown(_result()), "Test")
    assert html.startswith("<!doctype html>")
    assert "<h1>" in html and "Executive Summary" in html
