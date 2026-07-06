"""Schémas de données (records d'analyse SQL)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class QueryRecord:
    """Une requête SQL capturée pendant une requête HTTP ou un test."""

    sql: str
    params: tuple[Any, ...] = ()
    duration_ms: float | None = None
    alias: str = "default"


@dataclass(frozen=True)
class RedundantPattern:
    """Motif SQL répété (suspect N+1)."""

    normalized_sql: str
    execution_count: int
    sample_sql: str
    threshold: int


@dataclass
class AnalysisReport:
    """Rapport d'analyse d'un lot de requêtes SQL."""

    total_queries: int
    n_plus_one_detected: bool
    redundant_patterns: list[RedundantPattern] = field(default_factory=list)
    max_redundancy: int = 0

    @property
    def redundant_count(self) -> int:
        return len(self.redundant_patterns)


@dataclass(frozen=True)
class SentinelConfig:
    """Configuration résolue pour une exécution."""

    enabled: bool = True
    n_plus_one_threshold: int = 3
    max_queries_per_request: int | None = None
    debug_headers: bool = True
    strict_in_tests: bool = False
    structlog_enabled: bool = True
    redundancy_log_threshold: int = 5
    block_on_n_plus_one_staging: bool = False
