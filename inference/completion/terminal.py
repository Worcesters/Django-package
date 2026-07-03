"""Couleurs terminal (PowerShell / ANSI) pour la CLI."""

from __future__ import annotations

import os
import re
import sys

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"

_SECTION_MARKERS = (
    "Configuration Django",
    "Constantes requises",
    "Snippet à copier",
    "Variables d'environnement",
    "Installe aussi",
)


def _enable_windows_vt() -> None:
    if os.name != "nt":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            enable_vt = 0x0004
            kernel32.SetConsoleMode(handle, mode.value | enable_vt)
    except (AttributeError, OSError, ValueError):
        return


def supports_color() -> bool:
    """True si stdout supporte les séquences ANSI (PowerShell, Windows Terminal, etc.)."""
    if os.environ.get("NO_COLOR"):
        return False
    is_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    if not is_tty and not os.environ.get("FORCE_COLOR"):
        return False
    _enable_windows_vt()
    return True


def colorize_help(text: str) -> str:
    """Applique une coloration lisible sur le texte d'aide argparse."""
    if not supports_color():
        return text

    colored_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()

        if line.startswith("usage:"):
            colored_lines.append(f"{BOLD}{CYAN}{line}{RESET}")
            continue

        if stripped == "options:":
            colored_lines.append(f"{BOLD}{YELLOW}{line}{RESET}")
            continue

        if any(marker in line for marker in _SECTION_MARKERS):
            colored_lines.append(f"{BOLD}{CYAN}{line}{RESET}")
            continue

        if re.fullmatch(r"-{3,}", stripped):
            colored_lines.append(f"{DIM}{line}{RESET}")
            continue

        styled = line
        styled = re.sub(r"\b(INFERENCE_\w+)\b", rf"{BOLD}{MAGENTA}\1{RESET}", styled)
        styled = re.sub(r"\b(OPENAI_API_KEY|MISTRAL_API_KEY)\b", rf"{YELLOW}\1{RESET}", styled)
        styled = re.sub(r"\b(completion\.[\w.]+)\b", rf"{BLUE}\1{RESET}", styled)
        styled = re.sub(r"(\s|^)(-{1,2}[\w-]+)", rf"\1{GREEN}\2{RESET}", styled)
        colored_lines.append(styled)

    return "\n".join(colored_lines)


def print_help(text: str) -> None:
    """Affiche l'aide CLI avec couleurs si le terminal le permet."""
    print(colorize_help(text))
