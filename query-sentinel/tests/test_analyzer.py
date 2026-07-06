"""Tests de l'analyseur SQL."""

from __future__ import annotations

from query_sentinel.analyzer import analyze_queries, normalize_sql
from query_sentinel.schemas import QueryRecord


def test_normalize_sql_replaces_literals() -> None:
    sql_a = "SELECT * FROM book WHERE author_id = 1"
    sql_b = "SELECT * FROM book WHERE author_id = 42"
    assert normalize_sql(sql_a) == normalize_sql(sql_b)


def test_analyze_queries_detects_n_plus_one() -> None:
    pattern = "SELECT * FROM book WHERE author_id = ?"
    records = [
        QueryRecord(sql=pattern.replace("?", str(i)), params=(i,))
        for i in range(5)
    ]
    report = analyze_queries(records, threshold=3)
    assert report.n_plus_one_detected is True
    assert report.total_queries == 5
    assert report.redundant_patterns[0].execution_count == 5


def test_analyze_queries_clean_when_below_threshold() -> None:
    records = [
        QueryRecord(sql="SELECT 1"),
        QueryRecord(sql="SELECT 2"),
    ]
    report = analyze_queries(records, threshold=3)
    assert report.n_plus_one_detected is False
