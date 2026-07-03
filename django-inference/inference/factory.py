"""Factory LLM : résolution dynamique des providers (lazy import + cache)."""

from __future__ import annotations

import importlib
from typing import Any

from inference.conf import DEFAULT_PROVIDER_REGISTRY
from inference.exceptions import ProviderNotFoundError
from inference.providers.base import BaseLLMProvider


class LLMFactory:
    """
    Factory LLM : résolution dynamique des providers (lazy import + cache).

    MRO:
    1. __init__ -> registry + instances
    2. register -> ajout/surcharge provider
    3. list_providers -> liste providers supportés
    4. _get_provider_class -> chargement classe provider
    5. get_provider -> instanciation provider
    """

    def __init__(self) -> None:
        self._registry: dict[str, str] = dict(DEFAULT_PROVIDER_REGISTRY)
        self._instances: dict[str, BaseLLMProvider] = {}

    def register(self, name: str, provider_class_path: str) -> None:
        """Permet d'ajouter ou surcharger un provider (settings ou app métier)."""
        self._registry[name.lower()] = provider_class_path
        self._instances.pop(name.lower(), None)

    def list_providers(self) -> list[str]:
        """
        Retourne la liste des providers supportés.
        """

        return sorted(self._registry.keys())

    def _get_provider_class(self, name: str) -> type[BaseLLMProvider]:
        """
        Charge la classe provider à partir du registry.
        """

        path = self._registry.get(name.lower())
        if not path:
            raise ProviderNotFoundError(
                f"Le provider '{name}' n'est pas supporté. "
                f"Options : {self.list_providers()}",
                provider=name,
            )

        module_path, class_name = path.rsplit(".", 1)
        try:
            module = importlib.import_module(module_path)
            provider_class = getattr(module, class_name)
        except ImportError as exc:
            raise ImportError(
                f"Impossible de charger le provider '{name}'. "
                f"As-tu installé le SDK requis ? (Erreur: {exc})"
            ) from exc

        if not isinstance(provider_class, type) or not issubclass(
            provider_class,
            BaseLLMProvider,
        ):
            msg = f"La classe '{path}' n'hérite pas de BaseLLMProvider."
            raise TypeError(msg)

        return provider_class

    def get_provider(
        self,
        name: str,
        config: dict[str, Any],
        *,
        cache_instance: bool = True,
    ) -> BaseLLMProvider:
        """Instancie ou récupère le provider configuré."""
        name_key = name.lower()

        if cache_instance and name_key in self._instances:
            return self._instances[name_key]

        provider_class = self._get_provider_class(name_key)
        instance = provider_class(config)

        if cache_instance:
            self._instances[name_key] = instance

        return instance


llm_factory = LLMFactory()
