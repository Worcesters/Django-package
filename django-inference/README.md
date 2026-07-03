# django-inference

Package Django installable via **uv** depuis Git.

## Installation dans un projet existant

Apres avoir pousse ce depot sur GitHub/GitLab :

```powershell
cd chemin/vers/votre/projet-django
uv add "django-inference @ git+https://github.com/VOTRE_ORG/django-inference.git"
```

Branche ou tag specifique :

```powershell
uv add "django-inference @ git+https://github.com/VOTRE_ORG/django-inference.git@main"
uv add "django-inference @ git+https://github.com/VOTRE_ORG/django-inference.git@v0.1.0"
```

## CLI `inference`

```powershell
# Aide + snippet des constantes Django INFERENCE_*
uv run inference --help

# Preview architecture (PlantUML → SVG en ligne, navigateur)
uv run inference --preview

# Preview sans ouvrir le navigateur (URL Kroki dans le terminal)
uv run inference --preview --no-open
```

### Preview architecture

Le package embarque un diagramme PlantUML (`inference/docs/package_archi.puml`).

Avec `--preview` :

1. Charge le `.puml` embarque
2. Construit une **URL Kroki** (diagramme encode dans l'URL)
3. **Ouvre le navigateur** par defaut (sauf `--no-open`)
4. Affiche l'URL dans le terminal

**Aucun fichier n'est ecrit dans ton projet par defaut.**

Options supplementaires :

```powershell
uv run inference --preview -o docs/architecture.svg
uv run inference --preview --kroki-base-url https://kroki.mondomaine.local
```

| Commande | Description |
|----------|-------------|
| `uv run inference --help` | Aide CLI + snippet `INFERENCE_*` pour les settings |
| `uv run inference --preview` | Ouvre la preview Kroki dans le navigateur |
| `uv run inference --preview --no-open` | Affiche uniquement l'URL Kroki |
| `uv run inference --preview -o FICHIER` | Enregistre en plus une copie SVG locale |

Constantes Django documentees dans `--help` :

- `INFERENCE_DEFAULT_PROVIDER`
- `INFERENCE_PROVIDERS`
- `INFERENCE_RETRY` (optionnel)

### Prerequis preview

- Connexion **reseau** requise (rendu delegue a Kroki)
- Pas besoin de Java ni de PlantUML installe localement

### Developpement local (editable)

```powershell
uv add --editable ./chemin/vers/django-inference
uv run inference --preview
```

## Utilisation Python (inférence)

```python
from inference.services import complete

result = complete(messages=[{"role": "user", "content": "Bonjour"}])
print(result.text)
```

## Configuration Django

Dans `config/settings/base.py` :

```python
INSTALLED_APPS = [
    # ...
    "inference.apps.InferenceConfig",
]

INFERENCE_DEFAULT_PROVIDER = "llama"
INFERENCE_PROVIDERS = {
    "llama": {
        "backend": "inference.providers.ollama.OllamaProvider",
        "base_url": "http://ton-ollama:11434",
        "model": "llama3.2",
    },
}
```

Snippet complet : `uv run inference --help`

## Structure

- `inference/cli.py` — commande `uv run inference`
- `inference/preview.py` — logique preview PlantUML
- `inference/services.py` — `complete()` (inférence texte)
- `inference/conf.py` — constantes `INFERENCE_*`
- `inference/factory.py` — `LLMFactory`
- `inference/providers/` — `OpenAIProvider`, `MistralProvider`, `OllamaProvider`
- `inference/docs/package_archi.puml` — diagramme d'architecture
- `pyproject.toml` — metadata pip/uv (hatchling)
