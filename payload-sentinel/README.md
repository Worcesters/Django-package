# payload-sentinel

Package Django installable via **uv** — détection de **sur-sélection SQL** et **fuites de données** dans les réponses API.

> Alias conceptuel : *Le Gardien des Fuites de Données*

## Installation

```powershell
cd chemin/vers/votre/projet-django
uv add "payload-sentinel @ git+https://github.com/VOTRE_ORG/Django-package.git@main#subdirectory=payload-sentinel"
```

## CLI `payload-sentinel`

```powershell
# Aide + snippet PAYLOAD_SENTINEL_*
uv run payload-sentinel --help

# README coloré
uv run payload-sentinel --readme

# Preview architecture (zoom/pan)
uv run payload-sentinel --preview

# Lancer les tests Pytest
uv run payload-sentinel --test

# Vérifier la config active (Django)
uv run payload-sentinel --status --settings config.settings.dev

# Vérifier la config (standalone JSON)
uv run payload-sentinel --status --config ./payload.json
```

| Commande | Description |
|----------|-------------|
| `--help` | Aide CLI colorée + snippet settings |
| `--readme` | README coloré dans le terminal |
| `--preview` | Diagramme PlantUML interactif |
| `--test` | Lance la suite Pytest du package |
| `--status` | Affiche la config résolue (JSON) |
| `--settings MODULE` | Config depuis Django settings |
| `--config FICHIER` | Config depuis JSON standalone |

## Configuration Django

```python
INSTALLED_APPS = [
    # ...
    "payload_sentinel.apps.PayloadSentinelConfig",
]

MIDDLEWARE = [
    # ...
    "payload_sentinel.middleware.PayloadSentinelMiddleware",
]

PAYLOAD_SENTINEL_ENABLED = True
PAYLOAD_SENTINEL_SENSITIVE_FIELDS = ["password", "password_hash", "api_token", "secret"]
PAYLOAD_SENTINEL_OVERFETCH_THRESHOLD = 0.85
PAYLOAD_SENTINEL_BLOCK_SENSITIVE_LEAK = True
PAYLOAD_SENTINEL_DEBUG_HEADERS = True
PAYLOAD_SENTINEL_STRUCTLOG_ENABLED = True
PAYLOAD_SENTINEL_LOG_OVERFETCH = True
PAYLOAD_SENTINEL_STRICT_IN_TESTS = False
```

## Concept

En production, renvoyer trop de données dans les APIs est un risque **performance** (colonnes SQL inutiles) et **sécurité** (champs sensibles exposés).

`payload-sentinel` compare :

1. **Colonnes SQL réellement lues** (via `connection.execute_wrapper`)
2. **Champs effectivement sérialisés** dans la réponse JSON

### Alerte performance (sur-sélection)

Si vous faites un `SELECT` sur 40 colonnes mais que l'API n'expose que `id` et `title`, le Sentinel logue :

```
Sur-sélection SQL : 85% des colonnes récupérées ne sont pas dans la réponse JSON.
Optimisation : utilisez .only() / .values() / un serializer restreint.
```

### Alerte sécurité (fuite)

Si un champ sensible (`password_hash`, `api_token`, …) est détecté dans le JSON final, la réponse est **bloquée** et une exception de sécurité est levée.

### Headers debug (`DEBUG=True`)

| Header | Exemple | Signification |
|--------|---------|---------------|
| `X-Django-Payload-SQL-Columns` | `12` | Nombre de colonnes SQL distinctes lues |
| `X-Django-Payload-Response-Fields` | `3` | Nombre de chemins JSON dans la réponse |
| `X-Django-Payload-Overfetch-Ratio` | `0.9091` | Ratio colonnes inutilisées |
| `X-Django-Payload-Sensitive-Leak` | `true` / `false` | Fuite sensible détectée |
| `X-Django-Payload-Debug` | `{"unused_columns":[...]}` | JSON détaillé |

Visibles dans les DevTools (Network → Response Headers).

## Mode strict en tests

### Décorateur `@fail_on_overfetch`

```python
from payload_sentinel.decorators import fail_on_overfetch

@fail_on_overfetch()
def test_api_returns_minimal_payload(self):
    return self.client.get("/api/users/")  # sur-sélection → test échoue
```

### Décorateur `@fail_on_sensitive_leak`

```python
from payload_sentinel.decorators import fail_on_sensitive_leak

@fail_on_sensitive_leak()
def test_no_password_in_response(self):
    return self.client.get("/api/profile/")
```

### Décorateur `@payload_sentinel_guard`

Vérifie sur-sélection **et** fuites sensibles en une seule passe.

## Architecture

Service Layer strict :

| Module | Rôle |
|--------|------|
| `collector.py` | Capture SQL via `execute_wrapper` |
| `sql_parser.py` | Extraction colonnes SELECT |
| `response_inspector.py` | Aplatissement JSON + détection sensible |
| `analyzer.py` | Comparaison SQL vs payload |
| `services.py` | Orchestration + politiques |
| `selectors.py` | Lecture configuration |
| `middleware.py` | Surveillance passive HTTP |

```powershell
uv run payload-sentinel --preview
```

## Développement

```powershell
cd payload-sentinel
uv sync --extra dev
uv run payload-sentinel --test
uv run payload-sentinel --help
```

## Licence

MIT
