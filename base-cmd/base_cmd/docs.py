"""Chemins docs standardisés pour tous les packages du monorepo."""

from __future__ import annotations

from importlib import resources

# Convention unique : docs embarqués dans le module Python du package.
PACKAGE_README = "README.md"
PACKAGE_PUML = "docs/package_archi.puml"


def load_readme(package_module: str) -> str:
    """Charge README.md depuis le module package (wheel ou dépôt source)."""
    try:
        readme_ref = resources.files(package_module).joinpath(PACKAGE_README)
        if readme_ref.is_file():
            return readme_ref.read_text(encoding="utf-8")
    except (ModuleNotFoundError, TypeError, FileNotFoundError, OSError):
        pass

    try:
        import importlib
        from pathlib import Path

        mod = importlib.import_module(package_module)
        module_dir = Path(mod.__file__).resolve().parent
        for candidate in (module_dir / PACKAGE_README, module_dir.parent / PACKAGE_README):
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8")
    except (ImportError, AttributeError, TypeError, OSError):
        pass

    raise FileNotFoundError(
        f"{PACKAGE_README} introuvable pour '{package_module}'. "
        f"Emplacement attendu : {package_module}/{PACKAGE_README}"
    )


def load_puml(package_module: str) -> str:
    """Charge docs/package_archi.puml depuis le module package."""
    try:
        puml_ref = resources.files(package_module).joinpath(PACKAGE_PUML)
        if puml_ref.is_file():
            return puml_ref.read_text(encoding="utf-8")
    except (ModuleNotFoundError, TypeError, FileNotFoundError, OSError):
        pass

    try:
        import importlib
        from pathlib import Path

        mod = importlib.import_module(package_module)
        module_dir = Path(mod.__file__).resolve().parent
        for candidate in (module_dir / PACKAGE_PUML, module_dir.parent / PACKAGE_PUML):
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8")
    except (ImportError, AttributeError, TypeError, OSError):
        pass

    raise FileNotFoundError(
        f"{PACKAGE_PUML} introuvable pour '{package_module}'. "
        f"Emplacement attendu : {package_module}/{PACKAGE_PUML}"
    )
