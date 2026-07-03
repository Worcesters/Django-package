"""Commandes CLI : index, retrieve, embed."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from rag.exceptions import RagError


def _ensure_project_on_path() -> None:
    cwd = Path.cwd().resolve()
    roots: list[Path] = [cwd]

    for parent in [cwd, *cwd.parents]:
        if (parent / "manage.py").is_file():
            roots.insert(0, parent)
            break

    for root in roots:
        root_str = str(root)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)


def setup_django(settings_module: str | None) -> None:
    import django

    module = settings_module or os.environ.get("DJANGO_SETTINGS_MODULE")
    if not module:
        msg = (
            "DJANGO_SETTINGS_MODULE requis.\n"
            '  Exemple : uv run rag --retrieve "question" --settings config.settings.dev\n'
            "  Ou export DJANGO_SETTINGS_MODULE=config.settings.dev"
        )
        raise SystemExit(msg)

    _ensure_project_on_path()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", module)

    try:
        django.setup()
    except ModuleNotFoundError as exc:
        top_level = module.split(".", 1)[0]
        msg = (
            f"Impossible d'importer '{module}' ({exc}).\n"
            "  Lance depuis la racine Django (manage.py).\n"
            f"  Vérifie que '{top_level}' existe."
        )
        raise SystemExit(msg) from exc


def run_index(
    text: str,
    *,
    collection: str | None = None,
    source_id: str | None = None,
    embedder: str | None = None,
    store: str | None = None,
    settings_module: str | None = None,
) -> None:
    setup_django(settings_module)
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
) -> None:
    setup_django(settings_module)
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
) -> None:
    setup_django(settings_module)
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
