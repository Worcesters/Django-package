"""Logique d'écriture (couche service)."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from rag.chunkers import chunk_text
from rag.exceptions import DimensionMismatchError
from rag.factory import embedder_factory, store_factory
from rag.schemas import IndexResult, RetrievedChunk
from rag.selectors import (
    get_chunking_config,
    get_embedder_config,
    get_retrieval_defaults,
    get_store_config,
)


def _embedder_config_dict(config: Any) -> dict[str, Any]:
    return {
        "model": config.model,
        "api_key": config.api_key,
        "base_url": config.base_url,
        "dimensions": config.dimensions,
        "timeout": config.timeout,
        "extra": config.extra,
    }


def _store_config_dict(config: Any) -> dict[str, Any]:
    return {
        "collection": config.collection,
        "dimensions": config.dimensions,
        "connection": config.connection,
        "extra": config.extra,
    }


def index_text(
    text: str,
    *,
    metadata: dict[str, Any] | None = None,
    source_id: str | None = None,
    collection: str | None = None,
    embedder: str | None = None,
    store: str | None = None,
) -> IndexResult:
    """Découpe, embed et indexe un texte."""
    embed_cfg = get_embedder_config(embedder)
    store_cfg = get_store_config(store)
    chunk_cfg = get_chunking_config()
    target_collection = collection or store_cfg.collection

    chunks = chunk_text(text, chunk_cfg)
    if not chunks:
        return IndexResult(chunks_indexed=0, collection=target_collection, source_id=source_id)

    enriched = [
        replace(
            chunk,
            metadata={**(metadata or {}), **chunk.metadata},
            source_id=source_id or chunk.source_id,
        )
        for chunk in chunks
    ]

    embedder_instance = embedder_factory.get_embedder(
        embed_cfg.embedder,
        _embedder_config_dict(embed_cfg),
        cache_instance=False,
    )
    vectors = [result.vector for result in embedder_instance.embed_batch([c.text for c in enriched])]

    if vectors and len(vectors[0]) != store_cfg.dimensions:
        raise DimensionMismatchError(
            f"Dimensions embedder ({len(vectors[0])}) != store ({store_cfg.dimensions}).",
            component=store_cfg.store,
        )

    store_instance = store_factory.get_store(
        store_cfg.store, _store_config_dict(store_cfg), cache_instance=False
    )
    store_instance.ensure_collection(target_collection, store_cfg.dimensions)
    count = store_instance.upsert(enriched, vectors, collection=target_collection)

    return IndexResult(
        chunks_indexed=count,
        collection=target_collection,
        source_id=source_id,
    )


def retrieve(
    query: str,
    *,
    top_k: int | None = None,
    filters: dict[str, Any] | None = None,
    collection: str | None = None,
    embedder: str | None = None,
    store: str | None = None,
    min_score: float | None = None,
) -> list[RetrievedChunk]:
    """Embed la requête et recherche les chunks les plus proches."""
    embed_cfg = get_embedder_config(embedder)
    store_cfg = get_store_config(store)
    defaults = get_retrieval_defaults()
    target_collection = collection or store_cfg.collection
    k = top_k if top_k is not None else int(defaults.get("top_k", 5))
    threshold = min_score if min_score is not None else float(defaults.get("min_score", 0.0))

    embedder_instance = embedder_factory.get_embedder(
        embed_cfg.embedder,
        _embedder_config_dict(embed_cfg),
        cache_instance=False,
    )
    query_vector = embedder_instance.embed(query).vector

    if len(query_vector) != store_cfg.dimensions:
        raise DimensionMismatchError(
            f"Dimensions embedder ({len(query_vector)}) != store ({store_cfg.dimensions}).",
            component=store_cfg.store,
        )

    store_instance = store_factory.get_store(
        store_cfg.store, _store_config_dict(store_cfg), cache_instance=False
    )
    return store_instance.search(
        query_vector,
        top_k=k,
        collection=target_collection,
        filters=filters,
        min_score=threshold,
    )
