# query-sentinel

Package Django installable via **uv** — détection **N+1**, requêtes SQL dupliquées, headers debug et logs structurés.

> Alias conceptuel : *django-n-plus-one-killer*

## Installation

```powershell
cd chemin/vers/votre/projet-django
uv add "query-sentinel @ git+https://github.com/VOTRE_ORG/Django-package.git@main#subdirectory=query-sentinel"
```

## CLI `query-sentinel`

```powershell
# Aide + snippet QUERY_SENTINEL_*
uv run query-sentinel --help

# README coloré
uv run query-sentinel --readme

# Preview architecture (zoom/pan)
uv run query-sentinel --preview

# Vérifier la config active (Django)
uv run query-sentinel --status --settings config.settings.dev

# Vérifier la config (standalone JSON)
uv run query-sentinel --status --config ./sentinel.json
```

| Commande | Description |
|----------|-------------|
| `--help` | Aide CLI colorée + snippet settings |
| `--readme` | README coloré dans le terminal |
| `--preview` | Diagramme PlantUML interactif |
| `--status` | Affiche la config résolue (JSON) |
| `--settings MODULE` | Config depuis Django settings |
| `--config FICHIER` | Config depuis JSON standalone |

## Configuration Django

```python
INSTALLED_APPS = [
    # ...
    "query_sentinel.apps.QuerySentinelConfig",
]

MIDDLEWARE = [
    # ...
    "query_sentinel.middleware.QuerySentinelMiddleware",
]

QUERY_SENTINEL_ENABLED = True
QUERY_SENTINEL_N_PLUS_ONE_THRESHOLD = 3
QUERY_SENTINEL_DEBUG_HEADERS = True
QUERY_SENTINEL_STRUCTLOG_ENABLED = True
QUERY_SENTINEL_REDUNDANCY_LOG_THRESHOLD = 5
QUERY_SENTINEL_STRICT_IN_TESTS = False
QUERY_SENTINEL_BLOCK_ON_N_PLUS_ONE_STAGING = False
QUERY_SENTINEL_MAX_QUERIES_PER_REQUEST = None  # optionnel
```

### Headers debug (`DEBUG=True`)

Le middleware injecte :

| Header | Exemple |
|--------|---------|
| `X-Django-SQL-Count` | `42` |
| `X-Django-N-Plus-One-Detected` | `true` / `false` |
| `X-Django-SQL-Max-Redundancy` | `12` |

Visibles dans les DevTools du navigateur (onglet Network → Response Headers).

## Mode strict en tests

### Décorateur `@fail_on_n_plus_one`

```python
from query_sentinel.decorators import fail_on_n_plus_one

@fail_on_n_plus_one(threshold=3)
def test_list_books(self):
    for book in Book.objects.all():
        _ = book.author.name  # N+1 → test échoue
```

### Mixin `SentinelTestMixin`

```python
from django.test import TestCase
from query_sentinel.mixins import SentinelTestMixin

class BookTests(SentinelTestMixin, TestCase):
    ...
```

Active le mode strict si `QUERY_SENTINEL_STRICT_IN_TESTS = True`.

## Production — Structlog / Grafana

Si `QUERY_SENTINEL_STRUCTLOG_ENABLED = True` et redondance ≥ `QUERY_SENTINEL_REDUNDANCY_LOG_THRESHOLD`, un événement JSON est émis :

```json
{
  "event": "query_sentinel_redundancy",
  "sql_count": 47,
  "n_plus_one_detected": true,
  "max_redundancy": 15,
  "path": "/api/books/",
  "method": "GET"
}
```

Dépendance optionnelle : `uv add "query-sentinel[structlog]"`.

## Configuration standalone (`--config` / Lambda)

```json
{
  "QUERY_SENTINEL_ENABLED": true,
  "QUERY_SENTINEL_N_PLUS_ONE_THRESHOLD": 3,
  "QUERY_SENTINEL_DEBUG_HEADERS": true
}
```

```python
from query_sentinel.settings_source import configure_from_file
from query_sentinel.selectors import get_sentinel_config

configure_from_file("sentinel.json")
config = get_sentinel_config()
```

## Utilisation Python (couche service)

```python
from query_sentinel.collector import query_collection
from query_sentinel.selectors import get_sentinel_config
from query_sentinel.services import build_analysis_report, enforce_policies

config = get_sentinel_config()

with query_collection() as records:
    do_work()

report = build_analysis_report(records, config)
enforce_policies(report, config, strict=True)  # lève NPlusOneError
```

## Architecture

```
HTTP Request
    → QuerySentinelMiddleware
        → query_collection() [execute_wrapper]
            → Vue Django / API
        → analyze_queries() [normalisation SQL]
        → headers DEBUG / structlog / enforce_policies
```

Snippet complet : `uv run query-sentinel --help`  
Modèle JSON : `query_sentinel/examples/sentinel.dev.json`

## Structure

- `query_sentinel/middleware.py` — surveillance HTTP passive
- `query_sentinel/collector.py` — capture SQL via `execute_wrapper`
- `query_sentinel/analyzer.py` — détection N+1 (normalisation SQL)
- `query_sentinel/services.py` — politiques et rapports
- `query_sentinel/decorators.py` — `@fail_on_n_plus_one`
- `query_sentinel/mixins.py` — `SentinelTestMixin`
- `query_sentinel/logging_integration.py` — structlog JSON
- `query_sentinel/settings_source.py` — Django / JSON / Lambda
- `query_sentinel/docs/package_archi.puml` — diagramme

## Développement

```powershell
cd query-sentinel
uv sync --extra dev
uv run pytest -q
uv run query-sentinel --preview --no-open
```
