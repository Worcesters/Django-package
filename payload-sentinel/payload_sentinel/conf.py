"""Constantes de configuration Django pour payload-sentinel."""

from __future__ import annotations

SETTING_ENABLED = "PAYLOAD_SENTINEL_ENABLED"
SETTING_SENSITIVE_FIELDS = "PAYLOAD_SENTINEL_SENSITIVE_FIELDS"
SETTING_OVERFETCH_THRESHOLD = "PAYLOAD_SENTINEL_OVERFETCH_THRESHOLD"
SETTING_BLOCK_SENSITIVE_LEAK = "PAYLOAD_SENTINEL_BLOCK_SENSITIVE_LEAK"
SETTING_DEBUG_HEADERS = "PAYLOAD_SENTINEL_DEBUG_HEADERS"
SETTING_STRUCTLOG_ENABLED = "PAYLOAD_SENTINEL_STRUCTLOG_ENABLED"
SETTING_LOG_OVERFETCH = "PAYLOAD_SENTINEL_LOG_OVERFETCH"
SETTING_STRICT_IN_TESTS = "PAYLOAD_SENTINEL_STRICT_IN_TESTS"
SETTING_MIDDLEWARE = "PAYLOAD_SENTINEL_MIDDLEWARE"

DEFAULT_MIDDLEWARE = "payload_sentinel.middleware.PayloadSentinelMiddleware"

DEFAULT_SENSITIVE_FIELDS: tuple[str, ...] = (
    "password",
    "password_hash",
    "hashed_password",
    "api_token",
    "token",
    "secret",
    "private_key",
    "ssn",
    "credit_card",
)

HEADER_SQL_COLUMNS = "X-Django-Payload-SQL-Columns"
HEADER_RESPONSE_FIELDS = "X-Django-Payload-Response-Fields"
HEADER_OVERFETCH_RATIO = "X-Django-Payload-Overfetch-Ratio"
HEADER_SENSITIVE_LEAK = "X-Django-Payload-Sensitive-Leak"
HEADER_DEBUG = "X-Django-Payload-Debug"


def format_settings_help() -> str:
    return f"""
Configuration Django (config/settings/base.py)
--------------------------------------------

Constantes :

  {SETTING_ENABLED}
      Active la surveillance payload (middleware). Défaut : True

  {SETTING_SENSITIVE_FIELDS}
      Motifs de champs sensibles (sous-chaîne, insensible à la casse).
      Défaut : password, password_hash, api_token, secret, ...

  {SETTING_OVERFETCH_THRESHOLD}
      Ratio de colonnes SQL inutilisées avant alerte perf (0.85 = 85%). Défaut : 0.85

  {SETTING_BLOCK_SENSITIVE_LEAK}
      Bloque la réponse HTTP si fuite sensible détectée. Défaut : True

  {SETTING_DEBUG_HEADERS}
      Injecte {HEADER_DEBUG} et métriques si DEBUG=True. Défaut : True

  {SETTING_STRUCTLOG_ENABLED}
      Log JSON structuré en production. Défaut : True

  {SETTING_STRICT_IN_TESTS}
      Mode strict global pour les tests (via mixin). Défaut : False

Snippet :

INSTALLED_APPS = ["payload_sentinel.apps.PayloadSentinelConfig"]

MIDDLEWARE = ["payload_sentinel.middleware.PayloadSentinelMiddleware"]

{SETTING_ENABLED} = True
{SETTING_SENSITIVE_FIELDS} = ["password", "password_hash", "api_token", "secret"]
{SETTING_OVERFETCH_THRESHOLD} = 0.85
{SETTING_BLOCK_SENSITIVE_LEAK} = True

Configuration standalone (--config) :

  uv run payload-sentinel --status --config ./payload.json
""".strip()
