"""Commande CLI : test d'une completion LLM."""

from __future__ import annotations

import sys

from completion.exceptions import InferenceError
from completion.schemas import CompletionResult
from completion.settings_source import bootstrap_runtime


def run_complete(
    prompt: str,
    *,
    provider: str | None = None,
    settings_module: str | None = None,
    config_path: str | None = None,
) -> CompletionResult:
    """Exécute une completion et affiche le résultat sur stdout."""
    bootstrap_runtime(settings_module=settings_module, config_path=config_path)

    from completion.services import complete

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
