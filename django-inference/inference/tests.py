"""Tests Pytest pour inference."""

import pytest
from rest_framework.test import APIClient

from inference.conf import SETTING_DEFAULT_PROVIDER, SETTING_PROVIDERS, format_settings_help
from inference.factory import llm_factory
from inference.preview import build_kroki_preview_url, build_parser, load_puml


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


@pytest.mark.django_db
def test_health_requires_auth() -> None:
    client = APIClient()
    response = client.get("/api/inference/health/")
    assert response.status_code in (401, 403)