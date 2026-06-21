from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DistributionSpec:
    name: str
    dist_type: str = "Uniform"
    params: dict[str, str] = field(default_factory=dict)


@dataclass
class ModelSpec:
    name: str = "externalModel"
    module_to_load: str = ""
    sub_type: str = ""
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)


@dataclass
class FileInputSpec:
    name: str
    path: str
    file_type: str = ""


@dataclass
class FunctionSpec:
    name: str
    file: str
    variables: list[str] = field(default_factory=list)


@dataclass
class PoemInputState:
    analysis_type: str = "lhs"
    limit: str = "10"
    inputs: list[str] = field(default_factory=lambda: ["x", "y"])
    outputs: list[str] = field(default_factory=lambda: ["OutputPlaceHolder"])
    dynamic: bool = False
    pivot: str = "time"
    polynomial_order: str = "2"
    sparse_grid_data: str = ""
    data: str = ""
    initial_inputs: str = ""
    working_dir: str = "LHS"
    batch_size: str = "1"
    job_name: str = ""
    distributions: list[DistributionSpec] = field(default_factory=list)
    models: list[ModelSpec] = field(default_factory=list)
    files: list[FileInputSpec] = field(default_factory=list)
    functions: list[FunctionSpec] = field(default_factory=list)
    likelihood_model_xml: str = ""
    raw_attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class ValidationIssue:
    level: str
    message: str
    field: str = ""


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.level == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.level == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def add_error(self, message: str, field: str = "") -> None:
        self.issues.append(ValidationIssue("error", message, field))

    def add_warning(self, message: str, field: str = "") -> None:
        self.issues.append(ValidationIssue("warning", message, field))


@dataclass
class XmlSummary:
    path: Path | None
    analysis_type: str = ""
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    dynamic: bool = False
    working_dir: str = ""
    valid_xml: bool = True
    error: str = ""


@dataclass
class RunResult:
    command: list[str]
    return_code: int
    stdout: str
    stderr: str
    input_path: Path
    output_path: Path
    started_at: str
    finished_at: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "return_code": self.return_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "input_path": str(self.input_path),
            "output_path": str(self.output_path),
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


def split_csv(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def join_csv(items: list[str]) -> str:
    return ", ".join(item for item in items if item)

