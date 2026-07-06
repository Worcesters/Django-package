"""Commande --test : lance la suite Pytest du package."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def run_tests(
    *,
    settings_module: str | None = None,
    pytest_args: list[str] | None = None,
) -> None:
    """Exécute pytest dans le répertoire courant du package."""
    if settings_module:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
        _bootstrap_django(settings_module)

    import pytest

    args = list(pytest_args or ["-q"])
    exit_code = pytest.main(args)
    raise SystemExit(exit_code)


def _bootstrap_django(settings_module: str) -> None:
    try:
        import django
    except ImportError:
        return

    _ensure_project_on_path()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    if not django.apps.apps.ready:
        django.setup()


def _ensure_project_on_path() -> None:
    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        if (parent / "pyproject.toml").is_file() and (parent / "tests").is_dir():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            break
        if (parent / "manage.py").is_file():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            break
