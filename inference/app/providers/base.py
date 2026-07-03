"""Interface commune des providers LLM."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.schemas import CompletionResult


class BaseLLMProvider(ABC):
    provider_id: str

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @abstractmethod
    def complete(self, messages: list[dict[str, str]]) -> CompletionResult:
        """Envoie une requête de completion au provider."""
