from __future__ import annotations

from xml.etree.ElementTree import ParseError

from .config import SUPPORTED_ANALYSES
from .schema import PoemInputState, ValidationReport
from .xml_io import parse_xml_text, state_from_xml


def validate_xml_text(xml_text: str) -> ValidationReport:
    report = ValidationReport()
    try:
        root = parse_xml_text(xml_text)
    except ParseError as exc:
        report.add_error(f"XML parse error: {exc}", "xml")
        return report
    except Exception as exc:
        report.add_error(str(exc), "xml")
        return report

    if root.tag != "Simulation":
        report.add_error("Root element must be Simulation.", "Simulation")
        return report

    return validate_state(state_from_xml(root))


def validate_state(state: PoemInputState) -> ValidationReport:
    report = ValidationReport()

    if state.analysis_type not in SUPPORTED_ANALYSES:
        report.add_error(f"Unsupported AnalysisType: {state.analysis_type}", "AnalysisType")

    if not state.inputs:
        report.add_error("GlobalSettings Inputs must contain at least one variable.", "Inputs")

    if not state.outputs:
        report.add_error("GlobalSettings Outputs must contain at least one variable.", "Outputs")

    if state.limit:
        try:
            if int(float(state.limit)) <= 0:
                report.add_error("limit must be positive.", "limit")
        except ValueError:
            report.add_error("limit must be numeric.", "limit")

    if state.batch_size:
        try:
            if int(float(state.batch_size)) <= 0:
                report.add_error("batchSize must be positive.", "batchSize")
        except ValueError:
            report.add_error("batchSize must be numeric.", "batchSize")

    dist_names = {dist.name for dist in state.distributions if dist.name}
    for input_name in state.inputs:
        if input_name not in dist_names:
            report.add_error(f'Input "{input_name}" does not have a matching distribution.', "Distributions")

    for dist in state.distributions:
        if not dist.name:
            report.add_error("Distribution is missing a name.", "Distributions")
        if dist.dist_type == "Uniform":
            if "lowerBound" not in dist.params or "upperBound" not in dist.params:
                report.add_error(f'Uniform distribution "{dist.name}" needs lowerBound and upperBound.', "Distributions")
        if dist.dist_type == "Normal":
            if "mean" not in dist.params or "sigma" not in dist.params:
                report.add_error(f'Normal distribution "{dist.name}" needs mean and sigma.', "Distributions")

    if state.dynamic and not state.pivot:
        report.add_error("Dynamic workflows require a pivot variable.", "pivot")

    if state.analysis_type == "train_rom" and not state.data:
        report.add_error("train_rom requires GlobalSettings data.", "data")

    if state.analysis_type == "sparse_grid_rom" and not state.sparse_grid_data:
        report.add_error("sparse_grid_rom requires GlobalSettings SparseGridData.", "SparseGridData")

    if state.analysis_type == "bayesian_optimization":
        if len(state.outputs) != 1:
            report.add_error("bayesian_optimization supports exactly one output objective.", "Outputs")
        if not state.models:
            report.add_warning("Bayesian optimization usually needs a model block.", "Models")
        if not state.data:
            report.add_warning("No existing data file is configured; POEM will remove the data-loading steps.", "data")

    if state.analysis_type == "model_calibration" and not state.likelihood_model_xml.strip():
        report.add_error("model_calibration requires a LikelihoodModel block.", "LikelihoodModel")

    if state.analysis_type in {"sensitivity", "sparse_grid_construction", "sparse_grid_rom", "bayesian_optimization", "model_calibration"}:
        if not state.models:
            report.add_warning(f"{state.analysis_type} usually needs a Models block.", "Models")

    for model in state.models:
        if not model.name:
            report.add_error("ExternalModel is missing a name.", "Models")
        if not model.module_to_load:
            report.add_error(f'ExternalModel "{model.name or "<unnamed>"}" is missing ModuleToLoad.', "Models")
        if not model.inputs:
            report.add_warning(f'ExternalModel "{model.name or "<unnamed>"}" has no inputs.', "Models")
        if not model.outputs:
            report.add_warning(f'ExternalModel "{model.name or "<unnamed>"}" has no outputs.', "Models")

    return report

