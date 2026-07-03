"""Types partagés (config, résultats d'inférence)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 1024
    timeout: int = 60
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass(frozen=True)
class CompletionResult:
    text: str
    model: str
    usage: TokenUsage = field(default_factory=TokenUsage)
    raw: dict[str, Any] = field(default_factory=dict)
    finish_reason: str = ""
