"""Settings Django minimaux pour les tests du package."""

SECRET_KEY = "test-secret-key"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "completion.apps.InferenceConfig",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
ROOT_URLCONF = "tests.urls"
USE_TZ = True

INFERENCE_DEFAULT_PROVIDER = "openai"
INFERENCE_PROVIDERS = {
    "openai": {
        "backend": "completion.providers.openai.OpenAIProvider",
        "model": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
    },
    "llama": {
        "backend": "completion.providers.ollama.OllamaProvider",
        "model": "llama3.2",
        "base_url": "http://localhost:11434",
    },
}
