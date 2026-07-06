"""Inspection du payload JSON de la réponse HTTP."""

from __future__ import annotations

import json
from typing import Any

from payload_sentinel.schemas import SensitiveHit


def parse_json_response(content: bytes) -> tuple[Any | None, list[str]]:
    """Décode le JSON et retourne les chemins de champs aplatis."""
    if not content:
        return None, []
    try:
        payload = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, []
    return payload, flatten_field_paths(payload)


def flatten_field_paths(payload: Any, *, prefix: str = "") -> list[str]:
    """Aplati un JSON en chemins de champs (ex: user.email, id)."""
    paths: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            paths.append(path)
            paths.extend(flatten_field_paths(value, prefix=path))
    elif isinstance(payload, list):
        for index, item in enumerate(payload[:5]):
            list_prefix = f"{prefix}[{index}]" if prefix else f"[{index}]"
            paths.extend(flatten_field_paths(item, prefix=list_prefix))
    return paths


def detect_sensitive_fields(
    payload: Any,
    patterns: tuple[str, ...],
    *,
    prefix: str = "",
) -> list[SensitiveHit]:
    """Détecte les champs sensibles dans le JSON (clés et chemins)."""
    hits: list[SensitiveHit] = []
    normalized_patterns = tuple(pattern.lower() for pattern in patterns)

    if isinstance(payload, dict):
        for key, value in payload.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            matched = _match_sensitive_name(str(key), normalized_patterns)
            if matched:
                hits.append(SensitiveHit(field_path=path, matched_pattern=matched))
            hits.extend(detect_sensitive_fields(value, patterns, prefix=path))
    elif isinstance(payload, list):
        for index, item in enumerate(payload[:10]):
            list_prefix = f"{prefix}[{index}]" if prefix else f"[{index}]"
            hits.extend(detect_sensitive_fields(item, patterns, prefix=list_prefix))
    return hits


def _match_sensitive_name(name: str, patterns: tuple[str, ...]) -> str | None:
    lowered = name.lower()
    for pattern in patterns:
        if pattern in lowered:
            return pattern
    return None
