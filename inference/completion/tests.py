"""Tests Pytest pour inference."""

from unittest.mock import patch

import sys
from pathlib import Path

from completion.cli import PACKAGE_CLI, build_parser, main
from completion.complete_cmd import run_complete
from completion.conf import SETTING_DEFAULT_PROVIDER, SETTING_PROVIDERS, format_settings_help
from completion.factory import llm_factory
from base_cmd.preview import build_interactive_html, build_kroki_preview_url
from base_cmd.readme import load_readme
from base_cmd.docs import load_puml
from base_cmd.terminal import colorize_help, colorize_readme
from completion.schemas import CompletionResult, TokenUsage


def test_load_puml_returns_startuml_block() -> None:
    content = load_puml(PACKAGE_CLI.package_module)
    assert "@startuml" in content
    assert "@enduml" in content
    assert "LLMProvider" in content


def test_build_kroki_preview_url_points_to_kroki() -> None:
    url = build_kroki_preview_url(load_puml(PACKAGE_CLI.package_module))
    assert url.startswith("https://kroki.io/plantuml/svg/")
    assert len(url) > len("https://kroki.io/plantuml/svg/")


def test_help_includes_settings_constants() -> None:
    help_text = build_parser().format_help()
    assert SETTING_DEFAULT_PROVIDER in help_text
    assert SETTING_PROVIDERS in help_text
    assert "OPENAI_API_KEY" in help_text
    assert "--preview" in help_text


def test_build_interactive_html_includes_pan_zoom_controls() -> None:
    html_page = build_interactive_html('<svg xmlns="http://www.w3.org/2000/svg"></svg>', title="test")
    assert "zoom-in" in html_page
    assert "fitToView" in html_page
    assert "Molette : zoom" in html_page


def test_cli_preview_flag_parsing() -> None:
    args = build_parser().parse_args(["--preview", "--no-open"])
    assert args.preview is True
    assert args.no_open is True


def test_cli_test_flag_parsing() -> None:
    args = build_parser().parse_args(
        ["--test", "--settings", "tests.settings"]
    )
    assert args.test is True
    assert args.settings == "tests.settings"


def test_help_includes_test_flag() -> None:
    help_text = build_parser().format_help()
    assert "--test" in help_text
    assert "--settings" in help_text
    assert "--config" in help_text


def test_cli_config_flag_parsing() -> None:
    args = build_parser().parse_args(
        ["--test", "--config", "inference.json"]
    )
    assert args.test is True
    assert args.config == Path("inference.json")


def test_main_rejects_settings_and_config_together() -> None:
    try:
        main(["--test", "--settings", "tests.settings", "--config", "x.json"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("expected SystemExit")


@patch("completion.complete_cmd.bootstrap_runtime")
@patch("completion.services.complete")
def test_run_complete_prints_text(
    mock_complete: object,
    mock_bootstrap: object,
) -> None:
    mock_complete.return_value = CompletionResult(  # type: ignore[attr-defined]
        text="Salut !",
        model="llama3.2",
        usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        finish_reason="stop",
    )
    result = run_complete("Bonjour", provider="llama", settings_module="tests.settings")
    assert result.text == "Salut !"
    mock_bootstrap.assert_called_once()  # type: ignore[attr-defined]


def test_ensure_project_on_path_inserts_cwd(monkeypatch: object, tmp_path: object) -> None:
    from pathlib import Path

    from completion.settings_source import _ensure_project_on_path

    workdir = Path(tmp_path)  # type: ignore[arg-type]
    monkeypatch.chdir(workdir)  # type: ignore[attr-defined]
    original_path = sys.path.copy()
    sys.path.clear()
    sys.path.extend(original_path)

    _ensure_project_on_path()

    assert str(workdir.resolve()) in sys.path


def test_main_rejects_test_and_preview_together() -> None:
    try:
        main(["--test", "--preview", "--settings", "tests.settings"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("expected SystemExit")


def test_help_includes_readme_flag() -> None:
    help_text = build_parser().format_help()
    assert "--readme" in help_text


def test_cli_readme_flag_parsing() -> None:
    args = build_parser().parse_args(["--readme"])
    assert args.readme is True


def test_load_readme_returns_markdown() -> None:
    content = load_readme(PACKAGE_CLI.package_module)
    assert content.startswith("# inference")


def test_colorize_readme_adds_ansi_when_forced(monkeypatch: object) -> None:
    monkeypatch.setenv("FORCE_COLOR", "1")  # type: ignore[attr-defined]
    monkeypatch.delenv("NO_COLOR", raising=False)  # type: ignore[attr-defined]
    colored = colorize_readme(load_readme(PACKAGE_CLI.package_module))
    assert "\033[" in colored
    assert "# inference" in colored or "inference" in colored


@patch("base_cmd.readme._print_readme")
def test_main_readme_flag(mock_print: object) -> None:
    main(["--readme"])
    mock_print.assert_called_once()  # type: ignore[attr-defined]


def test_main_rejects_test_and_readme_together() -> None:
    try:
        main(["--test", "--readme"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("expected SystemExit")


def test_colorize_help_disabled_with_no_color(monkeypatch: object) -> None:
    monkeypatch.setenv("NO_COLOR", "1")  # type: ignore[attr-defined]
    monkeypatch.delenv("FORCE_COLOR", raising=False)  # type: ignore[attr-defined]
    raw = build_parser().format_help()
    assert colorize_help(raw, style=PACKAGE_CLI.terminal_style) == raw


def test_colorize_help_adds_ansi_when_forced(monkeypatch: object) -> None:
    monkeypatch.setenv("FORCE_COLOR", "1")  # type: ignore[attr-defined]
    monkeypatch.delenv("NO_COLOR", raising=False)  # type: ignore[attr-defined]
    colored = colorize_help(
        "usage: inference [-h]\n\noptions:\n  --test",
        style=PACKAGE_CLI.terminal_style,
    )
    assert "\033[" in colored
    assert "usage:" in colored


def test_format_settings_help_lists_default_providers() -> None:
    text = format_settings_help()
    assert "openai" in text
    assert "mistral" in text
    assert "llama" in text


def test_llm_factory_resolves_openai_provider() -> None:
    provider = llm_factory.get_provider(
        "openai",
        {"model": "gpt-4o"},
        cache_instance=False,
    )
    assert provider.provider_id == "openai"


def test_llm_factory_accepts_legacy_app_backend_path() -> None:
    llm_factory.register(
        "legacy_mistral",
        "app.providers.mistral.MistralProvider",
    )
    provider = llm_factory.get_provider(
        "legacy_mistral",
        {"model": "mistral-small"},
        cache_instance=False,
    )
    assert provider.provider_id == "mistral"