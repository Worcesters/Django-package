"""Tests Pytest pour rag."""

from unittest.mock import patch

from rag.cli import build_parser, main
from rag.conf import (
    SETTING_DEFAULT_EMBEDDER,
    SETTING_EMBEDDERS,
    SETTING_VECTOR_STORES,
    format_settings_help,
)
from rag.preview import build_kroki_preview_url, load_puml
from rag.terminal import colorize_help


def test_load_puml_returns_startuml_block() -> None:
    content = load_puml()
    assert "@startuml" in content
    assert "RagServices" in content


def test_build_kroki_preview_url_points_to_kroki() -> None:
    url = build_kroki_preview_url(load_puml())
    assert url.startswith("https://kroki.io/plantuml/svg/")


def test_help_includes_rag_settings_constants() -> None:
    help_text = build_parser().format_help()
    assert SETTING_DEFAULT_EMBEDDER in help_text
    assert SETTING_EMBEDDERS in help_text
    assert SETTING_VECTOR_STORES in help_text
    assert "--retrieve" in help_text
    assert "--index" in help_text


def test_cli_retrieve_flag_parsing() -> None:
    args = build_parser().parse_args(
        ["--retrieve", "question", "--settings", "tests.settings", "--top-k", "3"]
    )
    assert args.retrieve == "question"
    assert args.top_k == 3


def test_format_settings_help_lists_default_embedders() -> None:
    text = format_settings_help()
    assert "ollama" in text
    assert "openai" in text
    assert "memory" in text


def test_main_rejects_index_and_retrieve_together() -> None:
    try:
        main(["--index", "x", "--retrieve", "y", "--settings", "tests.settings"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("expected SystemExit")


def test_colorize_help_adds_ansi_when_forced(monkeypatch: object) -> None:
    monkeypatch.setenv("FORCE_COLOR", "1")  # type: ignore[attr-defined]
    colored = colorize_help("usage: rag [-h]\n\noptions:\n  --retrieve")
    assert "\033[" in colored
