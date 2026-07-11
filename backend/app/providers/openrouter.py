"""OpenRouter provider — gateway to Claude, DeepSeek, Qwen, Llama, Mistral..."""
from app.core.config import get_settings
from app.providers.openai_compatible import OpenAICompatibleProvider


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"
    base_url = "https://openrouter.ai/api/v1"

    def _api_key(self) -> str:
        return get_settings().openrouter_api_key

    def _model_name(self) -> str:
        return get_settings().openrouter_model

    def _extra_headers(self) -> dict[str, str]:
        return {
            "HTTP-Referer": "https://researchgpt.local",
            "X-Title": "ResearchGPT",
        }
