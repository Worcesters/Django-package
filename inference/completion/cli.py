"""Point d'entrée CLI : uv run inference [--help] [--preview] [--complete]."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from completion.complete_cmd import run_complete
from completion.conf import format_settings_help
from completion.preview import KROKI_BASE_URL, run_preview
from completion.terminal import print_help


class InferenceArgumentParser(argparse.ArgumentParser):
    """ArgumentParser avec aide colorée (-h / --help inclus)."""

    def print_help(self, file: TextIO | None = None) -> None:
        print_help(self.format_help(), file=file or sys.stdout)


def build_parser() -> InferenceArgumentParser:
    parser = InferenceArgumentParser(
        prog="inference",
        description="CLI inference : configuration, preview d'architecture et test de completion.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=format_settings_help(),
    )
    parser.add_argument(
        "--complete",
        "-c",
        metavar="PROMPT",
        help="Envoie un message au provider configuré et affiche la réponse.",
    )
    parser.add_argument(
        "--provider",
        metavar="NOM",
        help="Avec --complete : provider à utiliser (sinon INFERENCE_DEFAULT_PROVIDER).",
    )
    parser.add_argument(
        "--settings",
        metavar="MODULE",
        help="Avec --complete : module Django settings (ex. config.settings.dev).",
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
        help="Avec --preview : n'ouvre pas le navigateur (affiche l'URL Kroki).",
    )
    parser.add_argument(
        "--kroki-base-url",
        default=KROKI_BASE_URL,
        help="Avec --preview : URL de base du service Kroki (défaut : kroki.io).",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    if args.complete is not None:
        if args.preview:
            build_parser().error("--complete et --preview sont mutuellement exclusifs.")
        run_complete(
            args.complete,
            provider=args.provider,
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
