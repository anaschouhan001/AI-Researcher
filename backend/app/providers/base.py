"""LLM provider abstraction.

Adding a provider = subclass LLMProvider, register it in factory.py.
Nothing else in the codebase changes. All agents talk to `LLMRouter`,
never to a concrete provider.
"""
import json
import re
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from app.core.logging import get_logger

logger = get_logger("providers")


class LLMResponse(BaseModel):
    text: str
    provider: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class LLMProvider(ABC):
    """A single LLM backend (Gemini, OpenRouter, Groq, Ollama...)."""

    name: str = "base"

    @abstractmethod
    def is_configured(self) -> bool:
        """True when required credentials/config are present."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Generate a completion. Raise ProviderError on failure."""


def extract_json(text: str) -> Any:
    """Robustly pull a JSON object/array out of an LLM response.

    Handles code fences, leading prose, and trailing commentary. Raises
    ValueError when no parseable JSON is present so callers can retry.
    """
    fence = re.search(r"```(?:json)?\s*(.+?)```", text, re.DOTALL)
    candidate = fence.group(1) if fence else text
    candidate = candidate.strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    # Fall back to the outermost {...} or [...] span
    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        start = candidate.find(open_ch)
        end = candidate.rfind(close_ch)
        if start != -1 and end > start:
            try:
                return json.loads(candidate[start : end + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError("no JSON found in LLM response")
