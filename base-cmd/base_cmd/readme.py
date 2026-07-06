"""Affichage du README d'un package hôte."""

from __future__ import annotations

from base_cmd.docs import load_readme as _load_readme
from base_cmd.terminal import TerminalStyle, print_readme as _print_readme


def load_readme(package_module: str) -> str:
    return _load_readme(package_module)


def run_readme(
    package_module: str,
    *,
    style: TerminalStyle | None = None,
) -> None:
    """Affiche le README coloré dans le terminal."""
    _print_readme(_load_readme(package_module), style=style)
