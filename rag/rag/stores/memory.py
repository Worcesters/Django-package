"""Store en mémoire (dev / tests)."""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass
from typing import Any, ClassVar

from rag.schemas import Chunk, RetrievedChunk
from rag.stores.base import BaseVectorStore


@dataclass
class _StoredEntry:
    chunk_id: str
    text: str
    vector: list[float]
    metadata: dict[str, Any]
    source_id: str | None
    collection: str


class InMemoryStore(BaseVectorStore):
    """Vector store en RAM — données partagées entre instances du process."""

    store_id = "memory"
    _shared_data: ClassVar[dict[str, list[_StoredEntry]]] = {}

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

    def ensure_collection(self, collection: str, dimensions: int) -> None:
        self._shared_data.setdefault(collection, [])

    def upsert(
        self,
        chunks: list[Chunk],
        vectors: list[list[float]],
        *,
        collection: str,
    ) -> int:
        self.ensure_collection(collection, len(vectors[0]) if vectors else 0)
        entries = self._shared_data[collection]
        for chunk, vector in zip(chunks, vectors):
            entries.append(
                _StoredEntry(
                    chunk_id=str(uuid.uuid4()),
                    text=chunk.text,
                    vector=vector,
                    metadata=dict(chunk.metadata),
                    source_id=chunk.source_id,
                    collection=collection,
                )
            )
        return len(chunks)

    def search(
        self,
        vector: list[float],
        *,
        top_k: int,
        collection: str,
        filters: dict[str, Any] | None = None,
        min_score: float = 0.0,
    ) -> list[RetrievedChunk]:
        entries = self._shared_data.get(collection, [])
        scored: list[RetrievedChunk] = []
        for entry in entries:
            if filters and not _match_filters(entry.metadata, filters):
                continue
            score = _cosine_similarity(vector, entry.vector)
            if score < min_score:
                continue
            scored.append(
                RetrievedChunk(
                    text=entry.text,
                    score=score,
                    metadata=dict(entry.metadata),
                    chunk_id=entry.chunk_id,
                    source_id=entry.source_id,
                )
            )
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def delete_by_metadata(
        self,
        filters: dict[str, Any],
        *,
        collection: str,
    ) -> int:
        entries = self._shared_data.get(collection, [])
        kept = [entry for entry in entries if not _match_filters(entry.metadata, filters)]
        removed = len(entries) - len(kept)
        self._shared_data[collection] = kept
        return removed


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _match_filters(metadata: dict[str, Any], filters: dict[str, Any]) -> bool:
    return all(metadata.get(key) == value for key, value in filters.items())
