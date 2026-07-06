"""Affichage du README dans le terminal."""

from __future__ import annotations

from pathlib import Path

from query_sentinel.terminal import print_readme


def load_readme() -> str:
    module_dir = Path(__file__).resolve().parent
    for candidate in (module_dir / "README.md", module_dir.parent / "README.md"):
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8")
    raise FileNotFoundError(
        "README introuvable. Réinstallez le package ou exécutez depuis le dépôt source."
    )


def run_readme() -> None:
    print_readme(load_readme())
