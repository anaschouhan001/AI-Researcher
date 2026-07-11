"""Shared implementation for OpenAI-compatible chat completion APIs.

OpenRouter, Groq and Ollama all speak the same /chat/completions dialect,
so they share this base and differ only in base URL, key, and model.
"""
import httpx

from app.core.exceptions import ProviderError
from app.core.http import request_json
from app.providers.base import LLMProvider, LLMResponse


class OpenAICompatibleProvider(LLMProvider):
    name = "openai_compatible"
    base_url: str = ""

    def _api_key(self) -> str:
        return ""

    def _model_name(self) -> str:
        raise NotImplementedError

    def _extra_headers(self) -> dict[str, str]:
        return {}

    def is_configured(self) -> bool:
        return bool(self._api_key())

    async def generate(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        headers = {"Content-Type": "application/json", **self._extra_headers()}
        key = self._api_key()
        if key:
            headers["Authorization"] = f"Bearer {key}"

        try:
            data = await request_json(
                "POST",
                f"{self.base_url}/chat/completions",
                json={
                    "model": self._model_name(),
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                headers=headers,
            )
            choice = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return LLMResponse(
                text=choice or "",
                provider=self.name,
                model=self._model_name(),
                input_tokens=usage.get("prompt_tokens"),
                output_tokens=usage.get("completion_tokens"),
            )
        except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
            raise ProviderError(self.name, str(exc)) from exc
