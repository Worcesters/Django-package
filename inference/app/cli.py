"""Point d'entrée CLI : uv run inference [--help] [--preview]."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.conf import format_settings_help
from app.preview import KROKI_BASE_URL, run_preview


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inference",
        description="CLI inference : configuration et preview d'architecture.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=format_settings_help(),
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Affiche le diagramme PlantUML embarqué (rendu SVG via Kroki).",
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

    if args.preview:
        run_preview(
            output=args.output,
            no_open=args.no_open,
            kroki_base_url=args.kroki_base_url,
        )
        return

    build_parser().print_help()


if __name__ == "__main__":
    main()
