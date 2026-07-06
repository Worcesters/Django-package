"""Lecture / agrégations (couche selector)."""

from __future__ import annotations

import os
from typing import Any

from completion.conf import (
    DEFAULT_PROVIDER_REGISTRY,
    SETTING_DEFAULT_PROVIDER,
    SETTING_PROVIDERS,
)
from completion.exceptions import ProviderNotFoundError
from completion.factory import llm_factory
from completion.schemas import LLMConfig
from completion.settings_source import get_setting


def _get_providers_setting() -> dict[str, Any]:
    raw = get_setting(SETTING_PROVIDERS, default={})
    return dict(raw) if raw else {}


def list_available_providers() -> list[str]:
    configured = _get_providers_setting()
    if configured:
        return sorted(configured.keys())
    return llm_factory.list_providers()


def get_provider_config(provider_name: str | None = None) -> LLMConfig:
    """Construit un LLMConfig depuis la configuration active (Django ou JSON)."""
    providers = _get_providers_setting()
    if not providers:
        msg = (
            f"{SETTING_PROVIDERS} est absent ou vide. "
            "Lance `uv run inference --help` pour le snippet."
        )
        raise ProviderNotFoundError(msg)

    default_name = get_setting(SETTING_DEFAULT_PROVIDER, default=None)
    name = provider_name or default_name or next(iter(providers))
    raw = providers.get(name)
    if raw is None:
        raise ProviderNotFoundError(
            f"Provider '{name}' introuvable dans {SETTING_PROVIDERS}.",
            provider=name,
        )

    api_key = raw.get("api_key")
    if api_key is None and "api_key_env" in raw:
        api_key = os.environ.get(raw["api_key_env"])

    backend = raw.get("backend", DEFAULT_PROVIDER_REGISTRY.get(name))
    if backend:
        llm_factory.register(name, str(backend))

    return LLMConfig(
        provider=name,
        model=raw["model"],
        api_key=api_key,
        base_url=raw.get("base_url"),
        temperature=float(raw.get("temperature", 0.7)),
        max_tokens=int(raw.get("max_tokens", 1024)),
        timeout=int(raw.get("timeout", 60)),
        extra=dict(raw.get("extra", {})),
    )
