"""Research endpoints: submit jobs, poll status, download artifacts."""
import asyncio
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_optional_user
from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.models import User
from app.database.session import get_db
from app.schemas.research import (
    ResearchJobCreated,
    ResearchJobOut,
    ResearchRequest,
)
from app.services import research_service

router = APIRouter(prefix="/research", tags=["research"])
logger = get_logger("api.research")

_REPORT_FILES = {
    "markdown": ("report.md", "text/markdown"),
    "html": ("report.html", "text/html"),
    "pdf": ("report.pdf", "application/pdf"),
    "docx": (
        "report.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ),
}


# In-process tasks must be referenced or asyncio may garbage-collect them mid-run.
_background_tasks: set[asyncio.Task] = set()


def _dispatch(job_id: str) -> None:
    """Run via Celery in production, in-process task in development."""
    if get_settings().use_celery:
        from app.workers.tasks import execute_research_task

        execute_research_task.delay(job_id)
    else:
        task = asyncio.create_task(research_service.execute_research_job(job_id))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)


@router.post("", response_model=ResearchJobCreated, status_code=202)
async def start_research(
    payload: ResearchRequest,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    job = await research_service.create_job(db, payload, user.id if user else None)
    _dispatch(job.id)
    return ResearchJobCreated(job_id=job.id)


@router.get("", response_model=list[ResearchJobOut])
async def list_research(
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    jobs = await research_service.list_jobs(db, user.id if user else None)
    return [research_service.job_to_schema(j) for j in jobs]


@router.get("/{job_id}", response_model=ResearchJobOut)
async def get_research(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await research_service.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Research job not found")
    return research_service.job_to_schema(job)


@router.get("/{job_id}/report")
async def download_report(
    job_id: str, format: str = "markdown", db: AsyncSession = Depends(get_db)
):
    if format not in _REPORT_FILES:
        raise HTTPException(status_code=400, detail=f"Unknown format '{format}'")
    job = await research_service.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Research job not found")

    filename, media_type = _REPORT_FILES[format]
    path = Path(get_settings().storage_dir) / job_id / filename
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"{format} report not available (job status: {job.status})",
        )
    safe_topic = "".join(c if c.isalnum() or c in " -_" else "_" for c in job.topic)[:60]
    return FileResponse(
        path, media_type=media_type, filename=f"{safe_topic}{path.suffix}"
    )


@router.get("/{job_id}/podcast")
async def download_podcast(
    job_id: str, language: str = "en", db: AsyncSession = Depends(get_db)
):
    job = await research_service.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Research job not found")
    path = Path(get_settings().storage_dir) / job_id / f"podcast_{language}.wav"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Podcast not available")
    return FileResponse(path, media_type="audio/wav", filename="research_podcast.wav")
