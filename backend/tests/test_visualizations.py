"""Unit tests: deterministic chart building from real source data."""
from app.visualizations.builder import (
    build_data_charts,
    github_stars_chart,
    publication_trend_chart,
    source_distribution_chart,
)


def test_github_stars_chart(sample_documents):
    chart = github_stars_chart(sample_documents)
    assert chart is not None
    assert chart.type == "bar"
    assert chart.datasets[0].data == [5000.0, 2400.0]  # sorted desc


def test_publication_trend_needs_enough_years(sample_documents):
    # Only one document carries a year -> no trend chart
    assert publication_trend_chart(sample_documents) is None


def test_source_distribution(sample_documents):
    chart = source_distribution_chart(sample_documents)
    assert chart is not None
    assert sum(chart.datasets[0].data) == len(sample_documents)


def test_build_data_charts_filters_none(sample_documents):
    charts = build_data_charts(sample_documents)
    ids = {c.id for c in charts}
    assert "github_stars" in ids
    assert "publication_trend" not in ids
