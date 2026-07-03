"""Provider OpenAI (ChatGPT)."""

from __future__ import annotations

from inference.providers.base import BaseLLMProvider
from inference.schemas import CompletionResult


class OpenAIProvider(BaseLLMProvider):
    provider_id = "openai"

    def complete(self, messages: list[dict[str, str]]) -> CompletionResult:
        raise NotImplementedError("OpenAIProvider.complete() à implémenter.")
