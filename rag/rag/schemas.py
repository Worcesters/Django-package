"""Schémas de données (config, chunks, résultats RAG)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EmbedConfig:
    """Configuration d'un embedder."""

    embedder: str
    model: str
    dimensions: int
    api_key: str | None = None
    base_url: str | None = None
    timeout: int = 60
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StoreConfig:
    """Configuration d'un vector store."""

    store: str
    collection: str
    dimensions: int
    connection: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChunkingConfig:
    """Configuration du découpage de texte."""

    strategy: str = "fixed_size"
    chunk_size: int = 800
    chunk_overlap: int = 120
    separators: tuple[str, ...] = ("\n\n", "\n", ". ", " ")
    words_per_chunk: int | None = None


@dataclass(frozen=True)
class Chunk:
    """Fragment de texte indexé."""

    text: str
    index: int
    metadata: dict[str, Any] = field(default_factory=dict)
    source_id: str | None = None


@dataclass(frozen=True)
class EmbeddingResult:
    """Résultat d'un appel embedding."""

    vector: list[float]
    model: str
    dimensions: int
    usage: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievedChunk:
    """Chunk retrouvé par similarité."""

    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    chunk_id: str | None = None
    source_id: str | None = None


@dataclass(frozen=True)
class IndexResult:
    """Résultat d'une indexation."""

    chunks_indexed: int
    collection: str
    source_id: str | None = None
