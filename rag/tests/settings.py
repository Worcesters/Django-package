"""Settings Django minimaux pour les tests du package."""

SECRET_KEY = "test-secret-key"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rag.apps.RagConfig",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
ROOT_URLCONF = "tests.urls"
USE_TZ = True

RAG_DEFAULT_EMBEDDER = "ollama"
RAG_EMBEDDERS = {
    "ollama": {
        "backend": "rag.embedders.ollama.OllamaEmbedder",
        "model": "nomic-embed-text",
        "base_url": "http://localhost:11434",
        "dimensions": 3,
    },
    "openai": {
        "backend": "rag.embedders.openai.OpenAIEmbedder",
        "model": "text-embedding-3-small",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "dimensions": 3,
    },
}

RAG_DEFAULT_STORE = "memory"
RAG_VECTOR_STORES = {
    "memory": {
        "backend": "rag.stores.memory.InMemoryStore",
        "collection": "test",
        "dimensions": 3,
    },
}

RAG_CHUNKING = {
    "strategy": "fixed_size",
    "chunk_size": 20,
    "chunk_overlap": 5,
}

RAG_RETRIEVAL = {
    "top_k": 3,
    "min_score": 0.0,
}
