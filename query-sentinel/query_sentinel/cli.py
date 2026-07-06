"""Point d'entrée CLI : uv run query-sentinel [--help] [--preview] [--status]."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from query_sentinel.conf import format_settings_help
from query_sentinel.preview import KROKI_BASE_URL, run_preview
from query_sentinel.readme import run_readme
from query_sentinel.status_cmd import run_status
from query_sentinel.terminal import print_help


class SentinelArgumentParser(argparse.ArgumentParser):
    """ArgumentParser avec aide colorée."""

    def print_help(self, file: TextIO | None = None) -> None:
        print_help(self.format_help(), file=file or sys.stdout)


def build_parser() -> SentinelArgumentParser:
    parser = SentinelArgumentParser(
        prog="query-sentinel",
        description="CLI query-sentinel : N+1, surveillance SQL, preview architecture.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=format_settings_help(),
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Affiche la configuration active (JSON).",
    )
    parser.add_argument(
        "--settings",
        metavar="MODULE",
        help="Avec --status : module Django settings (ex. config.settings.dev).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        metavar="FICHIER",
        help="Avec --status : fichier JSON standalone (ex. ./sentinel.json).",
    )
    parser.add_argument(
        "--readme",
        action="store_true",
        help="Affiche le README du package (coloré) dans le terminal.",
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
    if args.settings and args.config:
        build_parser().error("--settings et --config sont mutuellement exclusifs.")

    actions = sum(
        1
        for flag in (args.status, args.preview, args.readme)
        if flag not in (None, False)
    )
    if actions > 1:
        build_parser().error("--status, --preview et --readme sont mutuellement exclusifs.")


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    _validate_exclusive(args)

    if args.status:
        run_status(
            settings_module=args.settings,
            config_path=str(args.config) if args.config else None,
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

    if args.readme:
        run_readme()
        return

    print_help(build_parser().format_help())


if __name__ == "__main__":
    main()
