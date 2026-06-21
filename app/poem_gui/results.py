from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


TEXT_SUFFIXES = {".txt", ".log", ".xml", ".rst", ".md", ".json", ".py", ".toml"}
TABLE_SUFFIXES = {".csv", ".tsv"}


@dataclass
class ResultFile:
    path: Path
    relative_path: str
    size: int
    suffix: str


def list_result_files(workspace: Path, max_files: int = 500) -> list[ResultFile]:
    if not workspace.exists():
        return []

    files: list[ResultFile] = []
    for path in sorted(item for item in workspace.rglob("*") if item.is_file()):
        if len(files) >= max_files:
            break
        files.append(
            ResultFile(
                path=path,
                relative_path=str(path.relative_to(workspace)),
                size=path.stat().st_size,
                suffix=path.suffix.lower(),
            )
        )
    return files


def read_text_preview(path: Path, max_chars: int = 20000) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n... truncated ..."
    return text


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES


def is_table_file(path: Path) -> bool:
    return path.suffix.lower() in TABLE_SUFFIXES

