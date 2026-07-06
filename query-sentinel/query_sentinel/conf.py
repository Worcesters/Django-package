"""Constantes de configuration Django pour query-sentinel."""

from __future__ import annotations

SETTING_ENABLED = "QUERY_SENTINEL_ENABLED"
SETTING_N_PLUS_ONE_THRESHOLD = "QUERY_SENTINEL_N_PLUS_ONE_THRESHOLD"
SETTING_MAX_QUERIES = "QUERY_SENTINEL_MAX_QUERIES_PER_REQUEST"
SETTING_DEBUG_HEADERS = "QUERY_SENTINEL_DEBUG_HEADERS"
SETTING_STRICT_IN_TESTS = "QUERY_SENTINEL_STRICT_IN_TESTS"
SETTING_STRUCTLOG_ENABLED = "QUERY_SENTINEL_STRUCTLOG_ENABLED"
SETTING_REDUNDANCY_LOG_THRESHOLD = "QUERY_SENTINEL_REDUNDANCY_LOG_THRESHOLD"
SETTING_BLOCK_STAGING = "QUERY_SENTINEL_BLOCK_ON_N_PLUS_ONE_STAGING"
SETTING_MIDDLEWARE = "QUERY_SENTINEL_MIDDLEWARE"

DEFAULT_MIDDLEWARE = "query_sentinel.middleware.QuerySentinelMiddleware"

HEADER_SQL_COUNT = "X-Django-SQL-Count"
HEADER_N_PLUS_ONE = "X-Django-N-Plus-One-Detected"
HEADER_MAX_REDUNDANCY = "X-Django-SQL-Max-Redundancy"
HEADER_N_PLUS_ONE_SOURCE = "X-Django-N-Plus-One-Source"
HEADER_N_PLUS_ONE_DEBUG = "X-Django-N-Plus-One-Debug"


def format_settings_help() -> str:
    """Texte d'aide affiché dans `query-sentinel --help`."""
    return f"""
Configuration Django (config/settings/base.py)
--------------------------------------------

Constantes :

  {SETTING_ENABLED}
      Active la surveillance SQL (middleware). Défaut : True

  {SETTING_N_PLUS_ONE_THRESHOLD}
      Nombre d'exécutions du même motif SQL avant alerte N+1. Défaut : 3

  {SETTING_MAX_QUERIES}
      Seuil optionnel de requêtes par requête HTTP (alerte / blocage staging)

  {SETTING_DEBUG_HEADERS}
      Injecte {HEADER_SQL_COUNT}, {HEADER_N_PLUS_ONE}, {HEADER_N_PLUS_ONE_SOURCE}
      et {HEADER_N_PLUS_ONE_DEBUG} si DEBUG=True. Défaut : True

  {SETTING_STRICT_IN_TESTS}
      Active le mode strict global pour les tests (décorateur / mixin). Défaut : False

  {SETTING_STRUCTLOG_ENABLED}
      Log JSON structuré (structlog) en production si seuil dépassé. Défaut : True

  {SETTING_REDUNDANCY_LOG_THRESHOLD}
      Seuil de redondance max pour logger en production. Défaut : 5

  {SETTING_BLOCK_STAGING}
      Bloque la réponse HTTP en staging si N+1 détecté. Défaut : False

Snippet à copier dans config/settings/base.py :

INSTALLED_APPS = [
    # ...
    "query_sentinel.apps.QuerySentinelConfig",
]

MIDDLEWARE = [
    # ...
    "{DEFAULT_MIDDLEWARE}",
]

{SETTING_ENABLED} = True
{SETTING_N_PLUS_ONE_THRESHOLD} = 3
{SETTING_DEBUG_HEADERS} = True
{SETTING_STRUCTLOG_ENABLED} = True
{SETTING_REDUNDANCY_LOG_THRESHOLD} = 5

Configuration standalone (Lambda, scripts, --config)
---------------------------------------------------

  uv run query-sentinel --status --config ./sentinel.json

Exemple sentinel.json :

{{
  "{SETTING_ENABLED}": true,
  "{SETTING_N_PLUS_ONE_THRESHOLD}": 3,
  "{SETTING_DEBUG_HEADERS}": true,
  "{SETTING_STRUCTLOG_ENABLED}": true
}}

En code : configure_from_dict() ou configure_from_file() au démarrage.
""".strip()
