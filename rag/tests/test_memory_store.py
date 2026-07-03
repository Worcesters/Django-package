"""Tests memory store."""

from rag.schemas import Chunk
from rag.stores.memory import InMemoryStore


def test_memory_store_upsert_and_search() -> None:
    InMemoryStore._shared_data.clear()
    store = InMemoryStore({"collection": "demo", "dimensions": 3})
    chunks = [
        Chunk(text="chat", index=0),
        Chunk(text="chien", index=1),
    ]
    vectors = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]
    store.upsert(chunks, vectors, collection="demo")

    results = store.search([1.0, 0.0, 0.0], top_k=1, collection="demo")
    assert len(results) == 1
    assert results[0].text == "chat"
    assert results[0].score > 0.99
