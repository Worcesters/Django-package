"""CLI de preview PlantUML embarqué (package_archi.puml → SVG dans le navigateur)."""

from __future__ import annotations

import argparse
import base64
import sys
import webbrowser
import zlib
from importlib import resources
from pathlib import Path

import httpx

from inference.conf import format_settings_help

PUML_RELATIVE_PATH = "docs/package_archi.puml"
KROKI_BASE_URL = "https://kroki.io"
KROKI_RENDER_URL = f"{KROKI_BASE_URL}/plantuml/svg"


def load_puml() -> str:
    """Charge le diagramme PlantUML embarqué dans le package."""
    puml_path = resources.files("inference").joinpath(PUML_RELATIVE_PATH)
    return puml_path.read_text(encoding="utf-8")


def build_kroki_preview_url(
    puml_source: str,
    *,
    kroki_base_url: str = KROKI_BASE_URL,
) -> str:
    """Construit une URL Kroki GET : le SVG s'affiche directement dans le navigateur."""
    compressed = zlib.compress(puml_source.encode("utf-8"), level=9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    base = kroki_base_url.rstrip("/")
    return f"{base}/plantuml/svg/{encoded}"


def render_svg(puml_source: str, *, kroki_render_url: str = KROKI_RENDER_URL) -> str:
    """Envoie le source PlantUML à Kroki (POST) et retourne le SVG."""
    response = httpx.post(
        kroki_render_url,
        content=puml_source.encode("utf-8"),
        headers={"Content-Type": "text/plain"},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Ouvre le diagramme d'architecture django-inference dans le navigateur "
            "(rendu en ligne via Kroki, aucun fichier local par défaut)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=format_settings_help(),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        metavar="FICHIER",
        help="Enregistre aussi le SVG localement (ex. docs/architecture.svg).",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="N'ouvre pas le navigateur (affiche uniquement l'URL Kroki).",
    )
    parser.add_argument(
        "--kroki-base-url",
        default=KROKI_BASE_URL,
        help="URL de base du service Kroki (défaut : kroki.io).",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    try:
        puml = load_puml()
        preview_url = build_kroki_preview_url(puml, kroki_base_url=args.kroki_base_url)
    except FileNotFoundError:
        print(
            f"Erreur : {PUML_RELATIVE_PATH} introuvable dans le package inference.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None

    print(f"Preview : {preview_url}")

    if args.output is not None:
        try:
            kroki_render_url = f"{args.kroki_base_url.rstrip('/')}/plantuml/svg"
            svg = render_svg(puml, kroki_render_url=kroki_render_url)
        except httpx.HTTPError as exc:
            print(f"Erreur lors du téléchargement SVG : {exc}", file=sys.stderr)
            raise SystemExit(1) from None

        output = args.output.resolve()
        output.write_text(svg, encoding="utf-8")
        print(f"SVG enregistré : {output}")

    if not args.no_open:
        webbrowser.open(preview_url)


if __name__ == "__main__":
    main()
