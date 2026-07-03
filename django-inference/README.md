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

## Preview architecture (PlantUML → SVG en ligne)

Le package embarque un diagramme PlantUML (`inference/docs/package_archi.puml`). Apres installation, tu peux le visualiser **directement dans le navigateur** sans creer de fichier dans ton projet.

### Utilisation rapide

```powershell
uv add "django-inference @ git+https://github.com/VOTRE_ORG/django-inference.git"
uv run inference-preview
```

Ce que fait la commande :

1. Charge le `.puml` embarque dans le package installe
2. Construit une **URL Kroki** (diagramme encode dans l'URL)
3. **Ouvre le navigateur** : le SVG s'affiche en ligne via [Kroki](https://kroki.io/)
4. Affiche l'URL dans le terminal (copiable / partageable)

**Aucun fichier n'est ecrit dans ton projet par defaut.**

Exemple d'URL generee :

```text
https://kroki.io/plantuml/svg/eNp...
```

Tu peux la coller dans n'importe quel navigateur pour revoir le diagramme sans reinstaller quoi que ce soit.

### Options

```powershell
# Affiche seulement l'URL Kroki (sans ouvrir le navigateur)
uv run inference-preview --no-open

# Preview en ligne + copie locale optionnelle du SVG
uv run inference-preview -o docs/architecture.svg

# Kroki self-hosted (optionnel)
uv run inference-preview --kroki-base-url https://kroki.mondomaine.local

# Snippet des constantes Django à ajouter dans config/settings/base.py
uv run inference-preview --help
```

| Option | Description |
|--------|-------------|
| *(aucune)* | Ouvre la preview Kroki dans le navigateur, 0 fichier local |
| `--help` | Affiche l'aide CLI **et** le snippet `INFERENCE_*` pour les settings |
| `--no-open` | Affiche uniquement l'URL de preview dans le terminal |
| `-o`, `--output FICHIER` | Enregistre en plus une copie SVG sur disque |
| `--kroki-base-url URL` | Change l'instance Kroki utilisee (defaut : `https://kroki.io`) |

Constantes Django documentees dans `--help` :

- `INFERENCE_DEFAULT_PROVIDER`
- `INFERENCE_PROVIDERS`
- `INFERENCE_RETRY` (optionnel)

### Prerequis

- Connexion **reseau** requise (le rendu est delegue a Kroki)
- Pas besoin de Java ni de PlantUML installe localement

### Developpement local (editable)

```powershell
uv add --editable ./chemin/vers/django-inference
uv run inference-preview
```

## Configuration Django

Dans `config/settings/base.py` :

```python
INSTALLED_APPS = [
    # ...
    "inference.apps.InferenceConfig",
]
```

Dans `config/urls.py` :

```python
path("api/inference/", include("inference.urls")),
```

Puis :

```powershell
uv run python manage.py makemigrations inference
uv run python manage.py migrate
```

## Structure

- `inference/` — app Django (models, services, selectors, serializers, views CBV)
- `inference/conf.py` — noms des settings `INFERENCE_*` + snippet d'aide
- `inference/factory.py` — `LLMFactory` (lazy import des providers)
- `inference/providers/` — `OpenAIProvider`, `MistralProvider`, `OllamaProvider`
- `inference/docs/package_archi.puml` — diagramme d'architecture (preview CLI)
- `inference/preview.py` — commande `inference-preview`
- `pyproject.toml` — metadata pip/uv (hatchling)
