"""Celery tasks. Each task bootstraps its own event loop and DB session."""
import asyncio

from app.core.logging import configure_logging, get_logger
from app.workers.celery_app import celery_app

logger = get_logger("workers.tasks")


@celery_app.task(name="research.execute", bind=True, max_retries=1)
def execute_research_task(self, job_id: str) -> str:
    configure_logging()

    async def _run() -> None:
        from app.database.session import init_db
        from app.services.research_service import execute_research_job

        await init_db()
        await execute_research_job(job_id)

    try:
        asyncio.run(_run())
        return job_id
    except Exception as exc:
        logger.error("task.failed", job_id=job_id, error=str(exc))
        raise self.retry(exc=exc, countdown=30)
