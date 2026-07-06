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

# README coloré dans le terminal
uv run inference --readme

# Preview architecture (PlantUML → SVG en ligne, navigateur)
uv run inference --preview

# Preview sans ouvrir le navigateur (URL Kroki dans le terminal)
uv run inference --preview --no-open

# Lancer les tests Pytest
uv run inference --test

# Tests avec settings Django explicites
uv run inference --test --settings config.settings.dev

# Standalone — config JSON avant tests
uv run inference --test --config ./inference.json
```

### Tests Pytest (`--test`)

Lance la suite de tests du package (`uv run pytest` équivalent).

```powershell
cd chemin/vers/inference
uv run inference --test

# Avec module Django settings
uv run inference --test --settings tests.settings

# Arguments pytest supplémentaires (après --test)
uv run inference --test -- -v -k test_factory
```

| Option | Description |
|--------|-------------|
| `--test` | Lance la suite Pytest du package |
| `--settings MODULE` | Module settings Django (`config.settings.dev`) |
| `--config FICHIER` | Fichier JSON standalone (pour commandes métier) |

### Configuration standalone (`--config`)

Même structure que les settings Django, dans un fichier JSON. Les clés API restent dans l'environnement (`api_key_env`).

Exemple `inference.json` (modèle embarqué : `completion/examples/inference.dev.json`) :

```json
{
  "INFERENCE_DEFAULT_PROVIDER": "openai",
  "INFERENCE_PROVIDERS": {
    "openai": {
      "backend": "completion.providers.openai.OpenAIProvider",
      "model": "gpt-4o",
      "api_key_env": "OPENAI_API_KEY",
      "base_url": "https://api.openai.com/v1"
    }
  }
}
```

```powershell
$env:OPENAI_API_KEY = "sk-..."
uv run inference --test --config ./inference.json
```

**Lambda** — charger au cold start :

```python
from completion.settings_source import configure_from_file
from completion.services import complete

configure_from_file("inference.json")

def handler(event, context):
    result = complete(messages=[{"role": "user", "content": event["prompt"]}])
    return {"statusCode": 200, "body": result.text}
```

`--settings` et `--config` sont **mutuellement exclusifs**.

### Preview architecture (interactive)

Avec `--preview` :

1. Charge le `.puml` embarqué et le rend via **Kroki**
2. Génère un **viewer HTML** local (zoom molette, glisser pour déplacer)
3. **Ouvre le navigateur** sur ce viewer (sauf `--no-open`)
4. Affiche aussi l'URL Kroki statique dans le terminal

**Contrôles du viewer :** molette = zoom · clic maintenu = pan · boutons +/- / Reset / Ajuster · double-clic = ajuster à l'écran

```powershell
uv run inference --preview
uv run inference --preview --no-open
uv run inference --preview -o docs/architecture.svg
uv run inference --preview --html-output docs/architecture.html
```

| Commande | Description |
|----------|-------------|
| `uv run inference --help` | Aide CLI + snippet `INFERENCE_*` pour les settings |
| `uv run inference --preview` | Ouvre le viewer HTML interactif (zoom/pan) |
| `uv run inference --preview --no-open` | Affiche les chemins preview sans ouvrir le navigateur |
| `uv run inference --preview -o FICHIER` | Enregistre en plus une copie SVG locale |
| `uv run inference --preview --html-output FICHIER.html` | Enregistre le viewer HTML à un chemin fixe |
| `uv run inference --test` | Lance la suite Pytest |
| `uv run inference --test --settings config.settings.dev` | Tests avec settings Django |
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

### Appel direct

```python
from completion.services import complete

result = complete(messages=[{"role": "user", "content": "Bonjour"}])
print(result.text)
```

### Exemple minimal dans ton app métier

`apps/assistant/services.py` :

```python
from __future__ import annotations

from completion.exceptions import InferenceError
from completion.services import complete


def ask_assistant(*, question: str, provider: str | None = None) -> str:
    """Pose une question au LLM et retourne le texte de réponse."""
    result = complete(
        messages=[{"role": "user", "content": question}],
        provider=provider,  # None = INFERENCE_DEFAULT_PROVIDER
    )
    return result.text
```

Appel depuis une vue DRF (orchestration seulement) :

```python
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assistant.services import ask_assistant
from completion.exceptions import InferenceError


class AskView(APIView):
    def post(self, request):
        question = request.data.get("question", "").strip()
        if not question:
            return Response({"error": "question requise"}, status=400)

        try:
            answer = ask_assistant(question=question)
        except InferenceError as exc:
            return Response(
                {"error": exc.message, "code": exc.code},
                status=502,
            )

        return Response({"answer": answer})
```

### Exemple avec historique de conversation

```python
from completion.services import complete


def chat_with_context(
    *,
    user_message: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    messages = list(history or [])
    messages.append({"role": "user", "content": user_message})
    result = complete(messages=messages)
    return result.text
```

Usage :

```python
history = [
    {"role": "user", "content": "Je m'appelle Julien."},
    {"role": "assistant", "content": "Enchanté Julien !"},
]
reply = chat_with_context(
    user_message="Comment je m'appelle ?",
    history=history,
)
```

### Ce que tu récupères

`complete()` retourne un `CompletionResult` :

```python
result = complete(messages=[{"role": "user", "content": "Bonjour"}])

result.text            # texte généré
result.model           # ex. "llama3.2"
result.usage.total_tokens
result.finish_reason   # ex. "stop"
result.raw             # réponse brute de l'API
```

### Points importants

- **Import** : `from completion.services import complete` — c'est le package **inference** installé (module `completion`), pas ton dossier `apps/`.
- **`provider=None`** → utilise `INFERENCE_DEFAULT_PROVIDER` de tes settings.
- **`provider="openai"`** → utilise l'entrée correspondante dans `INFERENCE_PROVIDERS`.
- **Pas besoin de `django.setup()`** dans ton service : Django est déjà initialisé via `runserver`, Celery, ou `manage.py`.
- **Gestion d'erreurs** : attrape `InferenceError` (ou les sous-classes : `ProviderAPIError`, `ProviderConnectionError`, etc.).

## Configuration Django

Dans `config/settings/base.py` :

```python
INSTALLED_APPS = [
    # ...
    "completion.apps.InferenceConfig",
]

INFERENCE_DEFAULT_PROVIDER = "llama"
INFERENCE_PROVIDERS = {
    "llama": {
        "backend": "completion.providers.ollama.OllamaProvider",
        "base_url": "http://ton-ollama:11434",
        "model": "llama3.2",
    },
}
```

Snippet complet : `uv run inference --help`

## Structure

- `completion/cli.py` — commande `uv run inference`
- `completion/complete_cmd.py` — orchestration completion (usage programmatique / tests)
- `completion/preview.py` — preview PlantUML (via `base-cmd`)
- `completion/services.py` — `complete()` (inférence texte)
- `completion/selectors.py` — lecture settings `INFERENCE_*`
- `completion/settings_source.py` — config Django / JSON / Lambda
- `completion/examples/inference.dev.json` — modèle JSON standalone
- `completion/factory.py` — `LLMFactory`
- `completion/schemas.py` — `CompletionResult`, `LLMConfig`, `TokenUsage`
- `completion/providers/` — `OpenAIProvider`, `MistralProvider`, `OllamaProvider`
- `completion/docs/package_archi.puml` — diagramme d'architecture
- `pyproject.toml` — metadata pip/uv (hatchling)
