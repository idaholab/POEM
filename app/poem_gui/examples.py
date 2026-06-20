from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .config import TESTS_DIR
from .schema import XmlSummary
from .xml_io import read_xml, summarize_xml


@dataclass
class ExampleInfo:
    path: Path
    summary: XmlSummary
    expected_outputs: list[str] = field(default_factory=list)
    prereq: str = ""
    skip: str = ""


def _parse_test_catalog(catalog_path: Path) -> dict[str, dict[str, str]]:
    if not catalog_path.exists():
        return {}

    catalog: dict[str, dict[str, str]] = {}
    current: dict[str, str] | None = None
    current_name = ""

    test_header = re.compile(r"\[\./([^\]]+)\]")
    assignment = re.compile(r"^\s*([A-Za-z_]+)\s*=\s*'([^']*)'")

    for line in catalog_path.read_text(encoding="utf-8").splitlines():
        header_match = test_header.search(line)
        if header_match:
            current_name = header_match.group(1)
            current = {}
            catalog[current_name] = current
            continue
        if current is None:
            continue
        assignment_match = assignment.search(line)
        if assignment_match:
            current[assignment_match.group(1)] = assignment_match.group(2)

    by_input = {}
    for item in catalog.values():
        input_name = item.get("input")
        if input_name:
            by_input[input_name] = item
    return by_input


def discover_examples(tests_dir: Path = TESTS_DIR) -> list[ExampleInfo]:
    catalog = _parse_test_catalog(tests_dir / "tests")
    examples: list[ExampleInfo] = []

    for path in sorted(tests_dir.glob("*.xml")):
        xml_text = read_xml(path)
        summary = summarize_xml(path, xml_text)
        metadata = catalog.get(path.name, {})
        examples.append(
            ExampleInfo(
                path=path,
                summary=summary,
                expected_outputs=metadata.get("output", "").split(),
                prereq=metadata.get("prereq", ""),
                skip=metadata.get("skip", metadata.get("skip_if_OS", "")),
            )
        )

    return examples


def group_examples_by_analysis(examples: list[ExampleInfo]) -> dict[str, list[ExampleInfo]]:
    grouped: dict[str, list[ExampleInfo]] = {}
    for example in examples:
        key = example.summary.analysis_type or "unknown"
        grouped.setdefault(key, []).append(example)
    return grouped


def load_example(path: Path) -> str:
    return read_xml(path)

