"""Constantes de configuration Django pour django-inference."""

from __future__ import annotations

# Noms des settings à déclarer dans config/settings/base.py du projet hôte
SETTING_DEFAULT_PROVIDER = "INFERENCE_DEFAULT_PROVIDER"
SETTING_PROVIDERS = "INFERENCE_PROVIDERS"
SETTING_RETRY = "INFERENCE_RETRY"

# Registry par défaut (chemins de classes provider)
DEFAULT_PROVIDER_REGISTRY: dict[str, str] = {
    "openai": "inference.providers.openai.OpenAIProvider",
    "mistral": "inference.providers.mistral.MistralProvider",
    "llama": "inference.providers.ollama.OllamaProvider",
}


def format_settings_help() -> str:
    """Texte d'aide affiché dans `inference-preview --help` (snippet settings)."""
    provider_keys = ", ".join(f'"{name}"' for name in DEFAULT_PROVIDER_REGISTRY)
    return f"""
Configuration Django (config/settings/base.py)
--------------------------------------------

Constantes requises :

  {SETTING_DEFAULT_PROVIDER}
      Provider utilisé par défaut si aucun nom n'est passé aux services.
      Exemple : "openai"

  {SETTING_PROVIDERS}
      Dict des providers disponibles. Chaque entrée accepte :
        - backend (str)       : chemin importable de la classe provider
        - model (str)         : modèle par défaut
        - api_key_env (str)   : nom de variable d'environnement (optionnel)
        - base_url (str)      : URL de l'API (optionnel)
        - temperature (float) : défaut 0.7
        - max_tokens (int)    : défaut 1024
        - timeout (int)       : secondes, défaut 60
        - extra (dict)        : paramètres spécifiques au provider

  {SETTING_RETRY}  (optionnel)
      Politique de retry HTTP : max_attempts, backoff, retry_on.

Providers enregistrés par défaut dans la factory : {provider_keys}

Snippet à copier dans config/settings/base.py :

{SETTING_DEFAULT_PROVIDER} = "openai"

{SETTING_PROVIDERS} = {{
    "openai": {{
        "backend": "{DEFAULT_PROVIDER_REGISTRY["openai"]}",
        "model": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "temperature": 0.2,
        "max_tokens": 2048,
        "timeout": 60,
    }},
    "mistral": {{
        "backend": "{DEFAULT_PROVIDER_REGISTRY["mistral"]}",
        "model": "mistral-large-latest",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
        "temperature": 0.3,
        "max_tokens": 2048,
        "timeout": 60,
    }},
    "llama": {{
        "backend": "{DEFAULT_PROVIDER_REGISTRY["llama"]}",
        "model": "llama3.2",
        "base_url": "http://localhost:11434",
        "temperature": 0.7,
        "max_tokens": 1024,
        "timeout": 120,
        "extra": {{"num_ctx": 4096}},
    }},
}}

{SETTING_RETRY} = {{
    "max_attempts": 3,
    "backoff": "exponential",
    "retry_on": [429, 502, 503],
}}

Variables d'environnement (.env) :

  OPENAI_API_KEY=sk-...
  MISTRAL_API_KEY=...

Installe aussi l'app dans INSTALLED_APPS :

  "inference.apps.InferenceConfig",
""".strip()
