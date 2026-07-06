from django.apps import AppConfig


class QuerySentinelConfig(AppConfig):
    """Configuration Django pour le package query-sentinel."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "query_sentinel"
    verbose_name = "Query Sentinel"
