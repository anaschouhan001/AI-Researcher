"""ChromaDB vector store with hybrid (vector + BM25) search.

Each research job gets its own collection so retrieval never bleeds
between topics and cleanup is a single collection drop.
"""
import asyncio

from rank_bm25 import BM25Okapi

from app.core.config import get_settings
from app.core.logging import get_logger, log_timing
from app.retrieval.chunker import chunk_document
from app.retrieval.embeddings import get_embedding_backend
from app.schemas.research import SourceDocument

logger = get_logger("retrieval.store")


class ResearchVectorStore:
    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self._collection = None

    def _get_collection(self):
        if self._collection is None:
            import chromadb

            client = chromadb.PersistentClient(
                path=get_settings().chroma_persist_dir
            )
            self._collection = client.get_or_create_collection(
                name=f"research_{self.job_id}",
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    async def index_documents(self, docs: list[SourceDocument]) -> int:
        """Chunk, embed and store documents. Returns chunk count."""
        chunks: list[dict] = []
        for doc in docs:
            chunks.extend(chunk_document(doc))
        if not chunks:
            return 0

        texts = [c["text"] for c in chunks]
        with log_timing(logger, "rag.index", job_id=self.job_id, chunks=len(chunks)):
            embeddings = await get_embedding_backend().embed(texts)
            collection = await asyncio.to_thread(self._get_collection)
            existing = collection.count()
            await asyncio.to_thread(
                collection.add,
                ids=[f"{self.job_id}_{existing + i}" for i in range(len(chunks))],
                documents=texts,
                embeddings=embeddings,
                metadatas=[c["metadata"] for c in chunks],
            )
        return len(chunks)

    async def similarity_search(
        self, query: str, k: int = 8, source_filter: list[str] | None = None
    ) -> list[dict]:
        """Pure vector search, optionally filtered by source adapter name."""
        collection = await asyncio.to_thread(self._get_collection)
        if collection.count() == 0:
            return []
        query_embedding = (await get_embedding_backend().embed([query]))[0]
        where = {"source": {"$in": source_filter}} if source_filter else None
        results = await asyncio.to_thread(
            collection.query,
            query_embeddings=[query_embedding],
            n_results=min(k, collection.count()),
            where=where,
        )
        hits = []
        for text, meta, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            hits.append(
                {"text": text, "metadata": meta, "score": 1 - distance}
            )
        return hits

    async def hybrid_search(
        self, query: str, k: int = 8, source_filter: list[str] | None = None
    ) -> list[dict]:
        """Vector + BM25 keyword search fused with reciprocal rank fusion."""
        vector_hits = await self.similarity_search(query, k * 2, source_filter)
        if not vector_hits:
            return []

        # BM25 re-ranks the vector candidate pool by keyword relevance.
        corpus = [h["text"].lower().split() for h in vector_hits]
        bm25 = BM25Okapi(corpus)
        keyword_scores = bm25.get_scores(query.lower().split())
        keyword_order = sorted(
            range(len(vector_hits)), key=lambda i: keyword_scores[i], reverse=True
        )

        rrf: dict[int, float] = {}
        for rank, idx in enumerate(range(len(vector_hits))):  # vector ranking
            rrf[idx] = rrf.get(idx, 0) + 1 / (60 + rank + 1)
        for rank, idx in enumerate(keyword_order):  # keyword ranking
            rrf[idx] = rrf.get(idx, 0) + 1 / (60 + rank + 1)

        fused = sorted(rrf.items(), key=lambda kv: kv[1], reverse=True)[:k]
        return [
            {**vector_hits[idx], "score": round(score, 5)} for idx, score in fused
        ]

    async def delete(self) -> None:
        import chromadb

        client = chromadb.PersistentClient(path=get_settings().chroma_persist_dir)
        try:
            await asyncio.to_thread(
                client.delete_collection, f"research_{self.job_id}"
            )
        except Exception:
            pass
