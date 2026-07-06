"""Orchestration CLI partagée pour tous les packages hôtes."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from base_cmd.parser import (
    ColoredArgumentParser,
    add_shared_args,
    collect_pytest_args,
    validate_mutually_exclusive,
    validate_settings_config_exclusive,
)
from base_cmd.preview import PreviewConfig, run_preview
from base_cmd.readme import run_readme
from base_cmd.terminal import TerminalStyle
from base_cmd.test_cmd import run_tests


@dataclass(frozen=True)
class PackageCliConfig:
    """Configuration CLI d'un package hôte."""

    prog: str
    package_module: str
    description: str
    preview_title: str
    setting_prefix: str = ""
    module_prefix: str = ""
    header_prefix: str = "X-Django"
    settings_epilog: str = ""

    @property
    def terminal_style(self) -> TerminalStyle:
        return TerminalStyle(
            setting_prefix=self.setting_prefix,
            module_prefix=self.module_prefix or self.package_module,
            header_prefix=self.header_prefix,
        )

    @property
    def preview_config(self) -> PreviewConfig:
        slug = self.prog.replace("-", "_")
        return PreviewConfig(
            package_module=self.package_module,
            title=self.preview_title,
            default_html_name=f"{slug}-architecture-preview.html",
        )


def build_package_parser(
    config: PackageCliConfig,
    *,
    register_args: Callable[[ColoredArgumentParser], None] | None = None,
) -> ColoredArgumentParser:
    """Construit un parser avec les commandes partagées base-cmd."""
    parser = ColoredArgumentParser(
        prog=config.prog,
        description=config.description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=config.settings_epilog or None,
        terminal_style=config.terminal_style,
    )
    if register_args is not None:
        register_args(parser)
    add_shared_args(parser)
    return parser


def validate_shared_exclusive(
    parser: ColoredArgumentParser,
    args: argparse.Namespace,
    *,
    extra_flag_names: tuple[str, ...] = (),
    message: str | None = None,
) -> None:
    """Valide l'exclusivité des commandes partagées + flags métier."""
    validate_settings_config_exclusive(parser, args)
    flag_names = (*extra_flag_names, "preview", "readme", "test")
    default_message = (
        f"{', '.join(f'--{name}' for name in flag_names)} sont mutuellement exclusifs."
    )
    validate_mutually_exclusive(
        parser,
        args,
        flag_names=flag_names,
        message=message or default_message,
    )


def dispatch_shared_commands(
    args: argparse.Namespace,
    config: PackageCliConfig,
) -> bool:
    """Exécute --test, --preview ou --readme. Retourne True si traité."""
    if getattr(args, "test", False):
        run_tests(
            settings_module=getattr(args, "settings", None),
            pytest_args=collect_pytest_args(args),
        )
        return True

    if getattr(args, "preview", False):
        run_preview(
            config.preview_config,
            output=getattr(args, "output", None),
            html_output=getattr(args, "html_output", None),
            no_open=getattr(args, "no_open", False),
            kroki_base_url=getattr(args, "kroki_base_url", "https://kroki.io"),
        )
        return True

    if getattr(args, "readme", False):
        run_readme(config.package_module, style=config.terminal_style)
        return True

    return False


def print_default_help(parser: ColoredArgumentParser) -> None:
    """Affiche l'aide colorée."""
    parser.print_help(file=sys.stdout)
