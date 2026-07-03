"""Tests services avec mocks embedder."""

from unittest.mock import MagicMock, patch

import pytest

from rag.schemas import EmbeddingResult
from rag.services import index_text, retrieve
from rag.stores.memory import InMemoryStore


@pytest.fixture(autouse=True)
def clear_memory_store() -> None:
    InMemoryStore._shared_data.clear()


@patch("rag.services.embedder_factory.get_embedder")
def test_index_text_stores_chunks(mock_get_embedder: MagicMock) -> None:
    embedder = MagicMock()
    embedder.embed_batch.return_value = [
        EmbeddingResult(vector=[1.0, 0.0, 0.0], model="m", dimensions=3),
        EmbeddingResult(vector=[0.0, 1.0, 0.0], model="m", dimensions=3),
    ]
    mock_get_embedder.return_value = embedder

    result = index_text("abcdefghijklmnopqrs", embedder="ollama", store="memory")
    assert result.chunks_indexed >= 1
    assert result.collection == "test"


@patch("rag.services.embedder_factory.get_embedder")
def test_retrieve_returns_scored_chunks(mock_get_embedder: MagicMock) -> None:
    embedder = MagicMock()
    embedder.embed_batch.return_value = [
        EmbeddingResult(vector=[1.0, 0.0, 0.0], model="m", dimensions=3),
    ]
    embedder.embed.return_value = EmbeddingResult(
        vector=[1.0, 0.0, 0.0], model="m", dimensions=3
    )
    mock_get_embedder.return_value = embedder

    index_text("texte sur les chats", embedder="ollama", store="memory")
    chunks = retrieve("chats", embedder="ollama", store="memory", top_k=1)
    assert len(chunks) >= 1
    assert chunks[0].score > 0
