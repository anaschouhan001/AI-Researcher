"""Retriever Agent — indexes evidence into ChromaDB and pulls the most
relevant context per sub-question via hybrid search."""
from app.agents.base import BaseAgent
from app.agents.state import PipelineState
from app.retrieval.vector_store import ResearchVectorStore


class RetrieverAgent(BaseAgent):
    name = "retriever"

    async def run(self, state: PipelineState) -> dict:
        store = ResearchVectorStore(state["job_id"])
        chunk_count = await store.index_documents(state.get("documents", []))
        self.logger.info("retriever.indexed", chunks=chunk_count)

        context_blocks: list[dict] = []
        seen_texts: set[str] = set()
        questions = [state["topic"], *state["plan"]["sub_questions"]]
        per_question = 6 if state.get("depth") == "deep" else 4

        for question in questions:
            hits = await store.hybrid_search(question, k=per_question)
            for hit in hits:
                fingerprint = hit["text"][:120]
                if fingerprint in seen_texts:
                    continue
                seen_texts.add(fingerprint)
                context_blocks.append({**hit, "question": question})

        self.logger.info("retriever.done", context_blocks=len(context_blocks))
        return {"context_blocks": context_blocks}
