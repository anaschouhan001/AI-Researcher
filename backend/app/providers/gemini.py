"""Google AI Studio (Gemini) provider."""
import asyncio

from app.core.config import get_settings
from app.core.exceptions import ProviderError
from app.core.logging import get_logger
from app.providers.base import LLMProvider, LLMResponse

logger = get_logger("providers.gemini")


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self) -> None:
        self._settings = get_settings()
        self._model = None

    def is_configured(self) -> bool:
        return bool(self._settings.google_api_key)

    def _get_model(self, system: str):
        import google.generativeai as genai

        genai.configure(api_key=self._settings.google_api_key)
        return genai.GenerativeModel(
            self._settings.gemini_model,
            system_instruction=system or None,
        )

    async def generate(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        try:
            model = self._get_model(system)
            # google-generativeai is sync; keep the event loop free
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            usage = getattr(response, "usage_metadata", None)
            return LLMResponse(
                text=response.text,
                provider=self.name,
                model=self._settings.gemini_model,
                input_tokens=getattr(usage, "prompt_token_count", None),
                output_tokens=getattr(usage, "candidates_token_count", None),
            )
        except Exception as exc:
            raise ProviderError(self.name, str(exc)) from exc
