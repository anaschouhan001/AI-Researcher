"""LLMRouter — provider selection with automatic failover.

Providers are tried in the order given by LLM_PROVIDER_PRIORITY; the
first configured one that succeeds wins. Token usage and latency are
logged per call.
"""
import time

from app.core.config import get_settings
from app.core.exceptions import AllProvidersFailedError, ProviderError
from app.core.logging import get_logger
from app.providers.base import LLMProvider, LLMResponse
from app.providers.gemini import GeminiProvider
from app.providers.groq import GroqProvider
from app.providers.ollama import OllamaProvider
from app.providers.openrouter import OpenRouterProvider

logger = get_logger("providers.router")

_REGISTRY: dict[str, type[LLMProvider]] = {
    "gemini": GeminiProvider,
    "openrouter": OpenRouterProvider,
    "groq": GroqProvider,
    "ollama": OllamaProvider,
}


class LLMRouter:
    def __init__(self, priority: list[str] | None = None) -> None:
        order = priority or get_settings().provider_priority_list
        self._providers: list[LLMProvider] = [
            _REGISTRY[name]() for name in order if name in _REGISTRY
        ]

    @property
    def available(self) -> list[str]:
        return [p.name for p in self._providers if p.is_configured()]

    async def generate(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        errors: list[str] = []
        for provider in self._providers:
            if not provider.is_configured():
                continue
            start = time.perf_counter()
            try:
                response = await provider.generate(
                    prompt,
                    system=system,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                logger.info(
                    "llm.call",
                    provider=provider.name,
                    model=response.model,
                    latency_ms=round((time.perf_counter() - start) * 1000, 1),
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                )
                return response
            except ProviderError as exc:
                logger.warning(
                    "llm.provider_failed",
                    provider=provider.name,
                    error=str(exc),
                    latency_ms=round((time.perf_counter() - start) * 1000, 1),
                )
                errors.append(str(exc))
        raise AllProvidersFailedError(
            f"all providers failed or unconfigured: {errors or 'none configured'}"
        )


_router: LLMRouter | None = None


def get_llm_router() -> LLMRouter:
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router
