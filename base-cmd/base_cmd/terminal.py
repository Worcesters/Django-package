"""Couleurs terminal (PowerShell / ANSI) pour la CLI partagée."""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
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
    "Configuration standalone",
    "Constantes",
    "Snippet",
    "Snippet à copier",
    "Variables d'environnement",
    "Installe aussi",
)


@dataclass(frozen=True)
class TerminalStyle:
    """Motifs de coloration spécifiques au package hôte."""

    setting_prefix: str = ""
    module_prefix: str = ""
    header_prefix: str = "X-Django"


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
    except (AttributeError, OSError, ValueError, SyntaxError):
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


def colorize_help(text: str, *, style: TerminalStyle | None = None) -> str:
    if not supports_color():
        return text
    return "\n".join(_colorize_help_line(line, style=style) for line in text.splitlines())


def _colorize_help_line(line: str, *, style: TerminalStyle | None) -> str:
    stripped = line.strip()
    if line.startswith("usage:"):
        return f"{BOLD}{CYAN}{line}{RESET}"
    if stripped == "options:":
        return f"{BOLD}{YELLOW}{line}{RESET}"
    if any(marker in line for marker in _SECTION_MARKERS):
        return f"{BOLD}{CYAN}{line}{RESET}"
    if re.fullmatch(r"-{3,}", stripped):
        return f"{DIM}{line}{RESET}"
    styled = _apply_style_patterns(line, style=style)
    styled = re.sub(r"(\s|^)(-{1,2}[\w-]+)", rf"\1{GREEN}\2{RESET}", styled)
    return styled


def colorize_readme(text: str, *, style: TerminalStyle | None = None) -> str:
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
        colored_lines.append(_style_readme_inline(line, style=style))
    return "\n".join(colored_lines)


def _style_readme_inline(line: str, *, style: TerminalStyle | None) -> str:
    styled = line
    styled = re.sub(r"\*\*(.+?)\*\*", rf"{BOLD}\1{RESET}", styled)
    styled = re.sub(r"`([^`]+)`", rf"{MAGENTA}\1{RESET}", styled)
    styled = _apply_style_patterns(styled, style=style)
    styled = re.sub(r"(\s|^)(-{1,2}[\w-]+)", rf"\1{GREEN}\2{RESET}", styled)
    return styled


def _apply_style_patterns(text: str, *, style: TerminalStyle | None) -> str:
    styled = text
    if style and style.setting_prefix:
        pattern = rf"\b({re.escape(style.setting_prefix)}_\w+)\b"
        styled = re.sub(pattern, rf"{BOLD}{MAGENTA}\1{RESET}", styled)
    else:
        styled = re.sub(
            r"\b([A-Z][A-Z0-9]*_[A-Z0-9_]+)\b",
            rf"{BOLD}{MAGENTA}\1{RESET}",
            styled,
        )
    header_pattern = (
        rf"\b({re.escape(style.header_prefix)}-[A-Za-z-]+)\b"
        if style
        else r"\b(X-Django-[A-Za-z-]+)\b"
    )
    styled = re.sub(header_pattern, rf"{YELLOW}\1{RESET}", styled)
    if style and style.module_prefix:
        module_pattern = rf"\b({re.escape(style.module_prefix)}\.[\w.]+)\b"
        styled = re.sub(module_pattern, rf"{BLUE}\1{RESET}", styled)
    return styled


def print_help(
    text: str,
    file: TextIO | None = None,
    *,
    style: TerminalStyle | None = None,
) -> None:
    output: IO[str] = file if file is not None else sys.stdout
    help_text = colorize_help(text, style=style) if output is sys.stdout else text
    output.write(help_text)
    if not help_text.endswith("\n"):
        output.write("\n")


def print_readme(
    text: str,
    file: TextIO | None = None,
    *,
    style: TerminalStyle | None = None,
) -> None:
    output: IO[str] = file if file is not None else sys.stdout
    readme_text = colorize_readme(text, style=style) if output is sys.stdout else text
    output.write(readme_text)
    if not readme_text.endswith("\n"):
        output.write("\n")
