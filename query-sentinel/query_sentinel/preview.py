"""Preview PlantUML embarqué (package_archi.puml → viewer HTML interactif)."""

from __future__ import annotations

import base64
import sys
import tempfile
import webbrowser
import zlib
from importlib import resources
from pathlib import Path

import httpx

from query_sentinel.preview_viewer import write_interactive_preview

PUML_RELATIVE_PATH = "docs/package_archi.puml"
KROKI_BASE_URL = "https://kroki.io"
KROKI_RENDER_URL = f"{KROKI_BASE_URL}/plantuml/svg"
PREVIEW_TITLE = "query-sentinel — architecture"


def load_puml() -> str:
    puml_path = resources.files("query_sentinel").joinpath(PUML_RELATIVE_PATH)
    return puml_path.read_text(encoding="utf-8")


def build_kroki_preview_url(
    puml_source: str,
    *,
    kroki_base_url: str = KROKI_BASE_URL,
) -> str:
    compressed = zlib.compress(puml_source.encode("utf-8"), level=9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    base = kroki_base_url.rstrip("/")
    return f"{base}/plantuml/svg/{encoded}"


def render_svg(puml_source: str, *, kroki_render_url: str = KROKI_RENDER_URL) -> str:
    response = httpx.post(
        kroki_render_url,
        content=puml_source.encode("utf-8"),
        headers={"Content-Type": "text/plain"},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.text


def _default_html_path() -> Path:
    return Path(tempfile.gettempdir()) / "query-sentinel-architecture-preview.html"


def run_preview(
    *,
    output: Path | None = None,
    html_output: Path | None = None,
    no_open: bool = False,
    kroki_base_url: str = KROKI_BASE_URL,
) -> None:
    try:
        puml = load_puml()
        preview_url = build_kroki_preview_url(puml, kroki_base_url=kroki_base_url)
    except FileNotFoundError:
        print(
            f"Erreur : {PUML_RELATIVE_PATH} introuvable dans query_sentinel.",
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

    html_path = write_interactive_preview(
        html_output or _default_html_path(),
        svg,
        title=PREVIEW_TITLE,
    )
    print(f"Preview interactive : file:///{html_path.as_posix()}")
    print(f"URL Kroki (statique) : {preview_url}")

    if output is not None:
        resolved_output = output.resolve()
        resolved_output.write_text(svg, encoding="utf-8")
        print(f"SVG enregistré : {resolved_output}")

    if not no_open:
        webbrowser.open(html_path.as_uri())
