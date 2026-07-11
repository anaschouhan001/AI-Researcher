"""Local Ollama provider (optional, last-resort fallback)."""
from app.core.config import get_settings
from app.providers.openai_compatible import OpenAICompatibleProvider


class OllamaProvider(OpenAICompatibleProvider):
    name = "ollama"

    @property
    def base_url(self) -> str:  # type: ignore[override]
        return f"{get_settings().ollama_base_url}/v1"

    def _api_key(self) -> str:
        return "ollama"  # Ollama ignores auth but the header must exist

    def _model_name(self) -> str:
        return get_settings().ollama_model

    def is_configured(self) -> bool:
        return bool(get_settings().ollama_base_url)
