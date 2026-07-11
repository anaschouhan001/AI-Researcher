"""Text utilities shared by agents."""
from app.schemas.research import SourceDocument


def format_evidence(
    context_blocks: list[dict],
    documents: list[SourceDocument],
    max_chars: int = 14000,
) -> str:
    """Render retrieved context (preferred) or raw documents as source-tagged
    evidence blocks for LLM prompts, respecting a character budget."""
    blocks: list[str] = []
    total = 0

    if context_blocks:
        for hit in context_blocks:
            meta = hit.get("metadata", {})
            block = (
                f"[{meta.get('source', 'unknown')}] {meta.get('title', '')}\n"
                f"{hit.get('text', '')}\n"
            )
            if total + len(block) > max_chars:
                break
            blocks.append(block)
            total += len(block)
    else:
        for doc in documents:
            block = f"[{doc.source}] {doc.title}\n{doc.content[:800]}\n"
            if total + len(block) > max_chars:
                break
            blocks.append(block)
            total += len(block)

    return "\n---\n".join(blocks) if blocks else "(no evidence gathered)"


def truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"
