"""Tests Pytest pour inference."""

from unittest.mock import patch

from app.cli import build_parser, main
from app.complete_cmd import run_complete
from app.conf import SETTING_DEFAULT_PROVIDER, SETTING_PROVIDERS, format_settings_help
from app.factory import llm_factory
from app.preview import build_kroki_preview_url, load_puml
from app.schemas import CompletionResult, TokenUsage


def test_load_puml_returns_startuml_block() -> None:
    content = load_puml()
    assert "@startuml" in content
    assert "@enduml" in content
    assert "LLMProvider" in content


def test_build_kroki_preview_url_points_to_kroki() -> None:
    url = build_kroki_preview_url(load_puml())
    assert url.startswith("https://kroki.io/plantuml/svg/")
    assert len(url) > len("https://kroki.io/plantuml/svg/")


def test_help_includes_settings_constants() -> None:
    help_text = build_parser().format_help()
    assert SETTING_DEFAULT_PROVIDER in help_text
    assert SETTING_PROVIDERS in help_text
    assert "OPENAI_API_KEY" in help_text
    assert "--preview" in help_text


def test_cli_preview_flag_parsing() -> None:
    args = build_parser().parse_args(["--preview", "--no-open"])
    assert args.preview is True
    assert args.no_open is True


def test_cli_complete_flag_parsing() -> None:
    args = build_parser().parse_args(
        ["--complete", "Bonjour", "--provider", "llama", "--settings", "tests.settings"]
    )
    assert args.complete == "Bonjour"
    assert args.provider == "llama"
    assert args.settings == "tests.settings"


def test_help_includes_complete_flag() -> None:
    help_text = build_parser().format_help()
    assert "--complete" in help_text
    assert "--settings" in help_text


@patch("app.services.complete")
@patch("app.complete_cmd.setup_django")
def test_run_complete_prints_text(
    mock_setup: object,
    mock_complete: object,
) -> None:
    mock_complete.return_value = CompletionResult(  # type: ignore[attr-defined]
        text="Salut !",
        model="llama3.2",
        usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        finish_reason="stop",
    )
    result = run_complete("Bonjour", provider="llama", settings_module="tests.settings")
    assert result.text == "Salut !"


def test_main_rejects_complete_and_preview_together(capsys: object) -> None:
    try:
        main(["--complete", "x", "--preview", "--settings", "tests.settings"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("expected SystemExit")


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