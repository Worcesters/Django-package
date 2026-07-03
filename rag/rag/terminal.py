"""Couleurs terminal (PowerShell / ANSI) pour la CLI."""

from __future__ import annotations

import os
import re
import sys
from typing import IO, TextIO

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
    if os.environ.get("FORCE_COLOR"):
        _enable_windows_vt()
        return True
    if os.environ.get("NO_COLOR"):
        return False
    is_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    if is_tty:
        _enable_windows_vt()
        return True
    if os.name == "nt" and os.environ.get("WT_SESSION"):
        _enable_windows_vt()
        return True
    return False


def colorize_help(text: str) -> str:
    if not supports_color():
        return text

    colored_lines: list[str] = []
    for line in text.splitlines():
        colored_lines.append(_colorize_help_line(line))

    return "\n".join(colored_lines)


def _colorize_help_line(line: str) -> str:
    stripped = line.strip()

    if line.startswith("usage:"):
        return f"{BOLD}{CYAN}{line}{RESET}"

    if stripped == "options:":
        return f"{BOLD}{YELLOW}{line}{RESET}"

    if any(marker in line for marker in _SECTION_MARKERS):
        return f"{BOLD}{CYAN}{line}{RESET}"

    if re.fullmatch(r"-{3,}", stripped):
        return f"{DIM}{line}{RESET}"

    styled = line
    styled = re.sub(r"\b(RAG_\w+)\b", rf"{BOLD}{MAGENTA}\1{RESET}", styled)
    styled = re.sub(r"\b(OPENAI_API_KEY|MISTRAL_API_KEY)\b", rf"{YELLOW}\1{RESET}", styled)
    styled = re.sub(r"\b(rag\.[\w.]+)\b", rf"{BLUE}\1{RESET}", styled)
    styled = re.sub(r"(\s|^)(-{1,2}[\w-]+)", rf"\1{GREEN}\2{RESET}", styled)
    return styled


def colorize_readme(text: str) -> str:
    """Applique une coloration Markdown lisible pour PowerShell / ANSI."""
    if not supports_color():
        return text

    colored_lines: list[str] = []
    in_code_block = False

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            colored_lines.append(f"{DIM}{line}{RESET}")
            continue

        if in_code_block:
            colored_lines.append(f"{DIM}{line}{RESET}")
            continue

        if stripped.startswith("# "):
            colored_lines.append(f"{BOLD}{CYAN}{line}{RESET}")
            continue
        if stripped.startswith("## "):
            colored_lines.append(f"{BOLD}{GREEN}{line}{RESET}")
            continue
        if stripped.startswith("### "):
            colored_lines.append(f"{BOLD}{YELLOW}{line}{RESET}")
            continue
        if stripped.startswith("#### "):
            colored_lines.append(f"{BOLD}{line}{RESET}")
            continue

        if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", stripped):
            colored_lines.append(f"{DIM}{line}{RESET}")
            continue

        if stripped.startswith(">"):
            colored_lines.append(f"{DIM}{CYAN}{_style_readme_inline(line)}{RESET}")
            continue

        if re.match(r"^(\s*[-*]|\s*\d+\.)\s", line):
            prefix_match = re.match(r"^(\s*(?:[-*]|\d+\.)\s)(.*)$", line)
            if prefix_match:
                prefix, body = prefix_match.groups()
                colored_lines.append(f"{prefix}{GREEN}{_style_readme_inline(body)}{RESET}")
                continue

        if "|" in line and stripped.startswith("|"):
            if re.match(r"^\|\s*-+", stripped):
                colored_lines.append(f"{DIM}{line}{RESET}")
            else:
                colored_lines.append(_style_readme_inline(line))
            continue

        colored_lines.append(_style_readme_inline(line))

    return "\n".join(colored_lines)


def _style_readme_inline(line: str) -> str:
    styled = line
    styled = re.sub(r"\*\*(.+?)\*\*", rf"{BOLD}\1{RESET}", styled)
    styled = re.sub(r"`([^`]+)`", rf"{MAGENTA}\1{RESET}", styled)
    styled = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        rf"{BLUE}\1{RESET}{DIM}(\2){RESET}",
        styled,
    )
    styled = re.sub(r"\b(RAG_\w+)\b", rf"{BOLD}{MAGENTA}\1{RESET}", styled)
    styled = re.sub(r"\b(OPENAI_API_KEY|MISTRAL_API_KEY)\b", rf"{YELLOW}\1{RESET}", styled)
    styled = re.sub(r"\b(rag\.[\w.]+)\b", rf"{BLUE}\1{RESET}", styled)
    styled = re.sub(r"(\s|^)(-{1,2}[\w-]+)", rf"\1{GREEN}\2{RESET}", styled)
    return styled


def print_help(text: str, file: TextIO | None = None) -> None:
    output: IO[str] = file if file is not None else sys.stdout
    help_text = colorize_help(text) if output is sys.stdout else text
    output.write(help_text)
    if not help_text.endswith("\n"):
        output.write("\n")


def print_readme(text: str, file: TextIO | None = None) -> None:
    """Affiche le README avec coloration Markdown si le terminal le permet."""
    output: IO[str] = file if file is not None else sys.stdout
    readme_text = colorize_readme(text) if output is sys.stdout else text
    output.write(readme_text)
    if not readme_text.endswith("\n"):
        output.write("\n")
