"""Collecte passive des requêtes SQL via execute_wrapper Django."""

from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Callable, Iterator

from django.db import connections

from query_sentinel.schemas import QueryRecord

_active_records: ContextVar[list[QueryRecord] | None] = ContextVar(
    "query_sentinel_records",
    default=None,
)


def get_active_records() -> list[QueryRecord] | None:
    """Retourne les enregistrements de la collecte en cours, ou None."""
    return _active_records.get()


@contextmanager
def query_collection() -> Iterator[list[QueryRecord]]:
    """
    Context manager : capture toutes les requêtes SQL sur toutes les connexions.

    Usage HTTP (middleware), tests (@fail_on_n_plus_one) ou jobs Celery.
    """
    records: list[QueryRecord] = []
    token = _active_records.set(records)
    contexts: list[Any] = []

    try:
        for connection in connections.all():
            wrapper = _build_wrapper(records, connection.alias)
            contexts.append(connection.execute_wrapper(wrapper))
            contexts[-1].__enter__()
        yield records
    finally:
        for ctx in reversed(contexts):
            ctx.__exit__(None, None, None)
        _active_records.reset(token)


def _build_wrapper(
    records: list[QueryRecord],
    alias: str,
) -> Callable[..., Any]:
    def wrapper(
        execute: Callable[..., Any],
        sql: str,
        params: Any,
        many: bool,
        context: dict[str, Any],
    ) -> Any:
        start = time.perf_counter()
        result = execute(sql, params, many, context)
        duration_ms = (time.perf_counter() - start) * 1000.0
        records.append(
            QueryRecord(
                sql=sql,
                params=_normalize_params(params),
                duration_ms=duration_ms,
                alias=alias,
            )
        )
        return result

    return wrapper


def _normalize_params(params: Any) -> tuple[Any, ...]:
    if params is None:
        return ()
    if isinstance(params, (list, tuple)):
        return tuple(params)
    return (params,)
