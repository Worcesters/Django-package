"""Factories : résolution dynamique embedders et vector stores."""

from __future__ import annotations

import importlib
from typing import Any

from rag.conf import DEFAULT_EMBEDDER_REGISTRY, DEFAULT_STORE_REGISTRY
from rag.embedders.base import BaseEmbedder
from rag.exceptions import EmbedderNotFoundError, StoreNotFoundError
from rag.stores.base import BaseVectorStore


def _normalize_path(path: str, *, legacy_prefix: str, replacement: str) -> str:
    if path.startswith(legacy_prefix):
        return replacement + path[len(legacy_prefix) :]
    return path


class EmbedderFactory:
    """Factory pour les embedders (lazy import + cache)."""

    def __init__(self) -> None:
        self._registry: dict[str, str] = dict(DEFAULT_EMBEDDER_REGISTRY)
        self._instances: dict[str, BaseEmbedder] = {}

    def register(self, name: str, class_path: str) -> None:
        self._registry[name.lower()] = class_path
        self._instances.pop(name.lower(), None)

    def list_embedders(self) -> list[str]:
        return sorted(self._registry.keys())

    def _get_class(self, name: str) -> type[BaseEmbedder]:
        path = _normalize_path(
            self._registry.get(name.lower(), ""),
            legacy_prefix="app.embedders.",
            replacement="rag.embedders.",
        )
        if not path:
            raise EmbedderNotFoundError(
                f"Embedder '{name}' non supporté. Options : {self.list_embedders()}",
                component=name,
            )
        module_path, class_name = path.rsplit(".", 1)
        try:
            module = importlib.import_module(module_path)
            embedder_class = getattr(module, class_name)
        except ImportError as exc:
            raise ImportError(
                f"Impossible de charger l'embedder '{name}'. (Erreur: {exc})"
            ) from exc
        if not isinstance(embedder_class, type) or not issubclass(
            embedder_class, BaseEmbedder
        ):
            msg = f"La classe '{path}' n'hérite pas de BaseEmbedder."
            raise TypeError(msg)
        return embedder_class

    def get_embedder(
        self,
        name: str,
        config: dict[str, Any],
        *,
        cache_instance: bool = True,
    ) -> BaseEmbedder:
        name_key = name.lower()
        if cache_instance and name_key in self._instances:
            return self._instances[name_key]
        instance = self._get_class(name_key)(config)
        if cache_instance:
            self._instances[name_key] = instance
        return instance


class VectorStoreFactory:
    """Factory pour les vector stores (lazy import + cache)."""

    def __init__(self) -> None:
        self._registry: dict[str, str] = dict(DEFAULT_STORE_REGISTRY)
        self._instances: dict[str, BaseVectorStore] = {}

    def register(self, name: str, class_path: str) -> None:
        self._registry[name.lower()] = class_path
        self._instances.pop(name.lower(), None)

    def list_stores(self) -> list[str]:
        return sorted(self._registry.keys())

    def _get_class(self, name: str) -> type[BaseVectorStore]:
        path = _normalize_path(
            self._registry.get(name.lower(), ""),
            legacy_prefix="app.stores.",
            replacement="rag.stores.",
        )
        if not path:
            raise StoreNotFoundError(
                f"Store '{name}' non supporté. Options : {self.list_stores()}",
                component=name,
            )
        module_path, class_name = path.rsplit(".", 1)
        try:
            module = importlib.import_module(module_path)
            store_class = getattr(module, class_name)
        except ImportError as exc:
            raise ImportError(
                f"Impossible de charger le store '{name}'. (Erreur: {exc})"
            ) from exc
        if not isinstance(store_class, type) or not issubclass(
            store_class, BaseVectorStore
        ):
            msg = f"La classe '{path}' n'hérite pas de BaseVectorStore."
            raise TypeError(msg)
        return store_class

    def get_store(
        self,
        name: str,
        config: dict[str, Any],
        *,
        cache_instance: bool = True,
    ) -> BaseVectorStore:
        name_key = name.lower()
        if cache_instance and name_key in self._instances:
            return self._instances[name_key]
        instance = self._get_class(name_key)(config)
        if cache_instance:
            self._instances[name_key] = instance
        return instance


embedder_factory = EmbedderFactory()
store_factory = VectorStoreFactory()
