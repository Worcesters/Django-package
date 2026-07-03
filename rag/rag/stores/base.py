"""Base class for vector stores."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from rag.schemas import Chunk, RetrievedChunk


class BaseVectorStore(ABC):
    """Classe de base pour les vector stores."""

    store_id: str = ""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @abstractmethod
    def ensure_collection(self, collection: str, dimensions: int) -> None:
        """Prépare la collection (création si nécessaire)."""

    @abstractmethod
    def upsert(
        self,
        chunks: list[Chunk],
        vectors: list[list[float]],
        *,
        collection: str,
    ) -> int:
        """Insère ou met à jour des chunks vectorisés."""

    @abstractmethod
    def search(
        self,
        vector: list[float],
        *,
        top_k: int,
        collection: str,
        filters: dict[str, Any] | None = None,
        min_score: float = 0.0,
    ) -> list[RetrievedChunk]:
        """Recherche par similarité cosinus."""

    @abstractmethod
    def delete_by_metadata(
        self,
        filters: dict[str, Any],
        *,
        collection: str,
    ) -> int:
        """Supprime des entrées par métadonnées."""
