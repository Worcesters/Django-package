"""Point d'entrée CLI : uv run inference [--help] [--preview] [--test]."""

from __future__ import annotations

from base_cmd.package_cli import (
    PackageCliConfig,
    build_package_parser,
    dispatch_shared_commands,
    print_default_help,
    validate_shared_exclusive,
)

from completion.conf import format_settings_help

PACKAGE_CLI = PackageCliConfig(
    prog="inference",
    package_module="completion",
    description="CLI inference : configuration, preview d'architecture et tests Pytest.",
    preview_title="inference — architecture",
    setting_prefix="INFERENCE",
    module_prefix="completion",
    settings_epilog=format_settings_help(),
)


def build_parser():
    return build_package_parser(PACKAGE_CLI)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    validate_shared_exclusive(parser, args)
    if dispatch_shared_commands(args, PACKAGE_CLI):
        return
    print_default_help(parser)


if __name__ == "__main__":
    main()
