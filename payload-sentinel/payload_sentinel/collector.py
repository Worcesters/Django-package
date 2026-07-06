"""Collecte SQL via execute_wrapper — extraction des colonnes SELECT."""

from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Callable, Iterator

from django.db import connections

from payload_sentinel.schemas import SqlCapture
from payload_sentinel.sql_parser import extract_columns_from_sql

_active_captures: ContextVar[list[SqlCapture] | None] = ContextVar(
    "payload_sentinel_captures",
    default=None,
)


@contextmanager
def sql_column_collection() -> Iterator[list[SqlCapture]]:
    """Capture les requêtes SELECT et leurs colonnes pendant une requête HTTP."""
    captures: list[SqlCapture] = []
    token = _active_captures.set(captures)
    contexts: list[Any] = []

    try:
        for connection in connections.all():
            wrapper = _build_wrapper(captures)
            contexts.append(connection.execute_wrapper(wrapper))
            contexts[-1].__enter__()
        yield captures
    finally:
        for ctx in reversed(contexts):
            ctx.__exit__(None, None, None)
        _active_captures.reset(token)


def _build_wrapper(captures: list[SqlCapture]) -> Callable[..., Any]:
    def wrapper(
        execute: Callable[..., Any],
        sql: str,
        params: Any,
        many: bool,
        context: dict[str, Any],
    ) -> Any:
        start = time.perf_counter()
        result = execute(sql, params, many, context)
        _ = (time.perf_counter() - start) * 1000.0
        columns = extract_columns_from_sql(sql)
        if columns:
            captures.append(SqlCapture(sql=sql, columns=columns))
        return result

    return wrapper
