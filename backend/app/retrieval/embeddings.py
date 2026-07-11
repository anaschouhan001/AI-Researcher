"""Embedding backends: local Sentence Transformers (default) or Google.

Selected by EMBEDDING_BACKEND config; both expose the same interface.
"""
import asyncio
from abc import ABC, abstractmethod

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("retrieval.embeddings")


class EmbeddingBackend(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class SentenceTransformerBackend(EmbeddingBackend):
    def __init__(self) -> None:
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            model_name = get_settings().embedding_model
            logger.info("embeddings.loading_model", model=model_name)
            self._model = SentenceTransformer(model_name)
        return self._model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        model = await asyncio.to_thread(self._load)
        vectors = await asyncio.to_thread(
            model.encode, texts, show_progress_bar=False, normalize_embeddings=True
        )
        return [v.tolist() for v in vectors]


class GoogleEmbeddingBackend(EmbeddingBackend):
    async def embed(self, texts: list[str]) -> list[list[float]]:
        import google.generativeai as genai

        genai.configure(api_key=get_settings().google_api_key)

        def _embed_batch() -> list[list[float]]:
            result = genai.embed_content(
                model="models/text-embedding-004", content=texts
            )
            embedding = result["embedding"]
            # single text returns one vector; batch returns a list of vectors
            return embedding if isinstance(embedding[0], list) else [embedding]

        return await asyncio.to_thread(_embed_batch)


_backend: EmbeddingBackend | None = None


def get_embedding_backend() -> EmbeddingBackend:
    global _backend
    if _backend is None:
        if get_settings().embedding_backend == "google":
            _backend = GoogleEmbeddingBackend()
        else:
            _backend = SentenceTransformerBackend()
    return _backend
