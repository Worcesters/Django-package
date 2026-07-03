# rag

Package Django installable via **uv** — embedding, indexation et retrieval (RAG).

Compose avec le package **[inference](../inference/)** pour la génération finale (`complete()`).

## Installation

```powershell
cd chemin/vers/votre/projet-django
uv add "rag @ git+https://github.com/VOTRE_ORG/package_llm_rag.git"
```

Développement local :

```powershell
uv add --editable ./chemin/vers/rag
```

## CLI `rag`

```powershell
# Aide + snippet des constantes Django RAG_*
uv run rag --help

# README coloré dans le terminal
uv run rag --readme

# Preview architecture interactive (zoom/pan)
uv run rag --preview

# Tester l'embedder
uv run rag --embed "Bonjour le monde" --settings config.settings.dev

# Indexer un texte
uv run rag --index "Les chats sont des félins domestiques." --settings config.settings.dev

# Rechercher des chunks
uv run rag --retrieve "félins" --settings config.settings.dev
```

### Workflow de test CLI

```powershell
cd chemin/vers/votre/projet-django

# 1. Indexer
uv run rag -i "Django est un framework Python pour le web." --settings config.settings.dev

# 2. Retriever
uv run rag -r "framework Python" --settings config.settings.dev --top-k 3
```

| Commande | Description |
|----------|-------------|
| `uv run rag --help` | Aide CLI + snippet `RAG_*` |
| `uv run rag --readme` | README coloré dans le terminal |
| `uv run rag --preview` | Viewer HTML interactif (zoom molette, glisser pour pan) |
| `uv run rag --preview --no-open` | Affiche les chemins preview sans ouvrir le navigateur |
| `uv run rag --preview --html-output docs/archi.html` | Enregistre le viewer HTML localement |
| `uv run rag -e "..." --settings ...` | Teste l'embedding |
| `uv run rag -i "..." --settings ...` | Indexe un texte |
| `uv run rag -r "..." --settings ...` | Recherche sémantique |

## Configuration Django

Dans `config/settings/base.py` :

```python
INSTALLED_APPS = [
    # ...
    "rag.apps.RagConfig",
]

RAG_DEFAULT_EMBEDDER = "ollama"
RAG_EMBEDDERS = {
    "ollama": {
        "backend": "rag.embedders.ollama.OllamaEmbedder",
        "model": "nomic-embed-text",
        "base_url": "http://localhost:11434",
        "dimensions": 768,
    },
    "openai": {
        "backend": "rag.embedders.openai.OpenAIEmbedder",
        "model": "text-embedding-3-small",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "dimensions": 1536,
    },
    "mistral": {
        "backend": "rag.embedders.mistral.MistralEmbedder",
        "model": "mistral-embed",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
        "dimensions": 1024,
    },
}

RAG_DEFAULT_STORE = "memory"
RAG_VECTOR_STORES = {
    "memory": {
        "backend": "rag.stores.memory.InMemoryStore",
        "collection": "default",
        "dimensions": 768,  # doit matcher RAG_DEFAULT_EMBEDDER
    },
}
```

> **Embedding ≠ LLM chat** — pour `--embed`, `--index` et `--retrieve`, tu n'as **pas besoin** d'un modèle de completion (`gpt-4`, `mistral-large`, etc.) ni du package `inference`. Il te faut un **modèle d'embedding** dédié (`nomic-embed-text`, `text-embedding-3-small`, `mistral-embed`…). Le package `inference` n'intervient que pour **générer la réponse** une fois les chunks récupérés (RAG complet côté projet hôte).

> **Clés API** — `OPENAI_API_KEY` et `MISTRAL_API_KEY` sont les **mêmes** que pour le chat, mais le **modèle** dans `RAG_EMBEDDERS` doit être un modèle d'embedding, pas un modèle LLM.

```python
RAG_CHUNKING = {
    "strategy": "fixed_size",
    "chunk_size": 800,
    "chunk_overlap": 120,
}

RAG_RETRIEVAL = {
    "top_k": 5,
    "min_score": 0.0,
}
```

Snippet complet : `uv run rag --help`

## Utilisation Python

### Indexation

```python
from rag.services import index_text

result = index_text(
    "Django est un framework web Python.",
    metadata={"topic": "django"},
    source_id="doc-1",
)
print(result.chunks_indexed)
```

### Retrieval

```python
from rag.services import retrieve

chunks = retrieve("framework web", top_k=3)
for chunk in chunks:
    print(chunk.score, chunk.text)
```

### RAG complet (avec inference)

```python
from rag.prompt import build_rag_messages
from rag.services import retrieve
from completion.services import complete

query = "Qu'est-ce que Django ?"
chunks = retrieve(query, top_k=5)
messages = build_rag_messages(query, chunks)
answer = complete(messages=messages)
print(answer.text)
```

### Service métier (projet hôte)

```python
from __future__ import annotations

from rag.exceptions import RagError
from rag.prompt import build_rag_messages
from rag.services import index_text, retrieve
from completion.exceptions import InferenceError
from completion.services import complete


def ask_with_rag(*, question: str) -> str:
    chunks = retrieve(question, top_k=5)
    messages = build_rag_messages(question, chunks)
    try:
        result = complete(messages=messages)
    except InferenceError as exc:
        raise RagError(exc.message, code=exc.code) from exc
    return result.text
```

## Chunking

La granularité se configure via `RAG_CHUNKING.strategy` :

| Strategy | Description |
|----------|-------------|
| `fixed_size` | Taille fixe + overlap (défaut) |
| `sentence` | Découpe par phrase |
| `paragraph` | Découpe par paragraphe |
| `word` | Découpe par mots (`words_per_chunk`) |

## Structure

- `rag/cli.py` — commande `uv run rag`
- `rag/services.py` — `index_text()`, `retrieve()`
- `rag/prompt.py` — `build_rag_messages()`
- `rag/chunkers.py` — découpage texte
- `rag/embedders/` — Ollama, OpenAI, Mistral
- `rag/stores/` — InMemoryStore (`pgvector` prévu v2)
- `rag/conf.py` — constantes `RAG_*`
- `rag/docs/package_archi.puml` — diagramme d'architecture

## Développement

```powershell
cd rag
uv sync --extra dev
uv run pytest -q
uv run rag --preview --no-open
```
