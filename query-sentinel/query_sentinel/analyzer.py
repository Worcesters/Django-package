"""Analyse des requêtes SQL — détection N+1 et redondances."""

from __future__ import annotations

import re
from collections import Counter, defaultdict

from query_sentinel.schemas import AnalysisReport, QueryOrigin, QueryRecord, RedundantPattern

_STRING_LITERAL = re.compile(r"'(?:''|[^'])*'")
_NUMERIC_LITERAL = re.compile(r"\b\d+(?:\.\d+)?\b")
_WHITESPACE = re.compile(r"\s+")


def normalize_sql(sql: str) -> str:
    """
    Normalise une requête SQL pour comparer la structure (pas les paramètres).

    Remplace littéraux et nombres par des placeholders.
    """
    collapsed = _WHITESPACE.sub(" ", sql.strip())
    without_strings = _STRING_LITERAL.sub("?", collapsed)
    return _NUMERIC_LITERAL.sub("?", without_strings)


def analyze_queries(
    records: list[QueryRecord],
    *,
    threshold: int = 3,
) -> AnalysisReport:
    """Détecte les motifs SQL répétés au-delà du seuil (N+1)."""
    if not records:
        return AnalysisReport(
            total_queries=0,
            n_plus_one_detected=False,
            redundant_patterns=[],
            max_redundancy=0,
        )

    counter: Counter[str] = Counter()
    samples: dict[str, str] = {}
    origins_by_pattern: dict[str, list[QueryOrigin]] = defaultdict(list)

    for record in records:
        key = normalize_sql(record.sql)
        counter[key] += 1
        samples.setdefault(key, record.sql)
        if record.origin is not None:
            origins_by_pattern[key].append(record.origin)

    redundant: list[RedundantPattern] = []
    max_redundancy = 0
    for normalized, count in counter.items():
        max_redundancy = max(max_redundancy, count)
        if count >= threshold:
            unique_origins = _dedupe_origins(origins_by_pattern.get(normalized, []))
            redundant.append(
                RedundantPattern(
                    normalized_sql=normalized,
                    execution_count=count,
                    sample_sql=samples[normalized],
                    threshold=threshold,
                    primary_origin=unique_origins[0] if unique_origins else None,
                    origins=tuple(unique_origins[:5]),
                )
            )

    redundant.sort(key=lambda item: item.execution_count, reverse=True)
    return AnalysisReport(
        total_queries=len(records),
        n_plus_one_detected=bool(redundant),
        redundant_patterns=redundant,
        max_redundancy=max_redundancy,
    )


def _dedupe_origins(origins: list[QueryOrigin]) -> list[QueryOrigin]:
    seen: set[tuple[str, int, str]] = set()
    unique: list[QueryOrigin] = []
    for origin in origins:
        key = (origin.filename, origin.lineno, origin.function)
        if key in seen:
            continue
        seen.add(key)
        unique.append(origin)
    return unique
