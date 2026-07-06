"""Point d'entrée CLI : uv run rag [--help] [--preview] [--test] [--index] [--retrieve]."""

from __future__ import annotations

import argparse
from pathlib import Path

from base_cmd.package_cli import (
    PackageCliConfig,
    build_package_parser,
    dispatch_shared_commands,
    print_default_help,
    validate_settings_config_exclusive,
)

from rag.conf import format_settings_help
from rag.rag_cmd import run_embed, run_index, run_retrieve

PACKAGE_CLI = PackageCliConfig(
    prog="rag",
    package_module="rag",
    description="CLI rag : configuration, preview d'architecture, tests et commandes RAG.",
    preview_title="rag — architecture",
    setting_prefix="RAG",
    module_prefix="rag",
    settings_epilog=format_settings_help(),
)


def _register_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--index",
        "-i",
        metavar="TEXTE",
        help="Indexe un texte (chunk + embed + store).",
    )
    parser.add_argument(
        "--retrieve",
        "-r",
        metavar="QUESTION",
        help="Recherche les chunks les plus proches d'une question.",
    )
    parser.add_argument(
        "--embed",
        "-e",
        metavar="TEXTE",
        help="Teste l'embedder (affiche dimensions + début du vecteur).",
    )
    parser.add_argument(
        "--collection",
        metavar="NOM",
        help="Collection vectorielle (sinon défaut du store).",
    )
    parser.add_argument(
        "--source-id",
        metavar="ID",
        help="Avec --index : identifiant source pour les métadonnées.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        metavar="N",
        help="Avec --retrieve : nombre de chunks (sinon RAG_RETRIEVAL.top_k).",
    )
    parser.add_argument(
        "--embedder",
        metavar="NOM",
        help="Embedder explicite (sinon RAG_DEFAULT_EMBEDDER).",
    )
    parser.add_argument(
        "--store",
        metavar="NOM",
        help="Vector store explicite (sinon RAG_DEFAULT_STORE).",
    )


def build_parser():
    return build_package_parser(PACKAGE_CLI, register_args=_register_args)


def _validate_exclusive(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    validate_settings_config_exclusive(parser, args)
    has_index = args.index is not None
    has_retrieve = args.retrieve is not None
    has_embed = args.embed is not None
    actions = sum(
        1
        for flag in (has_index, has_retrieve, has_embed, args.preview, args.readme, args.test)
        if flag
    )
    if actions > 1:
        parser.error(
            "--index, --retrieve, --embed, --preview, --readme et --test sont mutuellement exclusifs."
        )


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    _validate_exclusive(parser, args)

    if args.index is not None:
        run_index(
            args.index,
            collection=args.collection,
            source_id=args.source_id,
            embedder=args.embedder,
            store=args.store,
            settings_module=args.settings,
            config_path=str(args.config) if args.config else None,
        )
        return

    if args.retrieve is not None:
        run_retrieve(
            args.retrieve,
            top_k=args.top_k,
            collection=args.collection,
            embedder=args.embedder,
            store=args.store,
            settings_module=args.settings,
            config_path=str(args.config) if args.config else None,
        )
        return

    if args.embed is not None:
        run_embed(
            args.embed,
            embedder=args.embedder,
            settings_module=args.settings,
            config_path=str(args.config) if args.config else None,
        )
        return

    if dispatch_shared_commands(args, PACKAGE_CLI):
        return

    print_default_help(parser)


if __name__ == "__main__":
    main()
