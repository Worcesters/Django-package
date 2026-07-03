"""Commande CLI : test d'une completion LLM."""

from __future__ import annotations

import os
import sys

from app.exceptions import InferenceError
from app.schemas import CompletionResult


def setup_django(settings_module: str | None) -> None:
    """Initialise Django pour lire INFERENCE_* depuis les settings du projet hôte."""
    import django

    module = settings_module or os.environ.get("DJANGO_SETTINGS_MODULE")
    if not module:
        msg = (
            "DJANGO_SETTINGS_MODULE requis pour --complete.\n"
            "  Exemple : uv run inference --complete \"Bonjour\" --settings config.settings.dev\n"
            "  Ou export DJANGO_SETTINGS_MODULE=config.settings.dev"
        )
        raise SystemExit(msg)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", module)
    django.setup()


def run_complete(
    prompt: str,
    *,
    provider: str | None = None,
    settings_module: str | None = None,
) -> CompletionResult:
    """Exécute une completion et affiche le résultat sur stdout."""
    setup_django(settings_module)

    from app.services import complete

    try:
        result = complete(
            messages=[{"role": "user", "content": prompt}],
            provider=provider,
        )
    except InferenceError as exc:
        print(f"Erreur [{exc.code}]: {exc.message}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(result.text)
    if result.usage.total_tokens:
        meta = (
            f"model={result.model} | "
            f"tokens={result.usage.total_tokens} "
            f"(prompt={result.usage.prompt_tokens}, "
            f"completion={result.usage.completion_tokens})"
        )
        if result.finish_reason:
            meta += f" | finish={result.finish_reason}"
        print(f"\n--- {meta}", file=sys.stderr)

    return result
