# inference

Package Django installable via **uv** depuis Git.

## Installation dans un projet existant

Apres avoir pousse ce depot sur GitHub/GitLab :

```powershell
cd chemin/vers/votre/projet-django
uv add "inference @ git+https://github.com/VOTRE_ORG/package_llm_inference.git"
```

Branche ou tag specifique :

```powershell
uv add "inference @ git+https://github.com/VOTRE_ORG/package_llm_inference.git@main"
uv add "inference @ git+https://github.com/VOTRE_ORG/package_llm_inference.git@v0.1.0"
```

## CLI `inference`

```powershell
# Aide + snippet des constantes Django INFERENCE_*
uv run inference --help

# Preview architecture (PlantUML → SVG en ligne, navigateur)
uv run inference --preview

# Preview sans ouvrir le navigateur (URL Kroki dans le terminal)
uv run inference --preview --no-open

# Test de completion (projet Django hôte configuré)
uv run inference --complete "Bonjour, qui es-tu ?" --settings config.settings.dev

# Provider explicite (Ollama local)
uv run inference -c "2+2 ?" --provider llama --settings config.settings.dev
```

### Test de completion (`--complete`)

La commande appelle `complete()` avec les settings Django du projet hôte (`INFERENCE_*`).

**Prérequis :**

1. `INFERENCE_DEFAULT_PROVIDER` et `INFERENCE_PROVIDERS` définis dans tes settings
2. `--settings` pointant vers ton module Django (ou `DJANGO_SETTINGS_MODULE` exporté)
3. Clé API / Ollama accessible selon le provider

```powershell
# Depuis ton projet Django (package installé via uv add)
cd chemin/vers/votre/projet-django
uv run inference --complete "Explique Django en une phrase." --settings config.settings.dev

# Provider explicite
uv run inference -c "Hello" --provider openai --settings config.settings.dev

# Variable d'environnement à la place de --settings
$env:DJANGO_SETTINGS_MODULE = "config.settings.dev"
uv run inference --complete "Hello"
```

| Option | Description |
|--------|-------------|
| `--complete`, `-c PROMPT` | Message utilisateur envoyé au LLM |
| `--provider NOM` | Provider dans `INFERENCE_PROVIDERS` (sinon défaut) |
| `--settings MODULE` | Module settings Django (`config.settings.dev`) |

La réponse s'affiche sur **stdout** ; métadonnées (modèle, tokens) sur **stderr**.

### Preview architecture

Le package embarque un diagramme PlantUML (`app/docs/package_archi.puml`).

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
| `uv run inference --complete "..." --settings config.settings.dev` | Teste une completion LLM |
| `uv run inference -c "..." --provider llama --settings ...` | Completion avec provider explicite |

Constantes Django documentees dans `--help` :

- `INFERENCE_DEFAULT_PROVIDER`
- `INFERENCE_PROVIDERS`
- `INFERENCE_RETRY` (optionnel)

### Prerequis preview

- Connexion **reseau** requise (rendu delegue a Kroki)
- Pas besoin de Java ni de PlantUML installe localement

### Developpement local (editable)

```powershell
uv add --editable ./chemin/vers/inference
uv run inference --preview
```

## Utilisation Python (inférence)

```python
from app.services import complete

result = complete(messages=[{"role": "user", "content": "Bonjour"}])
print(result.text)
```

## Configuration Django

Dans `config/settings/base.py` :

```python
INSTALLED_APPS = [
    # ...
    "app.apps.InferenceConfig",
]

INFERENCE_DEFAULT_PROVIDER = "llama"
INFERENCE_PROVIDERS = {
    "llama": {
        "backend": "app.providers.ollama.OllamaProvider",
        "base_url": "http://ton-ollama:11434",
        "model": "llama3.2",
    },
}
```

Snippet complet : `uv run inference --help`

## Structure

- `app/cli.py` — commande `uv run inference`
- `app/preview.py` — logique preview PlantUML
- `app/services.py` — `complete()` (inférence texte)
- `app/conf.py` — constantes `INFERENCE_*`
- `app/factory.py` — `LLMFactory`
- `app/providers/` — `OpenAIProvider`, `MistralProvider`, `OllamaProvider`
- `app/docs/package_archi.puml` — diagramme d'architecture
- `pyproject.toml` — metadata pip/uv (hatchling)
