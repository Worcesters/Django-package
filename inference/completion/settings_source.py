"""Abstraction de configuration : Django, dict Python ou fichier JSON."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from completion.exceptions import ConfigurationError

_MISSING = object()

_active_config: dict[str, Any] | None = None


def configure_from_dict(data: dict[str, Any]) -> None:
    """Enregistre une configuration en mémoire (Lambda, tests, scripts)."""
    global _active_config
    _active_config = dict(data)


def configure_from_file(path: str | Path) -> None:
    """Charge un fichier JSON et l'enregistre comme configuration active."""
    config_path = Path(path).expanduser().resolve()
    if not config_path.is_file():
        raise ConfigurationError(f"Fichier de configuration introuvable : {config_path}")

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"JSON invalide dans {config_path} : {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigurationError(
            f"Le fichier {config_path} doit contenir un objet JSON à la racine."
        )

    configure_from_dict(raw)


def reset_configuration() -> None:
    """Réinitialise la source active (tests)."""
    global _active_config
    _active_config = None


def get_setting(name: str, default: Any = _MISSING) -> Any:
    """
    Lit une constante de configuration.

    Priorité :
    1. dict / fichier JSON enregistré via configure_from_*
    2. django.conf.settings si Django est initialisé
    3. default si fourni, sinon ConfigurationError
    """
    if _active_config is not None:
        if name in _active_config:
            return _active_config[name]
        if default is not _MISSING:
            return default
        raise ConfigurationError(
            f"Constante '{name}' absente du fichier de configuration.",
        )

    if _django_is_configured():
        from django.conf import settings

        if hasattr(settings, name):
            return getattr(settings, name)
        if default is not _MISSING:
            return default
        raise ConfigurationError(
            f"Constante '{name}' absente des settings Django.",
        )

    if default is not _MISSING:
        return default

    raise ConfigurationError(
        "Aucune configuration active.\n"
        "  Django : django.setup() ou --settings config.settings.dev\n"
        "  Standalone : configure_from_dict() / configure_from_file() ou --config fichier.json",
    )


def bootstrap_runtime(
    *,
    settings_module: str | None = None,
    config_path: str | Path | None = None,
) -> None:
    """
    Initialise la configuration pour la CLI ou un script.

    --settings et --config sont mutuellement exclusifs.
    """
    if settings_module and config_path:
        raise SystemExit("--settings et --config sont mutuellement exclusifs.")

    if config_path:
        try:
            configure_from_file(config_path)
        except ConfigurationError as exc:
            raise SystemExit(exc.message) from exc
        return

    if settings_module or os.environ.get("DJANGO_SETTINGS_MODULE"):
        _bootstrap_django(settings_module)
        return

    if _active_config is not None or _django_is_configured():
        return

    raise SystemExit(
        "Configuration requise pour cette commande.\n"
        '  Django : uv run inference --test --settings config.settings.dev\n'
        '  Standalone : uv run inference --test --config ./inference.json\n'
        "  Ou export DJANGO_SETTINGS_MODULE=config.settings.dev"
    )


def _bootstrap_django(settings_module: str | None) -> None:
    import django

    module = settings_module or os.environ.get("DJANGO_SETTINGS_MODULE")
    if not module:
        raise SystemExit("DJANGO_SETTINGS_MODULE requis pour --settings.")

    _ensure_project_on_path()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", module)

    try:
        django.setup()
    except ModuleNotFoundError as exc:
        top_level = module.split(".", 1)[0]
        msg = (
            f"Impossible d'importer le module settings '{module}' ({exc}).\n"
            "  Lance la commande depuis la racine de ton projet Django (manage.py).\n"
            f"  Vérifie que le package '{top_level}' existe."
        )
        raise SystemExit(msg) from exc


def _ensure_project_on_path() -> None:
    """Ajoute la racine du projet Django hôte à sys.path."""
    cwd = Path.cwd().resolve()
    roots: list[Path] = [cwd]

    for parent in [cwd, *cwd.parents]:
        if (parent / "manage.py").is_file():
            roots.insert(0, parent)
            break

    for root in roots:
        root_str = str(root)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)


def _django_is_configured() -> bool:
    try:
        from django.conf import settings

        return bool(settings.configured)
    except ImportError:
        return False
