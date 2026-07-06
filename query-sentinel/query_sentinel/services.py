"""Logique métier — analyse et application des politiques SQL."""

from __future__ import annotations

from query_sentinel.analyzer import analyze_queries
from query_sentinel.exceptions import NPlusOneError, QueryBudgetExceededError
from query_sentinel.schemas import AnalysisReport, QueryRecord, SentinelConfig


def build_analysis_report(
    records: list[QueryRecord],
    config: SentinelConfig,
) -> AnalysisReport:
    """Analyse les requêtes capturées selon la configuration active."""
    return analyze_queries(
        records,
        threshold=config.n_plus_one_threshold,
    )


def enforce_policies(
    report: AnalysisReport,
    config: SentinelConfig,
    *,
    strict: bool | None = None,
) -> None:
    """
    Applique les politiques strictes (tests, staging).

    Lève NPlusOneError ou QueryBudgetExceededError si seuils dépassés.
    """
    is_strict = config.strict_in_tests if strict is None else strict

    if report.n_plus_one_detected and (is_strict or config.block_on_n_plus_one_staging):
        top = report.redundant_patterns[0]
        raise NPlusOneError(
            f"N+1 détecté : {top.execution_count}x le motif « {top.normalized_sql[:120]}… » "
            f"(seuil={top.threshold}).",
            component="analyzer",
        )

    if config.max_queries_per_request is not None:
        if report.total_queries > config.max_queries_per_request and is_strict:
            raise QueryBudgetExceededError(
                f"{report.total_queries} requêtes SQL > budget {config.max_queries_per_request}.",
                component="budget",
            )


def should_log_redundancy(report: AnalysisReport, config: SentinelConfig) -> bool:
    """True si le rapport mérite un log structuré en production."""
    return (
        config.structlog_enabled
        and report.max_redundancy >= config.redundancy_log_threshold
    )
