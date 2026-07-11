"""Shared LangGraph pipeline state.

Kept as a TypedDict of plain/pydantic values so LangGraph can merge
node outputs; heavyweight resources (LLM router, vector store) live on
the agents, not in state.
"""
from typing import TypedDict

from app.schemas.research import ResearchResult, SourceDocument


class ResearchPlan(TypedDict):
    sub_questions: list[str]
    search_queries: list[str]
    source_categories: list[str]
    key_entities: list[str]


class PipelineState(TypedDict, total=False):
    # inputs
    job_id: str
    topic: str
    depth: str            # quick | standard | deep
    language: str         # en | hi

    # intermediate artifacts
    plan: ResearchPlan
    documents: list[SourceDocument]
    context_blocks: list[dict]     # hybrid-search hits used as evidence
    fact_check: dict               # confidence + conflicts payload
    draft: dict                    # writer output
    visuals: dict                  # visualization agent output

    # output
    result: ResearchResult
    podcast_path: str
    errors: list[str]
