"""Provider Ollama (Llama local et autres modèles)."""

from __future__ import annotations

from inference.providers.base import BaseLLMProvider
from inference.schemas import CompletionResult


class OllamaProvider(BaseLLMProvider):
    provider_id = "llama"

    def complete(self, messages: list[dict[str, str]]) -> CompletionResult:
        raise NotImplementedError("OllamaProvider.complete() à implémenter.")
