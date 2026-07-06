"""Point d'entrée CLI : uv run query-sentinel [--help] [--preview] [--test] [--status]."""

from __future__ import annotations

import argparse

from base_cmd.package_cli import (
    PackageCliConfig,
    build_package_parser,
    dispatch_shared_commands,
    print_default_help,
    validate_shared_exclusive,
)

from query_sentinel.conf import format_settings_help
from query_sentinel.status_cmd import run_status

PACKAGE_CLI = PackageCliConfig(
    prog="query-sentinel",
    package_module="query_sentinel",
    description="CLI query-sentinel : N+1, surveillance SQL, preview architecture.",
    preview_title="query-sentinel — architecture",
    setting_prefix="QUERY_SENTINEL",
    module_prefix="query_sentinel",
    settings_epilog=format_settings_help(),
)


def _register_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--status",
        action="store_true",
        help="Affiche la configuration active (JSON).",
    )


def build_parser():
    return build_package_parser(PACKAGE_CLI, register_args=_register_args)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    validate_shared_exclusive(
        parser,
        args,
        extra_flag_names=("status",),
        message="--status, --preview, --readme et --test sont mutuellement exclusifs.",
    )

    if args.status:
        run_status(
            settings_module=args.settings,
            config_path=str(args.config) if args.config else None,
        )
        return

    if dispatch_shared_commands(args, PACKAGE_CLI):
        return

    print_default_help(parser)


if __name__ == "__main__":
    main()
