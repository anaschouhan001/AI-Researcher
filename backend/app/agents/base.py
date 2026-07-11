"""BaseAgent — shared machinery for every pipeline agent.

Gives each agent: an LLM router, structured-output calls with automatic
retry on malformed JSON, per-agent memory of prior exchanges, and
uniform logging.
"""
from typing import Any

from app.core.logging import get_logger, log_timing
from app.providers.base import extract_json
from app.providers.factory import get_llm_router


class BaseAgent:
    name: str = "base"

    def __init__(self) -> None:
        self.llm = get_llm_router()
        self.logger = get_logger(f"agents.{self.name}")
        # Short-term memory: prior prompt/response pairs within this run,
        # available to prompts that want conversational continuity.
        self.memory: list[dict[str, str]] = []

    async def ask(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        with log_timing(self.logger, "agent.llm_call", agent=self.name):
            response = await self.llm.generate(
                prompt, system=system, temperature=temperature, max_tokens=max_tokens
            )
        self.memory.append({"prompt": prompt[:500], "response": response.text[:500]})
        return response.text

    async def ask_structured(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float = 0.2,
        max_tokens: int = 4096,
        attempts: int = 3,
    ) -> Any:
        """Call the LLM and parse JSON, retrying with a repair hint on failure."""
        last_error: Exception | None = None
        current_prompt = prompt
        for attempt in range(1, attempts + 1):
            text = await self.ask(
                current_prompt,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            try:
                return extract_json(text)
            except ValueError as exc:
                last_error = exc
                self.logger.warning(
                    "agent.bad_json", agent=self.name, attempt=attempt
                )
                current_prompt = (
                    f"{prompt}\n\nYour previous reply was not valid JSON. "
                    "Reply again with ONLY the JSON object, nothing else."
                )
        raise ValueError(f"{self.name}: no valid JSON after {attempts} attempts") from last_error
