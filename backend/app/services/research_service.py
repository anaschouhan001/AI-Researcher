"""Research job lifecycle: create, execute, track, fetch.

Execution runs either on a Celery worker (production, USE_CELERY=true)
or as an in-process asyncio task (development) — same code path either
way via `execute_research_job`.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import run_research_pipeline
from app.core.logging import get_logger
from app.database.models import ResearchJob
from app.database.session import get_session_factory
from app.schemas.research import (
    JobStatus,
    ResearchJobOut,
    ResearchRequest,
    ResearchResult,
)

logger = get_logger("services.research")


async def create_job(
    db: AsyncSession, request: ResearchRequest, user_id: int | None
) -> ResearchJob:
    job = ResearchJob(
        id=str(uuid.uuid4()),
        user_id=user_id,
        topic=request.topic,
        depth=request.depth.value,
        language=request.language,
        status=JobStatus.QUEUED.value,
    )
    db.add(job)
    await db.commit()
    logger.info("job.created", job_id=job.id, topic=job.topic)
    return job


async def get_job(db: AsyncSession, job_id: str) -> ResearchJob | None:
    return await db.get(ResearchJob, job_id)


async def list_jobs(db: AsyncSession, user_id: int | None, limit: int = 25):
    query = (
        select(ResearchJob)
        .order_by(ResearchJob.created_at.desc())
        .limit(limit)
    )
    if user_id is not None:
        query = query.where(ResearchJob.user_id == user_id)
    return (await db.execute(query)).scalars().all()


def job_to_schema(job: ResearchJob) -> ResearchJobOut:
    return ResearchJobOut(
        job_id=job.id,
        topic=job.topic,
        status=JobStatus(job.status),
        progress=job.progress,
        current_stage=job.current_stage,
        error=job.error,
        result=ResearchResult(**job.result_json) if job.result_json else None,
        created_at=job.created_at.isoformat() if job.created_at else "",
    )


async def _update_job(job_id: str, **fields) -> None:
    factory = get_session_factory()
    async with factory() as session:
        job = await session.get(ResearchJob, job_id)
        if job is None:
            return
        for key, value in fields.items():
            setattr(job, key, value)
        await session.commit()


async def execute_research_job(job_id: str) -> None:
    """Run the full agent pipeline for a queued job, updating progress."""
    factory = get_session_factory()
    async with factory() as session:
        job = await session.get(ResearchJob, job_id)
        if job is None:
            logger.error("job.not_found", job_id=job_id)
            return
        topic, depth, language = job.topic, job.depth, job.language

    async def progress(stage: str, percent: int) -> None:
        await _update_job(
            job_id,
            status=JobStatus.RUNNING.value,
            current_stage=stage,
            progress=percent,
        )

    try:
        final_state = await run_research_pipeline(
            job_id, topic, depth=depth, language=language, progress=progress
        )
        result: ResearchResult | None = final_state.get("result")
        await _update_job(
            job_id,
            status=JobStatus.COMPLETED.value,
            progress=100,
            current_stage="completed",
            result_json=result.model_dump() if result else None,
        )
        logger.info("job.completed", job_id=job_id)
    except Exception as exc:
        logger.error("job.failed", job_id=job_id, error=str(exc))
        await _update_job(
            job_id,
            status=JobStatus.FAILED.value,
            current_stage="failed",
            error=str(exc)[:2000],
        )
