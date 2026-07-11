"""Central application configuration.

Every tunable lives here and is sourced from environment variables /
`.env` via pydantic-settings. Nothing elsewhere in the codebase reads
`os.environ` directly.
"""
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Read the repo-root .env first, then a backend-local .env (which wins),
    # so `uvicorn` works from either the repo root or backend/.
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    # Application
    app_name: str = "ResearchGPT"
    app_env: str = Field("development", alias="APP_ENV")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    secret_key: str = Field("change-me", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    cors_origins: str = Field("http://localhost:3000", alias="CORS_ORIGINS")

    # LLM providers
    google_api_key: str = Field("", alias="GOOGLE_API_KEY")
    openrouter_api_key: str = Field("", alias="OPENROUTER_API_KEY")
    groq_api_key: str = Field("", alias="GROQ_API_KEY")
    ollama_base_url: str = Field("http://localhost:11434", alias="OLLAMA_BASE_URL")
    llm_provider_priority: str = Field(
        "gemini,openrouter,groq,ollama", alias="LLM_PROVIDER_PRIORITY"
    )
    gemini_model: str = Field("gemini-2.5-pro", alias="GEMINI_MODEL")
    openrouter_model: str = Field("deepseek/deepseek-chat", alias="OPENROUTER_MODEL")
    groq_model: str = Field("llama-3.3-70b-versatile", alias="GROQ_MODEL")
    ollama_model: str = Field("llama3.1", alias="OLLAMA_MODEL")

    # Research sources
    serpapi_key: str = Field("", alias="SERPAPI_KEY")
    tavily_api_key: str = Field("", alias="TAVILY_API_KEY")
    github_token: str = Field("", alias="GITHUB_TOKEN")
    huggingface_token: str = Field("", alias="HUGGINGFACE_TOKEN")
    kaggle_username: str = Field("", alias="KAGGLE_USERNAME")
    kaggle_key: str = Field("", alias="KAGGLE_KEY")
    gnews_api_key: str = Field("", alias="GNEWS_API_KEY")
    news_api_key: str = Field("", alias="NEWS_API_KEY")
    semantic_scholar_key: str = Field("", alias="SEMANTIC_SCHOLAR_KEY")
    pubmed_api_key: str = Field("", alias="PUBMED_API_KEY")
    openalex_email: str = Field("research@example.com", alias="OPENALEX_EMAIL")

    # Audio
    sarvam_api_key: str = Field("", alias="SARVAM_API_KEY")

    # Infrastructure
    database_url: str = Field(
        "sqlite+aiosqlite:///./researchgpt.db", alias="DATABASE_URL"
    )
    sync_database_url: str = Field(
        "sqlite:///./researchgpt.db", alias="SYNC_DATABASE_URL"
    )
    redis_url: str = Field("redis://localhost:6379/0", alias="REDIS_URL")
    celery_broker_url: str = Field("redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(
        "redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND"
    )
    chroma_persist_dir: str = Field("./chroma_data", alias="CHROMA_PERSIST_DIR")
    embedding_backend: str = Field(
        "sentence_transformers", alias="EMBEDDING_BACKEND"
    )  # sentence_transformers | google
    embedding_model: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL"
    )

    # Behaviour
    use_celery: bool = Field(False, alias="USE_CELERY")
    cache_ttl_seconds: int = Field(86400, alias="CACHE_TTL_SECONDS")
    http_timeout_seconds: float = Field(30.0, alias="HTTP_TIMEOUT_SECONDS")
    max_retries: int = Field(3, alias="MAX_RETRIES")
    storage_dir: str = Field("./storage", alias="STORAGE_DIR")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def provider_priority_list(self) -> list[str]:
        return [p.strip() for p in self.llm_provider_priority.split(",") if p.strip()]

    @property
    def storage_path(self) -> Path:
        path = Path(self.storage_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
