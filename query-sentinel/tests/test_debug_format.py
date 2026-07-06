"""Tests du formatage debug N+1."""

from __future__ import annotations

import json

from query_sentinel.debug_format import build_debug_header_value, format_n_plus_one_message
from query_sentinel.schemas import QueryOrigin, RedundantPattern
from query_sentinel.schemas import AnalysisReport


def test_format_n_plus_one_message_includes_origin() -> None:
    report = AnalysisReport(
        total_queries=5,
        n_plus_one_detected=True,
        max_redundancy=5,
        redundant_patterns=[
            RedundantPattern(
                normalized_sql="SELECT * FROM book WHERE author_id = ?",
                execution_count=5,
                sample_sql="SELECT * FROM book WHERE author_id = 1",
                threshold=3,
                primary_origin=QueryOrigin(
                    filename="apps/books/views.py",
                    lineno=42,
                    function="list_books",
                ),
            )
        ],
    )
    message = format_n_plus_one_message(report)
    assert "apps/books/views.py:42" in message
    assert "list_books" in message
    assert "SELECT * FROM book" in message


def test_build_debug_header_value_is_valid_json() -> None:
    report = AnalysisReport(
        total_queries=4,
        n_plus_one_detected=True,
        max_redundancy=4,
        redundant_patterns=[
            RedundantPattern(
                normalized_sql="SELECT 1",
                execution_count=4,
                sample_sql="SELECT 1",
                threshold=3,
                primary_origin=QueryOrigin("tests/urls.py", 17, "n_plus_one_view"),
            )
        ],
    )
    payload = json.loads(build_debug_header_value(report))
    assert payload["patterns"][0]["primary_origin"] == "tests/urls.py:17 in n_plus_one_view()"
