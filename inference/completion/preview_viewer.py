"""Viewer HTML interactif pour preview PlantUML (zoom + pan)."""

from __future__ import annotations

import html
import re
from pathlib import Path


def _sanitize_svg(svg: str) -> str:
    """Évite la fermeture prématurée de balises script dans le HTML."""
    return re.sub(r"</script>", r"<\\/script>", svg, flags=re.IGNORECASE)


def build_interactive_html(svg: str, *, title: str) -> str:
    """Construit une page HTML avec zoom (molette) et pan (glisser)."""
    safe_title = html.escape(title)
    safe_svg = _sanitize_svg(svg.strip())
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>
    * {{ margin: 0; box-sizing: border-box; }}
    body {{
      overflow: hidden;
      background: #18181b;
      color: #fafafa;
      font-family: Inter, system-ui, sans-serif;
    }}
    #toolbar {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 10;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      padding: 8px 12px;
      background: #27272a;
      border-bottom: 1px solid #3f3f46;
    }}
    button {{
      padding: 6px 12px;
      border: 1px solid #52525b;
      background: #3f3f46;
      color: #fafafa;
      cursor: pointer;
      border-radius: 4px;
      font-size: 13px;
    }}
    button:hover {{ background: #52525b; }}
    #hint {{
      color: #a1a1aa;
      font-size: 12px;
      margin-left: auto;
    }}
    #viewport {{
      width: 100vw;
      height: 100vh;
      padding-top: 48px;
      cursor: grab;
      overflow: hidden;
      touch-action: none;
    }}
    #viewport.grabbing {{ cursor: grabbing; }}
    #canvas {{
      transform-origin: 0 0;
      display: inline-block;
    }}
    #canvas svg {{
      display: block;
      max-width: none;
      height: auto;
    }}
  </style>
</head>
<body>
  <div id="toolbar">
    <button type="button" id="zoom-in" title="Zoom avant">+</button>
    <button type="button" id="zoom-out" title="Zoom arrière">−</button>
    <button type="button" id="reset" title="Réinitialiser">Reset</button>
    <button type="button" id="fit" title="Ajuster à l'écran">Ajuster</button>
    <span id="hint">Molette : zoom · Glisser : déplacer · Double-clic : ajuster</span>
  </div>
  <div id="viewport">
    <div id="canvas">{safe_svg}</div>
  </div>
  <script>
    const viewport = document.getElementById("viewport");
    const canvas = document.getElementById("canvas");
    let scale = 1;
    let panX = 0;
    let panY = 0;
    let dragging = false;
    let startX = 0;
    let startY = 0;

    function applyTransform() {{
      canvas.style.transform = `translate(${{panX}}px, ${{panY}}px) scale(${{scale}})`;
    }}

    function fitToView() {{
      const svg = canvas.querySelector("svg");
      if (!svg) return;
      const rect = viewport.getBoundingClientRect();
      const bbox = svg.getBBox();
      const svgW = bbox.width || svg.clientWidth || 1;
      const svgH = bbox.height || svg.clientHeight || 1;
      scale = Math.min((rect.width - 32) / svgW, (rect.height - 32) / svgH, 1.5);
      panX = (rect.width - svgW * scale) / 2;
      panY = (rect.height - svgH * scale) / 2;
      applyTransform();
    }}

    viewport.addEventListener("wheel", (event) => {{
      event.preventDefault();
      const factor = event.deltaY > 0 ? 0.9 : 1.1;
      const rect = viewport.getBoundingClientRect();
      const mx = event.clientX - rect.left;
      const my = event.clientY - rect.top;
      const newScale = Math.min(Math.max(scale * factor, 0.05), 20);
      panX = mx - (mx - panX) * (newScale / scale);
      panY = my - (my - panY) * (newScale / scale);
      scale = newScale;
      applyTransform();
    }}, {{ passive: false }});

    viewport.addEventListener("mousedown", (event) => {{
      dragging = true;
      startX = event.clientX - panX;
      startY = event.clientY - panY;
      viewport.classList.add("grabbing");
    }});

    window.addEventListener("mousemove", (event) => {{
      if (!dragging) return;
      panX = event.clientX - startX;
      panY = event.clientY - startY;
      applyTransform();
    }});

    window.addEventListener("mouseup", () => {{
      dragging = false;
      viewport.classList.remove("grabbing");
    }});

    viewport.addEventListener("dblclick", fitToView);

    document.getElementById("zoom-in").addEventListener("click", () => {{
      scale = Math.min(scale * 1.25, 20);
      applyTransform();
    }});
    document.getElementById("zoom-out").addEventListener("click", () => {{
      scale = Math.max(scale / 1.25, 0.05);
      applyTransform();
    }});
    document.getElementById("reset").addEventListener("click", () => {{
      scale = 1;
      panX = 0;
      panY = 0;
      applyTransform();
    }});
    document.getElementById("fit").addEventListener("click", fitToView);

    window.addEventListener("load", fitToView);
    window.addEventListener("resize", fitToView);
  </script>
</body>
</html>
"""


def write_interactive_preview(
    path: Path,
    svg: str,
    *,
    title: str,
) -> Path:
    """Écrit la page HTML interactive sur disque."""
    resolved = path.resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(build_interactive_html(svg, title=title), encoding="utf-8")
    return resolved
