"""Point d'entrée CLI : uv run rag [--help] [--preview] [--index] [--retrieve]."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from rag.conf import format_settings_help
from rag.preview import KROKI_BASE_URL, run_preview
from rag.rag_cmd import run_embed, run_index, run_retrieve
from rag.terminal import print_help


class RagArgumentParser(argparse.ArgumentParser):
    """ArgumentParser avec aide colorée."""

    def print_help(self, file: TextIO | None = None) -> None:
        print_help(self.format_help(), file=file or sys.stdout)


def build_parser() -> RagArgumentParser:
    parser = RagArgumentParser(
        prog="rag",
        description="CLI rag : configuration, preview d'architecture et test RAG.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=format_settings_help(),
    )
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
        "--settings",
        metavar="MODULE",
        help="Module Django settings (ex. config.settings.dev).",
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
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Affiche le diagramme PlantUML (viewer HTML zoom/pan via Kroki).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        metavar="FICHIER",
        help="Avec --preview : enregistre aussi le SVG localement.",
    )
    parser.add_argument(
        "--html-output",
        type=Path,
        default=None,
        metavar="FICHIER",
        help="Avec --preview : chemin du viewer HTML (défaut : fichier temp).",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Avec --preview : n'ouvre pas le navigateur.",
    )
    parser.add_argument(
        "--kroki-base-url",
        default=KROKI_BASE_URL,
        help="Avec --preview : URL de base Kroki.",
    )
    return parser


def _validate_exclusive(args: argparse.Namespace) -> None:
    actions = sum(
        1
        for flag in (args.index, args.retrieve, args.embed, args.preview)
        if flag not in (None, False)
    )
    if actions > 1:
        build_parser().error("--index, --retrieve, --embed et --preview sont mutuellement exclusifs.")


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    _validate_exclusive(args)

    if args.index is not None:
        run_index(
            args.index,
            collection=args.collection,
            source_id=args.source_id,
            embedder=args.embedder,
            store=args.store,
            settings_module=args.settings,
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
        )
        return

    if args.embed is not None:
        run_embed(
            args.embed,
            embedder=args.embedder,
            settings_module=args.settings,
        )
        return

    if args.preview:
        run_preview(
            output=args.output,
            html_output=args.html_output,
            no_open=args.no_open,
            kroki_base_url=args.kroki_base_url,
        )
        return

    print_help(build_parser().format_help())


if __name__ == "__main__":
    main()
