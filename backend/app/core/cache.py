"""Redis-backed cache with graceful degradation.

If Redis is unreachable the cache becomes a no-op (research still works,
just slower) — an outage of a supporting service must never take down
the platform.
"""
import hashlib
import json
from functools import wraps
from typing import Any, Awaitable, Callable

import redis.asyncio as aioredis

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("core.cache")

_redis: aioredis.Redis | None = None
_redis_healthy: bool = True


async def get_redis() -> aioredis.Redis | None:
    global _redis, _redis_healthy
    if not _redis_healthy:
        return None
    if _redis is None:
        try:
            _redis = aioredis.from_url(
                get_settings().redis_url,
                decode_responses=True,
                socket_connect_timeout=2,
            )
            await _redis.ping()
        except Exception as exc:  # pragma: no cover - environment dependent
            logger.warning("cache.unavailable", error=str(exc))
            _redis = None
            _redis_healthy = False
    return _redis


def _make_key(namespace: str, payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:32]
    return f"researchgpt:{namespace}:{digest}"


async def cache_get(namespace: str, payload: Any) -> Any | None:
    client = await get_redis()
    if client is None:
        return None
    try:
        value = await client.get(_make_key(namespace, payload))
        if value is not None:
            logger.debug("cache.hit", namespace=namespace)
            return json.loads(value)
    except Exception as exc:
        logger.warning("cache.get_failed", namespace=namespace, error=str(exc))
    return None


async def cache_set(
    namespace: str, payload: Any, value: Any, ttl: int | None = None
) -> None:
    client = await get_redis()
    if client is None:
        return
    try:
        await client.set(
            _make_key(namespace, payload),
            json.dumps(value, default=str),
            ex=ttl or get_settings().cache_ttl_seconds,
        )
    except Exception as exc:
        logger.warning("cache.set_failed", namespace=namespace, error=str(exc))


def cached(namespace: str, ttl: int | None = None):
    """Decorator caching an async function's JSON-serializable result."""

    def decorator(fn: Callable[..., Awaitable[Any]]):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            key_payload = {
                "fn": fn.__qualname__,
                "args": [repr(a) for a in args[1:] if not callable(a)],
                "kwargs": {k: repr(v) for k, v in kwargs.items()},
            }
            hit = await cache_get(namespace, key_payload)
            if hit is not None:
                return hit
            result = await fn(*args, **kwargs)
            if result is not None:
                await cache_set(namespace, key_payload, result, ttl)
            return result

        return wrapper

    return decorator
