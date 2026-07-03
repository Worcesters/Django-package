"""Logique d'écriture (couche service)."""

from __future__ import annotations

from inference.factory import llm_factory
from inference.schemas import CompletionResult
from inference.selectors import get_provider_config


def complete(
    *,
    messages: list[dict[str, str]],
    provider: str | None = None,
) -> CompletionResult:
    """Orchestre un appel de completion via le provider configuré."""
    config = get_provider_config(provider)
    llm = llm_factory.get_provider(
        config.provider,
        {
            "model": config.model,
            "api_key": config.api_key,
            "base_url": config.base_url,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "timeout": config.timeout,
            "extra": config.extra,
        },
    )
    return llm.complete(messages)
