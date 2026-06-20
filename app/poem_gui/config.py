from __future__ import annotations

from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = APP_DIR.parent
TESTS_DIR = REPO_ROOT / "tests"
DOCS_SOURCE_DIR = REPO_ROOT / "docs" / "source"
WORKSPACES_DIR = APP_DIR / "workspaces"
DEFAULT_WORKSPACE = WORKSPACES_DIR / "default"

SUPPORTED_ANALYSES = [
    "mc",
    "lhs",
    "train_rom",
    "sparse_grid_construction",
    "sparse_grid_rom",
    "sensitivity",
    "bayesian_optimization",
    "model_calibration",
]

ANALYSIS_LABELS = {
    "mc": "Monte Carlo",
    "lhs": "Latin Hypercube Sampling",
    "train_rom": "Train Gaussian Process ROM",
    "sparse_grid_construction": "Sparse Grid Construction",
    "sparse_grid_rom": "Sparse Grid ROM",
    "sensitivity": "Sensitivity Analysis",
    "bayesian_optimization": "Bayesian Optimization",
    "model_calibration": "Model Calibration",
}

ANALYSIS_SUMMARIES = {
    "mc": "Random model exploration with Monte Carlo sampling.",
    "lhs": "Random model exploration with Latin Hypercube Sampling.",
    "train_rom": "Train a Gaussian Process ROM from existing data.",
    "sparse_grid_construction": "Generate sparse-grid locations for experiment design.",
    "sparse_grid_rom": "Train a Gaussian Polynomial Chaos ROM from sparse-grid data.",
    "sensitivity": "Run static or dynamic sensitivity and uncertainty analysis.",
    "bayesian_optimization": "Run Bayesian optimization with a model and optional existing data.",
    "model_calibration": "Run Bayesian model calibration with a likelihood model.",
}

ANALYSIS_DOCS = {
    "mc": DOCS_SOURCE_DIR / "mc.rst",
    "lhs": DOCS_SOURCE_DIR / "lhs.rst",
    "train_rom": DOCS_SOURCE_DIR / "rom.rst",
    "sparse_grid_construction": DOCS_SOURCE_DIR / "sparsegrid.rst",
    "sparse_grid_rom": DOCS_SOURCE_DIR / "rom.rst",
    "sensitivity": DOCS_SOURCE_DIR / "sen.rst",
    "bayesian_optimization": DOCS_SOURCE_DIR / "bayesian.rst",
    "model_calibration": DOCS_SOURCE_DIR / "calibration.rst",
}

DEFAULT_WORKING_DIRS = {
    "mc": "MC",
    "lhs": "LHS",
    "train_rom": "GP",
    "sparse_grid_construction": "SparseGrid",
    "sparse_grid_rom": "SparseGrid",
    "sensitivity": "sauq_runs",
    "bayesian_optimization": "Optimization",
    "model_calibration": "calibration",
}

DEFAULT_LIMITS = {
    "mc": 10,
    "lhs": 10,
    "train_rom": 10,
    "sparse_grid_construction": 10,
    "sparse_grid_rom": 10,
    "sensitivity": 10,
    "bayesian_optimization": 10,
    "model_calibration": 100,
}

COMMON_XML_NAMES = {
    "input": "poem_input.xml",
    "generated": "raven_poem_input.xml",
}

