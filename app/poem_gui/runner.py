from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .config import MODELS_DIR, REPO_ROOT
from .schema import RunResult


def poem_command() -> list[str]:
    poem_path = shutil.which("poem")
    if poem_path:
        return [poem_path]
    return [sys.executable, "-m", "POEM.src.main"]


def raven_available() -> bool:
    return shutil.which("raven_framework") is not None


def copy_example_models(workspace: Path) -> list[Path]:
    if not MODELS_DIR.exists():
        raise FileNotFoundError(f"Models directory was not found: {MODELS_DIR}")

    workspace = workspace.expanduser()
    source = MODELS_DIR.resolve()
    destinations = []
    for destination in (workspace / "models", workspace.parent / "models"):
        resolved = destination.resolve()
        if resolved != source and resolved not in destinations:
            destinations.append(resolved)

    copied_destinations = []
    for destination in destinations:
        if destination.exists():
            continue
        shutil.copytree(
            source,
            destination,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
        copied_destinations.append(destination)
    return copied_destinations


def environment_status() -> dict[str, str | bool]:
    return {
        "python": sys.executable,
        "poem_command": " ".join(poem_command()),
        "poem_on_path": shutil.which("poem") is not None,
        "raven_framework_on_path": raven_available(),
        "repo_root": str(REPO_ROOT),
    }


def run_poem(
    input_path: Path,
    output_path: Path,
    no_run: bool = True,
    cwd: Path = REPO_ROOT,
    timeout: int = 900,
) -> RunResult:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = poem_command() + ["-i", str(input_path), "-o", str(output_path)]
    if no_run:
        command.append("-nr")

    started = datetime.now().isoformat(timespec="seconds")
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    finished = datetime.now().isoformat(timespec="seconds")
    return RunResult(
        command=command,
        return_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        input_path=input_path,
        output_path=output_path,
        started_at=started,
        finished_at=finished,
    )


def write_run_log(workspace: Path, result: RunResult) -> Path:
    workspace.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = workspace / f"run_{timestamp}.json"
    index = 1
    while path.exists():
        path = workspace / f"run_{timestamp}_{index}.json"
        index += 1
    path.write_text(json.dumps(result.as_dict(), indent=2), encoding="utf-8")
    return path
