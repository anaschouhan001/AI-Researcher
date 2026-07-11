"""Resilient async HTTP client shared by all source adapters.

Wraps httpx with:
- exponential-backoff retries (tenacity) on timeouts / 5xx / 429
- uniform latency + failure logging
- a single connection pool per process
"""
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("core.http")

_client: httpx.AsyncClient | None = None


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or status >= 500
    return False


async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        settings = get_settings()
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.http_timeout_seconds),
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
            headers={"User-Agent": "ResearchGPT/1.0 (research assistant)"},
            follow_redirects=True,
        )
    return _client


async def close_client() -> None:
    global _client
    if _client is not None and not _client.is_closed:
        await _client.aclose()
    _client = None


async def request_json(
    method: str,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    json: Any = None,
    headers: dict[str, str] | None = None,
    max_retries: int | None = None,
) -> Any:
    """Perform an HTTP request with retries and return parsed JSON."""
    settings = get_settings()
    attempts = max_retries if max_retries is not None else settings.max_retries
    client = await get_client()

    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        retry=retry_if_exception(_is_retryable),
        reraise=True,
    ):
        with attempt:
            response = await client.request(
                method, url, params=params, json=json, headers=headers
            )
            if attempt.retry_state.attempt_number > 1:
                logger.warning(
                    "http.retry",
                    url=url,
                    attempt=attempt.retry_state.attempt_number,
                )
            response.raise_for_status()
            return response.json()


async def request_bytes(
    method: str,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    json: Any = None,
    headers: dict[str, str] | None = None,
) -> bytes:
    """Perform an HTTP request with retries and return raw bytes."""
    settings = get_settings()
    client = await get_client()

    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        retry=retry_if_exception(_is_retryable),
        reraise=True,
    ):
        with attempt:
            response = await client.request(
                method, url, params=params, json=json, headers=headers
            )
            response.raise_for_status()
            return response.content
    raise RuntimeError("unreachable")
