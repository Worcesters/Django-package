"""Preview PlantUML via Kroki (partagé entre packages)."""

from __future__ import annotations

import base64
import sys
import tempfile
import webbrowser
import zlib
from dataclasses import dataclass
from pathlib import Path

import httpx

from base_cmd.docs import PACKAGE_PUML, load_puml as _load_puml
from base_cmd.preview.viewer import write_interactive_preview

KROKI_BASE_URL = "https://kroki.io"
KROKI_RENDER_URL = f"{KROKI_BASE_URL}/plantuml/svg"


@dataclass(frozen=True)
class PreviewConfig:
    """Configuration preview pour un package hôte."""

    package_module: str
    title: str
    default_html_name: str
    puml_relative_path: str = PACKAGE_PUML


def load_puml(config: PreviewConfig) -> str:
    _ = config.puml_relative_path
    return _load_puml(config.package_module)


def build_kroki_preview_url(
    puml_source: str,
    *,
    kroki_base_url: str = KROKI_BASE_URL,
) -> str:
    compressed = zlib.compress(puml_source.encode("utf-8"), level=9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    base = kroki_base_url.rstrip("/")
    return f"{base}/plantuml/svg/{encoded}"


def render_svg(
    puml_source: str,
    *,
    kroki_render_url: str = KROKI_RENDER_URL,
) -> str:
    response = httpx.post(
        kroki_render_url,
        content=puml_source.encode("utf-8"),
        headers={"Content-Type": "text/plain"},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.text


def run_preview(
    config: PreviewConfig,
    *,
    output: Path | None = None,
    html_output: Path | None = None,
    no_open: bool = False,
    kroki_base_url: str = KROKI_BASE_URL,
) -> None:
    """Affiche le diagramme PlantUML dans un viewer HTML interactif."""
    try:
        puml = load_puml(config)
        preview_url = build_kroki_preview_url(puml, kroki_base_url=kroki_base_url)
    except FileNotFoundError:
        print(
            f"Erreur : {PACKAGE_PUML} introuvable dans {config.package_module}.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None

    kroki_render_url = f"{kroki_base_url.rstrip('/')}/plantuml/svg"
    try:
        svg = render_svg(puml, kroki_render_url=kroki_render_url)
    except httpx.HTTPError as exc:
        print(f"Erreur Kroki : {exc}", file=sys.stderr)
        print(f"URL statique : {preview_url}", file=sys.stderr)
        if not no_open:
            webbrowser.open(preview_url)
        raise SystemExit(1) from None

    default_html = Path(tempfile.gettempdir()) / config.default_html_name
    html_path = write_interactive_preview(
        html_output or default_html,
        svg,
        title=config.title,
    )
    print(f"Preview interactive : file:///{html_path.as_posix()}")
    print(f"URL Kroki (statique) : {preview_url}")

    if output is not None:
        resolved_output = output.resolve()
        resolved_output.write_text(svg, encoding="utf-8")
        print(f"SVG enregistré : {resolved_output}")

    if not no_open:
        webbrowser.open(html_path.as_uri())
