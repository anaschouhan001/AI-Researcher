"""Health / readiness endpoints."""
from fastapi import APIRouter

from app.core.cache import get_redis
from app.providers.factory import get_llm_router
from app.sources.registry import all_sources

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/health/detail")
async def health_detail() -> dict:
    redis = await get_redis()
    sources = all_sources()
    return {
        "status": "ok",
        "redis": redis is not None,
        "llm_providers": get_llm_router().available,
        "sources": {
            name: adapter.is_configured() for name, adapter in sources.items()
        },
    }
