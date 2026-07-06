# base-cmd

CLI partagée pour tous les packages du monorepo Django.

## Convention docs (identique dans chaque package)

| Fichier | Emplacement dans le module Python |
|---------|-----------------------------------|
| README | `{module}/README.md` (souvent mappé depuis la racine du package) |
| PlantUML | `{module}/docs/package_archi.puml` |

Exemples :
- `completion/README.md` + `completion/docs/package_archi.puml`
- `query_sentinel/README.md` + `query_sentinel/docs/package_archi.puml`

## Commandes ajoutées à chaque CLI

| Flag | Description |
|------|-------------|
| `--help` | Aide colorée |
| `--readme` | README dans le terminal |
| `--preview` | Diagramme PlantUML interactif (Kroki) |
| `--test` | Lance `pytest` |
| `--settings` | Module Django settings |
| `--config` | Fichier JSON standalone |

## Intégration dans un package

```python
from base_cmd.package_cli import (
    PackageCliConfig,
    build_package_parser,
    dispatch_shared_commands,
    print_default_help,
    validate_shared_exclusive,
)

PACKAGE_CLI = PackageCliConfig(
    prog="mon-package",
    package_module="mon_module",
    description="...",
    preview_title="mon-package — architecture",
    setting_prefix="MON_PREFIX",
    module_prefix="mon_module",
    settings_epilog=format_settings_help(),
)

def build_parser():
    return build_package_parser(PACKAGE_CLI)

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    validate_shared_exclusive(parser, args)
    if dispatch_shared_commands(args, PACKAGE_CLI):
        return
    print_default_help(parser)
```

## Développement

```powershell
cd base-cmd
uv sync --extra dev
```
