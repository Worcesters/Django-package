"""Extraction des colonnes depuis les requêtes SQL SELECT."""

from __future__ import annotations

import re

from payload_sentinel.schemas import SqlColumn

_SELECT_PREFIX = re.compile(r"^\s*SELECT\s+", re.IGNORECASE)
_FROM_SPLIT = re.compile(r"\s+FROM\s+", re.IGNORECASE)
_QUOTED_IDENTIFIER = re.compile(r'"([^"]+)"')
_WILDCARD = re.compile(r"^\*$|^\w+\.\*$")


def extract_columns_from_sql(sql: str) -> tuple[SqlColumn, ...]:
    """Parse une requête SELECT et retourne les colonnes lues."""
    if not _SELECT_PREFIX.match(sql):
        return ()

    body = _FROM_SPLIT.split(sql, maxsplit=1)[0]
    select_clause = _SELECT_PREFIX.sub("", body, count=1).strip()
    if not select_clause:
        return ()

    columns: list[SqlColumn] = []
    for raw_part in _split_select_clause(select_clause):
        part = raw_part.strip()
        if not part or part == "*":
            columns.append(SqlColumn(table="", column="*", wildcard=True))
            continue

        if _WILDCARD.match(part):
            table = part.split(".", 1)[0].strip('"')
            columns.append(SqlColumn(table=table, column="*", wildcard=True))
            continue

        quoted = _QUOTED_IDENTIFIER.findall(part)
        if len(quoted) >= 2:
            columns.append(SqlColumn(table=quoted[-2], column=quoted[-1]))
            continue
        if len(quoted) == 1:
            columns.append(SqlColumn(table="", column=quoted[0]))
            continue

        bare = part.split()[-1].split(".")[-1].strip('"')
        if bare and bare != "*":
            columns.append(SqlColumn(table="", column=bare))

    return tuple(columns)


def _split_select_clause(select_clause: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in select_clause:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(depth - 1, 0)
        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if current:
        parts.append("".join(current).strip())
    return parts
