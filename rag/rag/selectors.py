"""Lecture / agrégations (couche selector)."""

from __future__ import annotations

import os
from typing import Any

from django.conf import settings

from rag.conf import (
    DEFAULT_EMBEDDER_REGISTRY,
    DEFAULT_STORE_REGISTRY,
    SETTING_CHUNKING,
    SETTING_DEFAULT_EMBEDDER,
    SETTING_DEFAULT_STORE,
    SETTING_EMBEDDERS,
    SETTING_PROMPT_TEMPLATE,
    SETTING_RETRIEVAL,
    SETTING_VECTOR_STORES,
)
from rag.exceptions import EmbedderNotFoundError, StoreNotFoundError
from rag.factory import embedder_factory, store_factory
from rag.schemas import ChunkingConfig, EmbedConfig, StoreConfig


def _get_embedders_setting() -> dict[str, Any]:
    return getattr(settings, SETTING_EMBEDDERS, {})


def _get_stores_setting() -> dict[str, Any]:
    return getattr(settings, SETTING_VECTOR_STORES, {})


def list_available_embedders() -> list[str]:
    configured = _get_embedders_setting()
    if configured:
        return sorted(configured.keys())
    return embedder_factory.list_embedders()


def list_available_stores() -> list[str]:
    configured = _get_stores_setting()
    if configured:
        return sorted(configured.keys())
    return store_factory.list_stores()


def get_embedder_config(embedder_name: str | None = None) -> EmbedConfig:
    """Construit un EmbedConfig depuis les settings Django."""
    embedders = _get_embedders_setting()
    if not embedders:
        msg = (
            f"{SETTING_EMBEDDERS} est absent ou vide. "
            "Lance `uv run rag --help` pour le snippet."
        )
        raise EmbedderNotFoundError(msg)

    name = embedder_name or getattr(
        settings,
        SETTING_DEFAULT_EMBEDDER,
        next(iter(embedders)),
    )
    raw = embedders.get(name)
    if raw is None:
        raise EmbedderNotFoundError(
            f"Embedder '{name}' introuvable dans {SETTING_EMBEDDERS}.",
            component=name,
        )

    api_key = raw.get("api_key")
    if api_key is None and "api_key_env" in raw:
        api_key = os.environ.get(raw["api_key_env"])

    backend = raw.get("backend", DEFAULT_EMBEDDER_REGISTRY.get(name))
    if backend:
        embedder_factory.register(name, backend)

    return EmbedConfig(
        embedder=name,
        model=raw["model"],
        dimensions=int(raw["dimensions"]),
        api_key=api_key,
        base_url=raw.get("base_url"),
        timeout=int(raw.get("timeout", 60)),
        extra=dict(raw.get("extra", {})),
    )


def get_store_config(store_name: str | None = None) -> StoreConfig:
    """Construit un StoreConfig depuis les settings Django."""
    stores = _get_stores_setting()
    if not stores:
        msg = (
            f"{SETTING_VECTOR_STORES} est absent ou vide. "
            "Lance `uv run rag --help` pour le snippet."
        )
        raise StoreNotFoundError(msg)

    name = store_name or getattr(
        settings,
        SETTING_DEFAULT_STORE,
        next(iter(stores)),
    )
    raw = stores.get(name)
    if raw is None:
        raise StoreNotFoundError(
            f"Store '{name}' introuvable dans {SETTING_VECTOR_STORES}.",
            component=name,
        )

    backend = raw.get("backend", DEFAULT_STORE_REGISTRY.get(name))
    if backend:
        store_factory.register(name, backend)

    return StoreConfig(
        store=name,
        collection=str(raw.get("collection", "default")),
        dimensions=int(raw["dimensions"]),
        connection=dict(raw.get("connection", {})),
        extra=dict(raw.get("extra", {})),
    )


def get_chunking_config() -> ChunkingConfig:
    """Lit RAG_CHUNKING ou retourne les défauts."""
    raw: dict[str, Any] = getattr(settings, SETTING_CHUNKING, {}) or {}
    separators = raw.get("separators", ["\n\n", "\n", ". ", " "])
    return ChunkingConfig(
        strategy=str(raw.get("strategy", "fixed_size")),
        chunk_size=int(raw.get("chunk_size", 800)),
        chunk_overlap=int(raw.get("chunk_overlap", 120)),
        separators=tuple(separators),
        words_per_chunk=raw.get("words_per_chunk"),
    )


def get_retrieval_defaults() -> dict[str, Any]:
    """Lit RAG_RETRIEVAL ou retourne les défauts."""
    return dict(getattr(settings, SETTING_RETRIEVAL, {}) or {"top_k": 5, "min_score": 0.0})


def get_prompt_template() -> str:
    """Lit RAG_PROMPT_TEMPLATE ou retourne un template par défaut."""
    default = (
        "Tu réponds uniquement à partir du contexte fourni.\n\n"
        "Contexte:\n{context}\n\nQuestion: {question}"
    )
    return str(getattr(settings, SETTING_PROMPT_TEMPLATE, default) or default)
