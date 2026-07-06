"""Compare colonnes SQL récupérées et champs JSON effectivement renvoyés."""

from __future__ import annotations

from payload_sentinel.response_inspector import detect_sensitive_fields
from payload_sentinel.schemas import PayloadAnalysisReport, PayloadSentinelConfig, SqlCapture


def analyze_payload(
    captures: list[SqlCapture],
    *,
    response_payload: object | None,
    response_paths: list[str],
    config: PayloadSentinelConfig,
) -> PayloadAnalysisReport:
    """Construit le rapport de sur-sélection et de fuite de données."""
    fetched_columns = _aggregate_fetched_columns(captures)
    response_paths_unique = sorted(set(response_paths))
    used, unused = _partition_columns(fetched_columns, response_paths_unique)

    overfetch_ratio = len(unused) / len(fetched_columns) if fetched_columns else 0.0
    overfetch_detected = (
        bool(fetched_columns)
        and bool(response_paths_unique)
        and overfetch_ratio >= config.overfetch_threshold
    )

    sensitive_hits: list = []
    if response_payload is not None and config.sensitive_fields:
        sensitive_hits = detect_sensitive_fields(response_payload, config.sensitive_fields)

    return PayloadAnalysisReport(
        sql_columns_fetched=fetched_columns,
        response_field_paths=response_paths_unique,
        unused_columns=unused,
        used_columns=used,
        overfetch_ratio=round(overfetch_ratio, 4),
        overfetch_detected=overfetch_detected,
        sensitive_hits=sensitive_hits,
        sensitive_leak_detected=bool(sensitive_hits),
        response_parsed=response_payload is not None,
    )


def _aggregate_fetched_columns(captures: list[SqlCapture]) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for capture in captures:
        for column in capture.columns:
            if column.wildcard:
                label = f"{column.table}.*" if column.table else "*"
            else:
                label = column.column
            if label in seen:
                continue
            seen.add(label)
            names.append(label)
    return names


def _partition_columns(
    fetched_columns: list[str],
    response_paths: list[str],
) -> tuple[list[str], list[str]]:
    if not fetched_columns:
        return [], []

    response_tokens = _response_tokens(response_paths)
    used: list[str] = []
    unused: list[str] = []

    for column in fetched_columns:
        if column.endswith(".*") or column == "*":
            unused.append(column)
            continue
        leaf = column.split(".")[-1].lower()
        if leaf in response_tokens:
            used.append(column)
        else:
            unused.append(column)
    return used, unused


def _response_tokens(response_paths: list[str]) -> set[str]:
    tokens: set[str] = set()
    for path in response_paths:
        for part in path.replace("[", ".").replace("]", ".").split("."):
            cleaned = part.strip()
            if cleaned and not cleaned.isdigit():
                tokens.add(cleaned.lower())
    return tokens
