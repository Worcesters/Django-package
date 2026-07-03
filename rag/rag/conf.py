"""Constantes de configuration Django pour django-rag."""

from __future__ import annotations

SETTING_DEFAULT_EMBEDDER = "RAG_DEFAULT_EMBEDDER"
SETTING_EMBEDDERS = "RAG_EMBEDDERS"
SETTING_DEFAULT_STORE = "RAG_DEFAULT_STORE"
SETTING_VECTOR_STORES = "RAG_VECTOR_STORES"
SETTING_CHUNKING = "RAG_CHUNKING"
SETTING_RETRIEVAL = "RAG_RETRIEVAL"
SETTING_PROMPT_TEMPLATE = "RAG_PROMPT_TEMPLATE"

DEFAULT_EMBEDDER_REGISTRY: dict[str, str] = {
    "openai": "rag.embedders.openai.OpenAIEmbedder",
    "mistral": "rag.embedders.mistral.MistralEmbedder",
    "ollama": "rag.embedders.ollama.OllamaEmbedder",
}

DEFAULT_STORE_REGISTRY: dict[str, str] = {
    "memory": "rag.stores.memory.InMemoryStore",
}


def format_settings_help() -> str:
    """Texte d'aide affiché dans `rag --help` (snippet settings)."""
    embedder_keys = ", ".join(f'"{name}"' for name in DEFAULT_EMBEDDER_REGISTRY)
    store_keys = ", ".join(f'"{name}"' for name in DEFAULT_STORE_REGISTRY)
    return f"""
Configuration Django (config/settings/base.py)
--------------------------------------------

Constantes requises :

  {SETTING_DEFAULT_EMBEDDER}
      Embedder utilisé par défaut. Exemple : "ollama"

  {SETTING_EMBEDDERS}
      Dict des embedders. Chaque entrée accepte :
        - backend (str)       : chemin importable de la classe embedder
        - model (str)         : modèle d'embedding
        - dimensions (int)    : taille du vecteur (obligatoire)
        - api_key_env (str)   : variable d'environnement (openai/mistral)
        - base_url (str)      : URL de l'API (obligatoire)
        - timeout (int)       : secondes, défaut 60
        - extra (dict)        : paramètres spécifiques

  {SETTING_DEFAULT_STORE}
      Vector store par défaut. Exemple : "memory"

  {SETTING_VECTOR_STORES}
      Dict des stores vectoriels :
        - backend (str)       : chemin importable (memory, pgvector v2...)
        - collection (str)    : nom de la collection
        - dimensions (int)    : doit matcher l'embedder

  {SETTING_CHUNKING}  (optionnel)
      strategy: fixed_size | sentence | paragraph | word
      chunk_size, chunk_overlap, separators

  {SETTING_RETRIEVAL}  (optionnel)
      top_k, min_score

  {SETTING_PROMPT_TEMPLATE}  (optionnel)
      Template avec {{context}} et {{question}}

Embedders par défaut : {embedder_keys}
Stores par défaut : {store_keys}

Snippet à copier dans config/settings/base.py :

{SETTING_DEFAULT_EMBEDDER} = "ollama"

{SETTING_EMBEDDERS} = {{
    "ollama": {{
        "backend": "{DEFAULT_EMBEDDER_REGISTRY["ollama"]}",
        "model": "nomic-embed-text",
        "base_url": "http://localhost:11434",
        "dimensions": 768,
    }},
    "openai": {{
        "backend": "{DEFAULT_EMBEDDER_REGISTRY["openai"]}",
        "model": "text-embedding-3-small",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "dimensions": 1536,
    }},
}}

{SETTING_DEFAULT_STORE} = "memory"

{SETTING_VECTOR_STORES} = {{
    "memory": {{
        "backend": "{DEFAULT_STORE_REGISTRY["memory"]}",
        "collection": "default",
        "dimensions": 768,
    }},
}}

{SETTING_CHUNKING} = {{
    "strategy": "fixed_size",
    "chunk_size": 800,
    "chunk_overlap": 120,
}}

{SETTING_RETRIEVAL} = {{
    "top_k": 5,
    "min_score": 0.0,
}}

Installe aussi l'app dans INSTALLED_APPS :

  "rag.apps.RagConfig",
""".strip()
