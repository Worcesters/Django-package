"""Capture de la stack applicative à l'origine d'une requête SQL."""

from __future__ import annotations

import traceback
from pathlib import Path

from query_sentinel.schemas import QueryOrigin

_SKIP_PATH_PARTS = (
    "query_sentinel",
    "django/db",
    "django/core",
    "django/test",
    "site-packages/django",
    "unittest",
    "pytest",
)


def capture_query_origin() -> QueryOrigin:
    """
    Retourne le premier frame hors infra Django/query_sentinel.

    Permet d'identifier le fichier et la ligne qui ont déclenché la requête SQL.
    """
    stack = traceback.extract_stack()[:-3]
    for frame in reversed(stack):
        filename = _short_path(frame.filename)
        normalized = filename.replace("\\", "/").lower()
        if any(part in normalized for part in _SKIP_PATH_PARTS):
            continue
        return QueryOrigin(
            filename=filename,
            lineno=frame.lineno,
            function=frame.name,
        )
    return QueryOrigin(filename="unknown", lineno=0, function="unknown")


def _short_path(filepath: str) -> str:
    path = Path(filepath)
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return path.name
