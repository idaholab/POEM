from __future__ import annotations

from pathlib import Path

from .config import ANALYSIS_DOCS, ANALYSIS_SUMMARIES, DOCS_SOURCE_DIR


def analysis_summary(analysis_type: str) -> str:
    return ANALYSIS_SUMMARIES.get(analysis_type, "No summary is available for this analysis type.")


def docs_path_for_analysis(analysis_type: str) -> Path | None:
    return ANALYSIS_DOCS.get(analysis_type)


def read_doc_excerpt(path: Path | None, max_lines: int = 160) -> str:
    if path is None or not path.exists():
        return "Documentation file is not available."
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[:max_lines])


def list_docs() -> list[Path]:
    return sorted(DOCS_SOURCE_DIR.glob("*.rst"))

