"""Provider OpenAI (ChatGPT)."""

from __future__ import annotations

from inference.providers.chat_completions import ChatCompletionsProvider


class OpenAIProvider(ChatCompletionsProvider):
    provider_id = "openai"
