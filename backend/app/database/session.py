"""Async SQLAlchemy engine/session management.

SQLite (aiosqlite) is the default store. Any SQLAlchemy async URL works
via DATABASE_URL (e.g. Postgres+asyncpg) — if that engine is
unreachable at startup we fall back to local SQLite so the platform
still runs.
"""
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.models import Base

logger = get_logger("database")

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _create_engine():
    settings = get_settings()
    return create_async_engine(settings.database_url, pool_pre_ping=True, echo=False)


async def init_db() -> None:
    """Create tables; fall back to local SQLite if the configured engine
    is unavailable."""
    global _engine, _session_factory
    _engine = _create_engine()
    try:
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:
        logger.warning("database.configured_engine_unavailable", error=str(exc))
        _engine = create_async_engine("sqlite+aiosqlite:///./researchgpt.db")
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database.sqlite_fallback")
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError("database not initialized — call init_db() first")
    return _session_factory


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency."""
    async with get_session_factory()() as session:
        yield session
