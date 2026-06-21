from __future__ import annotations

import base64
import html
import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path

from .config import ANALYSIS_DOCS, ANALYSIS_SUMMARIES, DOCS_SOURCE_DIR

try:
    from docutils.core import publish_parts
except ImportError:  # pragma: no cover - exercised only when optional app deps are missing.
    publish_parts = None


@dataclass
class RenderedDoc:
    html: str
    fallback_text: str
    error: str = ""


def analysis_summary(analysis_type: str) -> str:
    return ANALYSIS_SUMMARIES.get(analysis_type, "No summary is available for this analysis type.")


def docs_path_for_analysis(analysis_type: str) -> Path | None:
    return ANALYSIS_DOCS.get(analysis_type)


def read_doc_excerpt(path: Path | None, max_lines: int = 80) -> str:
    if path is None or not path.exists():
        return "Documentation file is not available."
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    excerpt = "\n".join(lines[:max_lines])
    if len(lines) > max_lines:
        excerpt += "\n\n... truncated ..."
    return excerpt


def list_docs() -> list[Path]:
    return sorted(DOCS_SOURCE_DIR.glob("*.rst"))


def render_doc_html(path: Path | None) -> RenderedDoc:
    if path is None or not path.exists():
        return RenderedDoc("", "Documentation file is not available.", "Documentation file is not available.")
    fallback = read_doc_excerpt(path)
    if publish_parts is None:
        return RenderedDoc(
            "",
            fallback,
            "docutils is not installed. Start the app with app/requirements.txt to enable rendered documentation.",
        )

    try:
        source = _normalize_sphinx_rst(path.read_text(encoding="utf-8", errors="replace"))
        parts = publish_parts(
            source=source,
            source_path=str(path),
            writer_name="html5",
            settings_overrides={
                "file_insertion_enabled": False,
                "halt_level": 6,
                "report_level": 5,
                "raw_enabled": False,
                "stylesheet_path": None,
                "traceback": False,
            },
        )
        body = _inline_local_images(parts.get("html_body", ""), path)
        return RenderedDoc(_wrap_html(body), fallback)
    except Exception as exc:
        return RenderedDoc("", fallback, f"Could not render documentation: {exc}")


def _normalize_sphinx_rst(text: str) -> str:
    text = _drop_sphinx_directive_blocks(text)
    text = _replace_sphinx_roles(text)
    return text


def _drop_sphinx_directive_blocks(text: str) -> str:
    sphinx_directives = {
        "toctree",
        "autosummary",
        "automodule",
        "autoclass",
        "autofunction",
        "autodata",
        "autodecorator",
        "autoexception",
        "autoattribute",
        "automethod",
    }
    output: list[str] = []
    skipping = False
    base_indent = 0

    for line in text.splitlines():
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        directive = re.match(r"\.\.\s+([A-Za-z0-9_-]+)::", stripped)
        if directive and directive.group(1) in sphinx_directives:
            skipping = True
            base_indent = indent
            continue

        if skipping:
            if not stripped:
                continue
            if indent > base_indent:
                continue
            skipping = False

        output.append(line)

    return "\n".join(output)


def _replace_sphinx_roles(text: str) -> str:
    roles = (
        "ref",
        "doc",
        "mod",
        "class",
        "func",
        "meth",
        "attr",
        "data",
        "exc",
        "term",
        "command",
        "option",
    )
    role_names = "|".join(roles)
    pattern = re.compile(rf":(?:[A-Za-z0-9_]+:)?(?:{role_names}):`([^`]+)`")

    def replacement(match: re.Match[str]) -> str:
        content = match.group(1)
        angled = re.match(r"(.+?)\s*<[^>]+>$", content)
        return angled.group(1).strip() if angled else content

    return pattern.sub(replacement, text)


def _inline_local_images(rendered_html: str, source_path: Path) -> str:
    pattern = re.compile(r'(<img\b[^>]*\bsrc=")([^"]+)(")', re.IGNORECASE)

    def replacement(match: re.Match[str]) -> str:
        prefix, src, suffix = match.groups()
        if re.match(r"^(?:https?:|data:|/)", src):
            return match.group(0)
        image_path = (source_path.parent / html.unescape(src)).resolve()
        if not image_path.exists() or not image_path.is_file():
            return match.group(0)
        mime_type = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
        data = base64.b64encode(image_path.read_bytes()).decode("ascii")
        return f'{prefix}data:{mime_type};base64,{data}{suffix}'

    return pattern.sub(replacement, rendered_html)


def _wrap_html(body: str) -> str:
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    :root {{
      color-scheme: light;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
      color: #1f2937;
    }}
    body {{
      margin: 0;
      padding: 0 0.25rem 1.5rem;
    }}
    h1, h2, h3, h4 {{
      color: #111827;
      line-height: 1.2;
      margin: 1.1rem 0 0.55rem;
    }}
    p, li {{
      font-size: 0.96rem;
    }}
    a {{
      color: #075985;
      text-decoration: none;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin: 1rem 0;
    }}
    th, td {{
      border: 1px solid #d1d5db;
      padding: 0.45rem 0.55rem;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #f3f4f6;
    }}
    pre {{
      background: #f8fafc;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      overflow-x: auto;
      padding: 0.75rem;
      white-space: pre;
    }}
    code {{
      background: #f3f4f6;
      border-radius: 4px;
      padding: 0.05rem 0.25rem;
    }}
    pre code {{
      background: transparent;
      padding: 0;
    }}
    img {{
      border: 1px solid #e5e7eb;
      border-radius: 6px;
      height: auto;
      margin: 0.75rem 0;
      max-width: 100%;
    }}
  </style>
</head>
<body>
{body}
</body>
</html>"""
