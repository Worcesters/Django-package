"""Provider Mistral."""

from __future__ import annotations

from app.providers.chat_completions import ChatCompletionsProvider


class MistralProvider(ChatCompletionsProvider):
    provider_id = "mistral"
