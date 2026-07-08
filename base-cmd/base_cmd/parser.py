"""Arguments CLI partagés (--readme, --preview, --test, --settings, --config)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, TextIO

from base_cmd.preview import KROKI_BASE_URL
from base_cmd.terminal import TerminalStyle, print_help


class ColoredArgumentParser(argparse.ArgumentParser):
    """ArgumentParser avec aide colorée et style terminal configurable."""

    def __init__(
        self,
        *args: Any,
        terminal_style: TerminalStyle | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.terminal_style = terminal_style

    def print_help(self, file: TextIO | None = None) -> None:
        print_help(
            self.format_help(),
            file=file or sys.stdout,
            style=self.terminal_style,
        )


def add_config_args(parser: argparse.ArgumentParser) -> None:
    """Ajoute --settings et --config."""
    parser.add_argument(
        "--settings",
        metavar="MODULE",
        help="Module Django settings (ex. config.settings.dev).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        metavar="FICHIER",
        help="Fichier JSON standalone (ex. ./config.json).",
    )


def add_readme_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--readme",
        action="store_true",
        help="Affiche le README du package (coloré) dans le terminal.",
    )


def add_test_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--test",
        action="store_true",
        help=(
            "Lance pytest. Mettez --settings/--config avant les filtres pytest. "
            "Ex : --test --settings config.settings.dev -- -k test_foo -v"
        ),
    )
    parser.add_argument(
        "pytest_remainder",
        nargs=argparse.REMAINDER,
        help=argparse.SUPPRESS,
    )


def add_preview_args(parser: argparse.ArgumentParser) -> None:
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


def add_shared_args(parser: argparse.ArgumentParser) -> None:
    """Regroupe les arguments communs à tous les packages."""
    add_readme_arg(parser)
    add_preview_args(parser)
    add_config_args(parser)
    add_test_arg(parser)  # REMAINDER en dernier


def validate_settings_config_exclusive(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if getattr(args, "settings", None) and getattr(args, "config", None):
        parser.error("--settings et --config sont mutuellement exclusifs.")


def validate_mutually_exclusive(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
    *,
    flag_names: tuple[str, ...],
    message: str,
) -> None:
    active = sum(1 for name in flag_names if getattr(args, name, False))
    if active > 1:
        parser.error(message)


def collect_pytest_args(args: argparse.Namespace) -> list[str]:
    """Extrait les arguments pytest passés après --test."""
    remainder = list(getattr(args, "pytest_remainder", []) or [])
    if remainder and remainder[0] == "--":
        remainder = remainder[1:]

    _reject_cli_flags_in_pytest_remainder(remainder)

    if not remainder:
        return ["-q"]

    if len(remainder) == 1 and not remainder[0].startswith("-"):
        return ["-q", "-k", remainder[0]]

    return remainder


def _reject_cli_flags_in_pytest_remainder(remainder: list[str]) -> None:
    """Bloque si --settings/--config ont été avalés par le REMAINDER pytest."""
    leaked = [token for token in remainder if token in ("--settings", "--config")]
    if not leaked:
        return
    message = (
        "Erreur : --settings et --config doivent être placés AVANT les arguments pytest.\n"
        "  Correct : uv run inference --test --settings config.settings.dev\n"
        "  Filtre  : uv run inference --test --settings config.settings.dev -- -k test_foo -v\n"
        '  Incorrect : uv run inference --test "mon test" --settings config.settings.dev'
    )
    print(message, file=sys.stderr)
    raise SystemExit(1)
