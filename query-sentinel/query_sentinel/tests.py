"""Tests Pytest pour query-sentinel."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from base_cmd.docs import load_puml
from base_cmd.preview import build_interactive_html, build_kroki_preview_url
from base_cmd.readme import load_readme
from base_cmd.terminal import colorize_help
from query_sentinel.cli import PACKAGE_CLI, build_parser, main
from query_sentinel.conf import SETTING_ENABLED, format_settings_help


def test_load_puml_returns_startuml_block() -> None:
    content = load_puml(PACKAGE_CLI.package_module)
    assert "@startuml" in content
    assert "QuerySentinelMiddleware" in content


def test_build_kroki_preview_url_points_to_kroki() -> None:
    url = build_kroki_preview_url(load_puml(PACKAGE_CLI.package_module))
    assert url.startswith("https://kroki.io/plantuml/svg/")


def test_help_includes_sentinel_constants() -> None:
    help_text = build_parser().format_help()
    assert SETTING_ENABLED in help_text
    assert "--status" in help_text
    assert "--test" in help_text
    assert "--config" in help_text
    assert "--readme" in help_text


def test_cli_status_flag_parsing() -> None:
    args = build_parser().parse_args(["--status", "--config", "sentinel.json"])
    assert args.status is True
    assert args.config == Path("sentinel.json")


def test_main_rejects_status_and_preview() -> None:
    try:
        main(["--status", "--preview"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("expected SystemExit")


def test_main_rejects_status_and_test() -> None:
    try:
        main(["--status", "--test"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("expected SystemExit")


def test_load_readme_returns_markdown() -> None:
    content = load_readme(PACKAGE_CLI.package_module)
    assert content.startswith("# query-sentinel")


def test_build_interactive_html_includes_controls() -> None:
    html_page = build_interactive_html('<svg xmlns="http://www.w3.org/2000/svg"></svg>', title="t")
    assert "zoom-in" in html_page


def test_format_settings_help_lists_headers() -> None:
    text = format_settings_help()
    assert "X-Django-SQL-Count" in text
    assert "X-Django-N-Plus-One-Source" in text


@patch("query_sentinel.status_cmd.bootstrap_runtime")
@patch("query_sentinel.status_cmd.get_sentinel_config")
def test_run_status_prints_json(mock_config: object, mock_bootstrap: object, capsys: object) -> None:
    from query_sentinel.schemas import SentinelConfig
    from query_sentinel.status_cmd import run_status

    mock_config.return_value = SentinelConfig(enabled=True, n_plus_one_threshold=3)  # type: ignore[attr-defined]
    run_status(config_path="sentinel.json")
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert '"enabled": true' in captured.out
    mock_bootstrap.assert_called_once()  # type: ignore[attr-defined]


def test_colorize_help_adds_ansi_when_forced(monkeypatch: object) -> None:
    monkeypatch.setenv("FORCE_COLOR", "1")  # type: ignore[attr-defined]
    colored = colorize_help(
        "usage: query-sentinel [-h]\n\noptions:\n  --status",
        style=PACKAGE_CLI.terminal_style,
    )
    assert "\033[" in colored
