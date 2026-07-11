"""Sentence-aware document chunking with overlap."""
import re

from app.schemas.research import SourceDocument

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    """Split text into ~chunk_size character chunks on sentence boundaries."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    sentences = _SENTENCE_SPLIT.split(text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if current and len(current) + len(sentence) + 1 > chunk_size:
            chunks.append(current.strip())
            # keep a tail of the previous chunk for context continuity
            current = current[-overlap:] + " " + sentence
        else:
            current = f"{current} {sentence}" if current else sentence
    if current.strip():
        chunks.append(current.strip())
    return chunks


def chunk_document(doc: SourceDocument) -> list[dict]:
    """Turn a SourceDocument into chunk dicts with full source metadata."""
    chunks = chunk_text(doc.content)
    return [
        {
            "text": chunk,
            "metadata": {
                "source": doc.source,
                "title": doc.title[:300],
                "url": doc.url[:500],
                "chunk_index": i,
                "total_chunks": len(chunks),
            },
        }
        for i, chunk in enumerate(chunks)
    ]
