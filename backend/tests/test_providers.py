"""Unit tests: LLM provider layer — JSON extraction and failover."""
import pytest

from app.core.exceptions import AllProvidersFailedError, ProviderError
from app.providers.base import LLMProvider, LLMResponse, extract_json
from app.providers.factory import LLMRouter


class TestExtractJson:
    def test_plain_json(self):
        assert extract_json('{"a": 1}') == {"a": 1}

    def test_fenced_json(self):
        assert extract_json('Here you go:\n```json\n{"a": 1}\n```') == {"a": 1}

    def test_json_with_prose(self):
        assert extract_json('Sure! {"key": [1, 2]} Hope that helps.') == {"key": [1, 2]}

    def test_array(self):
        assert extract_json("[1, 2, 3]") == [1, 2, 3]

    def test_no_json_raises(self):
        with pytest.raises(ValueError):
            extract_json("There is no JSON here at all.")


class _StubProvider(LLMProvider):
    def __init__(self, name: str, *, fails: bool, configured: bool = True):
        self.name = name
        self._fails = fails
        self._configured = configured
        self.calls = 0

    def is_configured(self) -> bool:
        return self._configured

    async def generate(self, prompt, *, system="", temperature=0.3, max_tokens=4096):
        self.calls += 1
        if self._fails:
            raise ProviderError(self.name, "boom")
        return LLMResponse(text="ok", provider=self.name, model="stub")


class TestRouterFailover:
    async def test_first_provider_wins(self):
        router = LLMRouter(priority=[])
        good = _StubProvider("p1", fails=False)
        router._providers = [good, _StubProvider("p2", fails=False)]
        response = await router.generate("hi")
        assert response.provider == "p1"

    async def test_failover_to_second(self):
        router = LLMRouter(priority=[])
        bad = _StubProvider("p1", fails=True)
        good = _StubProvider("p2", fails=False)
        router._providers = [bad, good]
        response = await router.generate("hi")
        assert response.provider == "p2"
        assert bad.calls == 1

    async def test_unconfigured_skipped(self):
        router = LLMRouter(priority=[])
        skipped = _StubProvider("p1", fails=False, configured=False)
        good = _StubProvider("p2", fails=False)
        router._providers = [skipped, good]
        response = await router.generate("hi")
        assert response.provider == "p2"
        assert skipped.calls == 0

    async def test_all_fail_raises(self):
        router = LLMRouter(priority=[])
        router._providers = [_StubProvider("p1", fails=True)]
        with pytest.raises(AllProvidersFailedError):
            await router.generate("hi")
