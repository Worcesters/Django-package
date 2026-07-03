"""Provider Mistral."""

from __future__ import annotations

from completion.providers.chat_completions import ChatCompletionsProvider


class MistralProvider(ChatCompletionsProvider):
    provider_id = "mistral"
