"""Unit tests: document chunking."""
from app.retrieval.chunker import chunk_document, chunk_text
from app.schemas.research import SourceDocument


def test_short_text_single_chunk():
    assert chunk_text("Short sentence.") == ["Short sentence."]


def test_empty_text_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_long_text_splits_with_overlap():
    text = " ".join(f"Sentence number {i} has some words in it." for i in range(100))
    chunks = chunk_text(text, chunk_size=300, overlap=50)
    assert len(chunks) > 1
    assert all(len(c) <= 400 for c in chunks)  # size + carried overlap headroom


def test_chunk_document_carries_metadata():
    doc = SourceDocument(
        source="wikipedia",
        title="Test",
        url="https://example.org",
        content=" ".join(f"Sentence {i}." for i in range(300)),
    )
    chunks = chunk_document(doc)
    assert len(chunks) >= 2
    first = chunks[0]["metadata"]
    assert first["source"] == "wikipedia"
    assert first["url"] == "https://example.org"
    assert first["chunk_index"] == 0
    assert first["total_chunks"] == len(chunks)
