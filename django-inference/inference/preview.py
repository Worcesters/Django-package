"""Preview PlantUML embarqué (package_archi.puml → SVG via Kroki)."""

from __future__ import annotations

import base64
import sys
import webbrowser
import zlib
from importlib import resources
from pathlib import Path

import httpx

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


def run_preview(
    *,
    output: Path | None = None,
    no_open: bool = False,
    kroki_base_url: str = KROKI_BASE_URL,
) -> None:
    """Lance la preview architecture (URL Kroki + ouverture navigateur optionnelle)."""
    try:
        puml = load_puml()
        preview_url = build_kroki_preview_url(puml, kroki_base_url=kroki_base_url)
    except FileNotFoundError:
        print(
            f"Erreur : {PUML_RELATIVE_PATH} introuvable dans le package inference.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None

    print(f"Preview : {preview_url}")

    if output is not None:
        try:
            kroki_render_url = f"{kroki_base_url.rstrip('/')}/plantuml/svg"
            svg = render_svg(puml, kroki_render_url=kroki_render_url)
        except httpx.HTTPError as exc:
            print(f"Erreur lors du téléchargement SVG : {exc}", file=sys.stderr)
            raise SystemExit(1) from None

        resolved_output = output.resolve()
        resolved_output.write_text(svg, encoding="utf-8")
        print(f"SVG enregistré : {resolved_output}")

    if not no_open:
        webbrowser.open(preview_url)
