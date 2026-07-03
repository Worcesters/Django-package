"""Base class for all embedders."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from rag.schemas import EmbeddingResult


class BaseEmbedder(ABC):
    """Classe de base pour tous les embedders."""

    embedder_id: str = ""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @abstractmethod
    def embed(self, text: str) -> EmbeddingResult:
        """Embed a single text."""

    def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """Embed a batch of texts (défaut : appels séquentiels)."""
        return [self.embed(text) for text in texts]
