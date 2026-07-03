"""Provider Mistral."""

from __future__ import annotations

from inference.providers.base import BaseLLMProvider
from inference.schemas import CompletionResult


class MistralProvider(BaseLLMProvider):
    provider_id = "mistral"

    def complete(self, messages: list[dict[str, str]]) -> CompletionResult:
        raise NotImplementedError("MistralProvider.complete() à implémenter.")
