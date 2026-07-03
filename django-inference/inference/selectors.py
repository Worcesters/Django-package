"""Lecture / agrégations (couche selector)."""

from __future__ import annotations

import os
from typing import Any

from django.conf import settings

from inference.conf import (
    DEFAULT_PROVIDER_REGISTRY,
    SETTING_DEFAULT_PROVIDER,
    SETTING_PROVIDERS,
)
from inference.exceptions import ProviderNotFoundError
from inference.factory import llm_factory
from inference.schemas import LLMConfig


def _get_providers_setting() -> dict[str, Any]:
    return getattr(settings, SETTING_PROVIDERS, {})


def list_available_providers() -> list[str]:
    configured = _get_providers_setting()
    if configured:
        return sorted(configured.keys())
    return llm_factory.list_providers()


def get_provider_config(provider_name: str | None = None) -> LLMConfig:
    """Construit un LLMConfig depuis les settings Django du projet hôte."""
    providers = _get_providers_setting()
    if not providers:
        msg = (
            f"{SETTING_PROVIDERS} est absent ou vide dans les settings Django. "
            "Lance `uv run inference-preview --help` pour le snippet."
        )
        raise ProviderNotFoundError(msg)

    name = provider_name or getattr(
        settings,
        SETTING_DEFAULT_PROVIDER,
        next(iter(providers)),
    )
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
        llm_factory.register(name, backend)

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
