"""Shared fixtures. External APIs are mocked with respx; no network."""
import os

# Test environment must be set before app modules import settings.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_researchgpt.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-0123456789abcdef0123456789abcdef")
os.environ.setdefault("REDIS_URL", "redis://localhost:1/0")  # unreachable -> no-op cache

import pytest

from app.schemas.research import SourceDocument


@pytest.fixture
def sample_documents() -> list[SourceDocument]:
    return [
        SourceDocument(
            source="wikipedia",
            title="Quantum computing",
            url="https://en.wikipedia.org/wiki/Quantum_computing",
            content="Quantum computing uses quantum mechanics to process information. "
            "It has applications in cryptography, drug discovery and optimization.",
            metadata={"sections": ["History", "Applications"]},
        ),
        SourceDocument(
            source="arxiv",
            title="Quantum ML for Healthcare",
            url="https://arxiv.org/abs/1234.5678",
            content="We survey quantum machine learning methods applied to healthcare "
            "diagnostics, including variational quantum circuits.",
            metadata={"year": 2024, "authors": ["A. Researcher"], "published": "2024-03-01"},
        ),
        SourceDocument(
            source="github",
            title="qiskit/qiskit",
            url="https://github.com/Qiskit/qiskit",
            content="Open-source quantum computing framework.",
            metadata={"stars": 5000, "language": "Python"},
        ),
        SourceDocument(
            source="github",
            title="pennylane/pennylane",
            url="https://github.com/PennyLaneAI/pennylane",
            content="Quantum machine learning library.",
            metadata={"stars": 2400, "language": "Python"},
        ),
    ]
