"""Domain exceptions. Adapters and providers raise these so callers can
handle failure classes uniformly instead of catching library-specific
errors everywhere."""


class ResearchGPTError(Exception):
    """Base class for all domain errors."""


class SourceError(ResearchGPTError):
    """A research source failed after retries."""

    def __init__(self, source: str, message: str):
        self.source = source
        super().__init__(f"[{source}] {message}")


class SourceRateLimitError(SourceError):
    """Source rate-limited us; retryable."""


class SourceUnavailableError(SourceError):
    """Source missing credentials or permanently unavailable; not retryable."""


class ProviderError(ResearchGPTError):
    """An LLM provider call failed after retries."""

    def __init__(self, provider: str, message: str):
        self.provider = provider
        super().__init__(f"[{provider}] {message}")


class AllProvidersFailedError(ResearchGPTError):
    """Every configured LLM provider failed for a request."""


class AudioGenerationError(ResearchGPTError):
    """Sarvam AI TTS failed."""


class ReportGenerationError(ResearchGPTError):
    """Report rendering failed."""
