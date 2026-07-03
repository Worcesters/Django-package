"""Parsing des réponses API LLM."""

from __future__ import annotations

from typing import Any

from inference.exceptions import ParseError
from inference.schemas import CompletionResult, TokenUsage


def parse_ollama_response(raw: dict[str, Any], *, model: str) -> CompletionResult:
    """Transforme la réponse JSON Ollama /api/chat en CompletionResult."""
    try:
        message = raw["message"]
        text = message["content"]
        if not isinstance(text, str):
            raise TypeError("content is not str")
    except (KeyError, TypeError) as exc:
        raise ParseError(
            "Réponse Ollama invalide : champ message.content absent ou mal formé.",
            provider="llama",
        ) from exc

    prompt_tokens = int(raw.get("prompt_eval_count") or 0)
    completion_tokens = int(raw.get("eval_count") or 0)

    return CompletionResult(
        text=text,
        model=str(raw.get("model") or model),
        usage=TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
        raw=raw,
        finish_reason="stop" if raw.get("done") else "",
    )


def parse_chat_completions_response(
    raw: dict[str, Any],
    *,
    model: str,
    provider: str,
) -> CompletionResult:
    """Transforme une réponse OpenAI-compatible /chat/completions en CompletionResult."""
    try:
        choice = raw["choices"][0]
        message = choice["message"]
        text = message["content"]
        if not isinstance(text, str):
            raise TypeError("content is not str")
        finish_reason = str(choice.get("finish_reason") or "")
    except (KeyError, IndexError, TypeError) as exc:
        raise ParseError(
            "Réponse chat/completions invalide : choices[0].message.content absent.",
            provider=provider,
        ) from exc

    usage_raw = raw.get("usage") or {}
    prompt_tokens = int(usage_raw.get("prompt_tokens") or 0)
    completion_tokens = int(usage_raw.get("completion_tokens") or 0)
    total_tokens = int(usage_raw.get("total_tokens") or prompt_tokens + completion_tokens)

    return CompletionResult(
        text=text,
        model=str(raw.get("model") or model),
        usage=TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        ),
        raw=raw,
        finish_reason=finish_reason,
    )
