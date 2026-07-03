"""Tests chunkers."""

from rag.chunkers import chunk_text
from rag.schemas import ChunkingConfig


def test_chunk_fixed_size_splits_text() -> None:
    config = ChunkingConfig(strategy="fixed_size", chunk_size=10, chunk_overlap=2)
    chunks = chunk_text("abcdefghijklmnop", config)
    assert len(chunks) >= 2
    assert all(chunk.text for chunk in chunks)


def test_chunk_sentence_splits_on_punctuation() -> None:
    config = ChunkingConfig(strategy="sentence")
    chunks = chunk_text("Première phrase. Deuxième phrase!", config)
    assert len(chunks) == 2
