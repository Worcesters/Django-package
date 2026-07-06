"""Settings Django minimaux pour les tests du package."""

SECRET_KEY = "test-secret-key"
DEBUG = True
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "query_sentinel.apps.QuerySentinelConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "query_sentinel.middleware.QuerySentinelMiddleware",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
ROOT_URLCONF = "tests.urls"
USE_TZ = True

QUERY_SENTINEL_ENABLED = True
QUERY_SENTINEL_N_PLUS_ONE_THRESHOLD = 3
QUERY_SENTINEL_DEBUG_HEADERS = True
QUERY_SENTINEL_STRICT_IN_TESTS = False
QUERY_SENTINEL_STRUCTLOG_ENABLED = False
QUERY_SENTINEL_REDUNDANCY_LOG_THRESHOLD = 5
