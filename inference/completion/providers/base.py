"""Interface commune des providers LLM."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from completion.schemas import CompletionResult


class BaseLLMProvider(ABC):
    """Classe de base pour tous les providers LLM (adaptateurs HTTP)."""

    provider_id: str = ""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @abstractmethod
    def complete(self, messages: list[dict[str, str]]) -> CompletionResult:
        """Envoie une requête de completion au provider."""
