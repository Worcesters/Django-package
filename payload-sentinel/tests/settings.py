"""Settings Django minimaux pour les tests du package."""

SECRET_KEY = "test-secret-key"
DEBUG = True
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "payload_sentinel.apps.PayloadSentinelConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "payload_sentinel.middleware.PayloadSentinelMiddleware",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
ROOT_URLCONF = "tests.urls"
USE_TZ = True

PAYLOAD_SENTINEL_ENABLED = True
PAYLOAD_SENTINEL_OVERFETCH_THRESHOLD = 0.75
PAYLOAD_SENTINEL_DEBUG_HEADERS = True
PAYLOAD_SENTINEL_BLOCK_SENSITIVE_LEAK = True
PAYLOAD_SENTINEL_STRICT_IN_TESTS = False
PAYLOAD_SENTINEL_STRUCTLOG_ENABLED = False
