"""Groq provider — fast Llama/Mistral inference."""
from app.core.config import get_settings
from app.providers.openai_compatible import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    name = "groq"
    base_url = "https://api.groq.com/openai/v1"

    def _api_key(self) -> str:
        return get_settings().groq_api_key

    def _model_name(self) -> str:
        return get_settings().groq_model
