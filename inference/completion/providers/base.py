"""Interface commune des providers LLM."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from completion.schemas import CompletionResult


class BaseLLMProvider(ABC):
    """Base class for all LLM providers."""
    provider_id: str
    config: dict[str, Any]

    @abstractmethod
    def complete(self, messages: list[dict[str, str]]) -> CompletionResult:
        """Send a completion request to the provider."""
