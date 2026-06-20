from __future__ import annotations

import copy
import xml.etree.ElementTree as ET
from pathlib import Path

from .config import DEFAULT_LIMITS, DEFAULT_WORKING_DIRS
from .schema import (
    DistributionSpec,
    FileInputSpec,
    FunctionSpec,
    ModelSpec,
    PoemInputState,
    XmlSummary,
    join_csv,
    split_csv,
)


def read_xml(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_xml_text(xml_text: str) -> ET.Element:
    return ET.fromstring(xml_text.strip())


def element_to_text(root: ET.Element) -> str:
    root_copy = copy.deepcopy(root)
    ET.indent(root_copy, space="  ")
    body = ET.tostring(root_copy, encoding="unicode")
    return '<?xml version="1.0" ?>\n' + body + "\n"


def parse_bool(text: str | None) -> bool:
    return str(text or "").strip().lower() in {"true", "1", "yes", "y"}


def child_text(parent: ET.Element | None, tag: str, default: str = "") -> str:
    if parent is None:
        return default
    node = parent.find(tag)
    if node is None or node.text is None:
        return default
    return node.text.strip()


def optional_child(parent: ET.Element, tag: str, text: str | int | None) -> None:
    if text is None:
        return
    value = str(text).strip()
    if value:
        ET.SubElement(parent, tag).text = value


def state_from_xml(root: ET.Element) -> PoemInputState:
    global_settings = root.find("GlobalSettings")
    run_info = root.find("RunInfo")

    analysis_type = child_text(global_settings, "AnalysisType", "lhs").lower()
    state = PoemInputState(
        analysis_type=analysis_type,
        limit=child_text(global_settings, "limit", str(DEFAULT_LIMITS.get(analysis_type, 10))),
        inputs=split_csv(child_text(global_settings, "Inputs", "x, y")),
        outputs=split_csv(child_text(global_settings, "Outputs", "OutputPlaceHolder")),
        dynamic=parse_bool(child_text(global_settings, "dynamic", "False")),
        pivot=child_text(global_settings, "pivot", "time"),
        polynomial_order=child_text(global_settings, "PolynomialOrder", "2"),
        sparse_grid_data=child_text(global_settings, "SparseGridData", ""),
        data=child_text(global_settings, "data", ""),
        initial_inputs=child_text(global_settings, "InitialInputs", ""),
        working_dir=child_text(run_info, "WorkingDir", DEFAULT_WORKING_DIRS.get(analysis_type, "workdir")),
        batch_size=child_text(run_info, "batchSize", "1"),
        job_name=child_text(run_info, "JobName", ""),
        raw_attributes=dict(root.attrib),
    )

    distributions = []
    distributions_node = root.find("Distributions")
    if distributions_node is not None:
        for dist in list(distributions_node):
            params = {child.tag: (child.text or "").strip() for child in list(dist)}
            distributions.append(
                DistributionSpec(
                    name=dist.attrib.get("name", ""),
                    dist_type=dist.tag,
                    params=params,
                )
            )
    state.distributions = distributions

    models = []
    models_node = root.find("Models")
    if models_node is not None:
        for model in models_node.findall("ExternalModel"):
            models.append(
                ModelSpec(
                    name=model.attrib.get("name", ""),
                    module_to_load=model.attrib.get("ModuleToLoad", ""),
                    sub_type=model.attrib.get("subType", ""),
                    inputs=split_csv(child_text(model, "inputs", "")),
                    outputs=split_csv(child_text(model, "outputs", "")),
                )
            )
    state.models = models

    files = []
    files_node = root.find("Files")
    if files_node is not None:
        for item in files_node.findall("Input"):
            files.append(
                FileInputSpec(
                    name=item.attrib.get("name", ""),
                    path=(item.text or "").strip(),
                    file_type=item.attrib.get("type", ""),
                )
            )
    state.files = files

    functions = []
    functions_node = root.find("Functions")
    if functions_node is not None:
        for func in functions_node.findall("External"):
            functions.append(
                FunctionSpec(
                    name=func.attrib.get("name", ""),
                    file=func.attrib.get("file", ""),
                    variables=split_csv(child_text(func, "variables", "")),
                )
            )
    state.functions = functions

    likelihood = root.find("LikelihoodModel")
    if likelihood is not None:
        state.likelihood_model_xml = element_to_text(likelihood).replace('<?xml version="1.0" ?>\n', "", 1).strip()

    return state


def state_to_xml(state: PoemInputState) -> ET.Element:
    root = ET.Element("Simulation", state.raw_attributes)

    run_info = ET.SubElement(root, "RunInfo")
    optional_child(run_info, "WorkingDir", state.working_dir)
    optional_child(run_info, "batchSize", state.batch_size)
    optional_child(run_info, "JobName", state.job_name)

    global_settings = ET.SubElement(root, "GlobalSettings")
    ET.SubElement(global_settings, "AnalysisType").text = state.analysis_type
    optional_child(global_settings, "limit", state.limit)
    ET.SubElement(global_settings, "Inputs").text = join_csv(state.inputs)
    ET.SubElement(global_settings, "Outputs").text = join_csv(state.outputs)
    if state.dynamic:
        ET.SubElement(global_settings, "pivot").text = state.pivot or "time"
        ET.SubElement(global_settings, "dynamic").text = "True"
    if state.analysis_type in {"sparse_grid_construction", "sparse_grid_rom"}:
        optional_child(global_settings, "PolynomialOrder", state.polynomial_order)
    if state.analysis_type == "sparse_grid_rom":
        optional_child(global_settings, "SparseGridData", state.sparse_grid_data)
    if state.analysis_type in {"train_rom", "bayesian_optimization"}:
        optional_child(global_settings, "data", state.data)
    if state.initial_inputs:
        optional_child(global_settings, "InitialInputs", state.initial_inputs)

    if state.distributions:
        distributions_node = ET.SubElement(root, "Distributions")
        for dist in state.distributions:
            dist_node = ET.SubElement(distributions_node, dist.dist_type, {"name": dist.name})
            for key, value in dist.params.items():
                optional_child(dist_node, key, value)

    if state.models:
        models_node = ET.SubElement(root, "Models")
        for model in state.models:
            model_node = ET.SubElement(
                models_node,
                "ExternalModel",
                {"ModuleToLoad": model.module_to_load, "name": model.name, "subType": model.sub_type},
            )
            ET.SubElement(model_node, "inputs").text = join_csv(model.inputs)
            ET.SubElement(model_node, "outputs").text = join_csv(model.outputs)

    if state.files:
        files_node = ET.SubElement(root, "Files")
        for file_input in state.files:
            ET.SubElement(files_node, "Input", {"name": file_input.name, "type": file_input.file_type}).text = file_input.path

    if state.functions:
        functions_node = ET.SubElement(root, "Functions")
        for func in state.functions:
            func_node = ET.SubElement(functions_node, "External", {"file": func.file, "name": func.name})
            ET.SubElement(func_node, "variables").text = join_csv(func.variables)

    if state.analysis_type == "model_calibration" and state.likelihood_model_xml.strip():
        likelihood_root = parse_xml_text(state.likelihood_model_xml)
        root.append(likelihood_root)

    return root


def state_to_xml_text(state: PoemInputState) -> str:
    return element_to_text(state_to_xml(state))


def summarize_xml(path: Path | None, xml_text: str) -> XmlSummary:
    try:
        root = parse_xml_text(xml_text)
        state = state_from_xml(root)
        return XmlSummary(
            path=path,
            analysis_type=state.analysis_type,
            inputs=state.inputs,
            outputs=state.outputs,
            dynamic=state.dynamic,
            working_dir=state.working_dir,
            valid_xml=root.tag == "Simulation",
            error="" if root.tag == "Simulation" else "Root element is not Simulation",
        )
    except Exception as exc:
        return XmlSummary(path=path, valid_xml=False, error=str(exc))


def default_distributions(inputs: list[str]) -> list[DistributionSpec]:
    return [
        DistributionSpec(name=name, dist_type="Uniform", params={"lowerBound": "-10", "upperBound": "10"})
        for name in inputs
    ]


def write_xml(path: Path, xml_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(xml_text, encoding="utf-8")

