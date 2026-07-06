"""Commandes CLI : index, retrieve, embed."""

from __future__ import annotations

import sys

from rag.exceptions import RagError
from rag.settings_source import bootstrap_runtime


def run_index(
    text: str,
    *,
    collection: str | None = None,
    source_id: str | None = None,
    embedder: str | None = None,
    store: str | None = None,
    settings_module: str | None = None,
    config_path: str | None = None,
) -> None:
    bootstrap_runtime(settings_module=settings_module, config_path=config_path)
    from rag.services import index_text

    try:
        result = index_text(
            text,
            collection=collection,
            source_id=source_id,
            embedder=embedder,
            store=store,
        )
    except RagError as exc:
        print(f"Erreur [{exc.code}]: {exc.message}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"Indexé : {result.chunks_indexed} chunk(s) dans '{result.collection}'")
    if result.source_id:
        print(f"source_id={result.source_id}", file=sys.stderr)


def run_retrieve(
    query: str,
    *,
    top_k: int | None = None,
    collection: str | None = None,
    embedder: str | None = None,
    store: str | None = None,
    settings_module: str | None = None,
    config_path: str | None = None,
) -> None:
    bootstrap_runtime(settings_module=settings_module, config_path=config_path)
    from rag.services import retrieve

    try:
        chunks = retrieve(
            query,
            top_k=top_k,
            collection=collection,
            embedder=embedder,
            store=store,
        )
    except RagError as exc:
        print(f"Erreur [{exc.code}]: {exc.message}", file=sys.stderr)
        raise SystemExit(1) from exc

    if not chunks:
        print("Aucun chunk trouvé.")
        return

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n--- [{index}] score={chunk.score:.4f} ---")
        print(chunk.text)


def run_embed(
    text: str,
    *,
    embedder: str | None = None,
    settings_module: str | None = None,
    config_path: str | None = None,
) -> None:
    bootstrap_runtime(settings_module=settings_module, config_path=config_path)
    from rag.factory import embedder_factory
    from rag.selectors import get_embedder_config

    config = get_embedder_config(embedder)
    try:
        instance = embedder_factory.get_embedder(
            config.embedder,
            {
                "model": config.model,
                "api_key": config.api_key,
                "base_url": config.base_url,
                "dimensions": config.dimensions,
                "timeout": config.timeout,
                "extra": config.extra,
            },
            cache_instance=False,
        )
        result = instance.embed(text)
    except RagError as exc:
        print(f"Erreur [{exc.code}]: {exc.message}", file=sys.stderr)
        raise SystemExit(1) from exc

    preview = result.vector[:5]
    print(f"model={result.model} dimensions={result.dimensions}")
    print(f"vector[:5]={preview} ...")
