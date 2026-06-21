from __future__ import annotations

from collections.abc import Callable
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st
import streamlit.components.v1 as components

from poem_gui.config import (
    ANALYSIS_LABELS,
    BUILDER_DEFAULT_EXAMPLES,
    COMMON_XML_NAMES,
    DEFAULT_LIMITS,
    DEFAULT_WORKING_DIRS,
    DEFAULT_WORKSPACE,
    DOCS_SOURCE_DIR,
    REPO_ROOT,
    SUPPORTED_ANALYSES,
)
from poem_gui.docs import analysis_summary, docs_path_for_analysis, list_docs, render_doc_html
from poem_gui.examples import ExampleInfo, discover_examples, group_examples_by_analysis, load_example, prerequisite_chain
from poem_gui.results import is_table_file, is_text_file, list_result_files, read_text_preview
from poem_gui.runner import copy_example_models, environment_status, raven_available, run_poem, write_run_log
from poem_gui.schema import (
    DistributionSpec,
    FileInputSpec,
    FunctionSpec,
    ModelSpec,
    PoemInputState,
    join_csv,
    split_csv,
)
from poem_gui.validators import validate_state, validate_xml_text
from poem_gui.xml_io import (
    default_distributions,
    parse_xml_text,
    state_from_xml,
    state_to_xml_text,
    summarize_xml,
    write_xml,
)


st.set_page_config(page_title="POEM GUI", page_icon=None, layout="wide")


def default_state() -> PoemInputState:
    state = PoemInputState()
    state.working_dir = DEFAULT_WORKING_DIRS[state.analysis_type]
    state.limit = str(DEFAULT_LIMITS[state.analysis_type])
    state.distributions = default_distributions(state.inputs)
    return state


def ensure_session() -> None:
    DEFAULT_WORKSPACE.mkdir(parents=True, exist_ok=True)
    if "workspace" not in st.session_state:
        st.session_state.workspace = str(DEFAULT_WORKSPACE)
    if "state" not in st.session_state:
        st.session_state.state = default_state()
    if "xml_text" not in st.session_state:
        st.session_state.xml_text = state_to_xml_text(st.session_state.state)
    if "xml_editor_text" not in st.session_state:
        st.session_state.xml_editor_text = st.session_state.xml_text
    if "last_run" not in st.session_state:
        st.session_state.last_run = None
    if "last_prereq_runs" not in st.session_state:
        st.session_state.last_prereq_runs = []
    if "current_source_label" not in st.session_state:
        st.session_state.current_source_label = "Default builder template"
    if "xml_revision" not in st.session_state:
        st.session_state.xml_revision = 0


def set_current_xml(xml_text: str, source_label: str = "Current XML") -> None:
    st.session_state.xml_text = xml_text
    st.session_state.xml_editor_text = xml_text
    st.session_state.current_source_label = source_label
    st.session_state.xml_revision = st.session_state.get("xml_revision", 0) + 1
    try:
        st.session_state.state = state_from_xml(parse_xml_text(xml_text))
    except Exception:
        pass


def display_report(report) -> None:
    if report.ok and not report.warnings:
        st.success("Validation passed.")
        return
    for issue in report.errors:
        label = f"{issue.field}: " if issue.field else ""
        st.error(label + issue.message)
    for issue in report.warnings:
        label = f"{issue.field}: " if issue.field else ""
        st.warning(label + issue.message)


def render_status_cards() -> None:
    status = environment_status()
    # col1, col2, col3 = st.columns(3)
    # col1.metric("Python", Path(str(status["python"])).name)
    # col2.metric("POEM command", "found" if status["poem_on_path"] else "module fallback")
    # col3.metric("RAVEN", "found" if status["raven_framework_on_path"] else "not on PATH")
    with st.expander("Environment details"):
        st.json(status)


def render_current_xml_summary(xml_text: str | None = None) -> None:
    summary = summarize_xml(None, xml_text or st.session_state.xml_text)
    with st.expander("Current XML summary"):
        st.write(
            {
                "Analysis": summary.analysis_type or "unknown",
                "Inputs": join_csv(summary.inputs) or "-",
                "Outputs": join_csv(summary.outputs) or "-",
                "Dynamic": "yes" if summary.dynamic else "no",
                "Source": st.session_state.current_source_label,
            }
        )
    if summary.error:
        st.warning(summary.error)


def render_workspace_controls(key_prefix: str) -> Path:
    workspace_text = st.text_input(
        "Workspace",
        value=st.session_state.workspace,
        key=f"{key_prefix}_workspace",
        help="Generated POEM inputs, RAVEN XML, logs, and outputs are written here.",
    )
    workspace = Path(workspace_text).expanduser()
    st.session_state.workspace = str(workspace)
    return workspace


def render_xml_editor_panel(
    key_prefix: str,
    title: str = "XML Editor",
    allow_upload: bool = True,
) -> str:
    st.subheader(title)
    if allow_upload:
        uploaded = st.file_uploader("Upload POEM XML", type=["xml"], key=f"{key_prefix}_upload")
        if uploaded is not None:
            upload_id = f"{uploaded.name}:{uploaded.size}"
            last_upload_key = f"{key_prefix}_last_upload"
            if st.session_state.get(last_upload_key) != upload_id:
                set_current_xml(uploaded.getvalue().decode("utf-8"), f"Uploaded {uploaded.name}")
                st.session_state[last_upload_key] = upload_id
                st.success(f"Loaded {uploaded.name}")

    area_key = f"{key_prefix}_xml_area"
    area_revision_key = f"{area_key}_revision"
    if st.session_state.get(area_revision_key) != st.session_state.xml_revision:
        st.session_state[area_key] = st.session_state.xml_editor_text
        st.session_state[area_revision_key] = st.session_state.xml_revision

    xml_text = st.text_area("POEM XML", height=520, key=area_key)
    st.session_state.xml_editor_text = xml_text

    col1, col2, col3 = st.columns(3)
    if col1.button("Validate XML", type="primary", key=f"{key_prefix}_validate"):
        display_report(validate_xml_text(xml_text))
    if col2.button("Use this XML", key=f"{key_prefix}_use"):
        set_current_xml(xml_text, f"Edited in {title}")
        st.success("Current XML updated.")
    col3.download_button(
        "Download XML",
        data=xml_text,
        file_name=COMMON_XML_NAMES["input"],
        mime="application/xml",
        key=f"{key_prefix}_download",
    )

    return xml_text


def render_run_panel(
    key_prefix: str,
    xml_text: str | None = None,
    source_label: str | None = None,
    prepare_workspace: Callable[[Path], list[Path]] | None = None,
    pre_run_steps: list[tuple[str, str, str]] | None = None,
    default_input_name: str | None = None,
    default_output_name: str | None = None,
    default_token: str | None = None,
) -> Path:
    st.subheader("Run")
    workspace = render_workspace_controls(key_prefix)

    default_input_name = default_input_name or COMMON_XML_NAMES["input"]
    default_output_name = default_output_name or f"raven_{default_input_name}"
    default_token = default_token or default_input_name
    input_key = f"{key_prefix}_input_name"
    output_key = f"{key_prefix}_output_name"
    previous_input_key = f"{key_prefix}_previous_input_name"
    default_token_key = f"{key_prefix}_filename_default_token"

    if st.session_state.get(default_token_key) != default_token:
        st.session_state[input_key] = default_input_name
        st.session_state[output_key] = default_output_name
        st.session_state[previous_input_key] = default_input_name
        st.session_state[default_token_key] = default_token
    else:
        st.session_state.setdefault(input_key, default_input_name)
        st.session_state.setdefault(output_key, default_output_name)
        st.session_state.setdefault(previous_input_key, st.session_state[input_key])

    def sync_generated_output_name() -> None:
        previous_input_name = st.session_state.get(previous_input_key, default_input_name)
        previous_output_name = f"raven_{previous_input_name}"
        current_output_name = st.session_state.get(output_key, "")
        current_input_name = st.session_state.get(input_key, default_input_name)
        if not current_output_name or current_output_name == previous_output_name:
            st.session_state[output_key] = f"raven_{current_input_name}"
        st.session_state[previous_input_key] = current_input_name

    col1, col2 = st.columns(2)
    input_name = col1.text_input(
        "POEM input file name",
        key=input_key,
        on_change=sync_generated_output_name,
    )
    output_name = col2.text_input(
        "Generated RAVEN XML file name",
        key=output_key,
    )
    full_run = st.checkbox("Run RAVEN after generating XML", value=False, key=f"{key_prefix}_full_run")

    if full_run and not raven_available():
        st.warning("RAVEN executable was not found on PATH. Generate-only mode is recommended.")

    run_prerequisites = False
    if pre_run_steps:
        run_prerequisites = st.checkbox(
            "Run prerequisite tests first",
            value=True,
            key=f"{key_prefix}_run_prereqs",
        )
        with st.expander("Prerequisite run order", expanded=True):
            for index, (label, step_input_name, _) in enumerate(pre_run_steps, start=1):
                st.write(f"{index}. {label} -> `{step_input_name}`")
        if run_prerequisites and not full_run:
            st.warning(
                "Prerequisite tests are in generate-only mode. Enable the RAVEN run option if dependent CSV outputs are required."
            )

    candidate_xml = xml_text if xml_text is not None else st.session_state.xml_text
    report = validate_xml_text(candidate_xml)
    display_report(report)

    input_path = workspace / input_name
    output_path = workspace / output_name

    def prepare_selected_workspace() -> bool:
        if prepare_workspace is None:
            return True
        try:
            destinations = prepare_workspace(workspace)
        except Exception as exc:
            st.error(f"Could not prepare workspace: {exc}")
            return False
        st.info("Copied models folder to: " + ", ".join(str(path) for path in destinations))
        return True

    def run_prerequisite_steps() -> bool:
        if not run_prerequisites or not pre_run_steps:
            st.session_state.last_prereq_runs = []
            return True

        records = []
        for label, input_filename, step_xml in pre_run_steps:
            step_input_path = workspace / input_filename
            step_output_path = workspace / f"raven_{input_filename}"
            write_xml(step_input_path, step_xml)
            result = run_poem(input_path=step_input_path, output_path=step_output_path, no_run=not full_run)
            log_path = write_run_log(workspace, result)
            records.append({"label": label, "log_path": log_path, "result": result})
            if result.return_code != 0:
                st.session_state.last_prereq_runs = records
                st.session_state.last_run = result
                st.error(f"Prerequisite test failed: {label}. Log: {log_path}")
                return False

        st.session_state.last_prereq_runs = records
        if records:
            st.success(f"Completed {len(records)} prerequisite test(s).")
        return True

    col1, col2 = st.columns(2)
    if col1.button("Save current XML", key=f"{key_prefix}_save"):
        if prepare_selected_workspace():
            set_current_xml(candidate_xml, source_label or st.session_state.current_source_label)
            write_xml(input_path, candidate_xml)
            st.success(f"Saved {input_path}")

    if col2.button("Run POEM", type="primary", disabled=not report.ok, key=f"{key_prefix}_run"):
        if prepare_selected_workspace():
            set_current_xml(candidate_xml, source_label or st.session_state.current_source_label)
            write_xml(input_path, candidate_xml)
            with st.spinner("Running POEM"):
                prerequisites_ok = run_prerequisite_steps()
                if prerequisites_ok:
                    if run_prerequisites and pre_run_steps:
                        st.info("Prerequisite tests finished. Running selected POEM input file.")
                    result = run_poem(input_path=input_path, output_path=output_path, no_run=not full_run)
                    log_path = write_run_log(workspace, result)
                else:
                    result = None
                    log_path = None
            if result is None:
                return workspace
            st.session_state.last_run = result
            if result.return_code == 0:
                st.success(f"POEM completed. Log: {log_path}")
            else:
                st.error(f"POEM failed with return code {result.return_code}. Log: {log_path}")

    if st.session_state.last_prereq_runs:
        with st.expander("Last prerequisite runs"):
            for record in st.session_state.last_prereq_runs:
                result = record["result"]
                st.write(f"{record['label']}: return code `{result.return_code}`, log `{record['log_path']}`")
                st.code(" ".join(result.command), language="bash")

    if st.session_state.last_run is not None:
        result = st.session_state.last_run
        st.markdown("**Last run**")
        st.code(" ".join(result.command), language="bash")
        st.write(f"Return code: `{result.return_code}`")
        if result.stdout:
            with st.expander("stdout", expanded=True):
                st.code(result.stdout)
        if result.stderr:
            with st.expander("stderr", expanded=True):
                st.code(result.stderr)

    return workspace


def render_results_panel(workspace: Path, key_prefix: str) -> None:
    st.subheader("Results")
    st.caption(str(workspace))
    files = [item for item in list_result_files(workspace) if item.suffix in {".csv", ".py"}]
    if not files:
        st.info("No CSV or Python files were found in this workspace.")
        return

    selected = st.selectbox(
        "CSV or Python file",
        files,
        format_func=lambda item: f"{item.relative_path} ({item.size} bytes)",
        key=f"{key_prefix}_result_file",
    )
    st.write(str(selected.path))

    if is_table_file(selected.path):
        try:
            import pandas as pd

            sep = "\t" if selected.path.suffix.lower() == ".tsv" else ","
            frame = pd.read_csv(selected.path, sep=sep)
            st.dataframe(frame, width="stretch")
        except Exception as exc:
            st.warning(f"Could not preview table: {exc}")
            st.code(read_text_preview(selected.path))
    elif is_text_file(selected.path):
        st.code(read_text_preview(selected.path), language=selected.path.suffix.lstrip(".") or None)
    else:
        st.info("Binary or unsupported file type. Use download to inspect it locally.")

    st.download_button(
        "Download selected file",
        data=selected.path.read_bytes(),
        file_name=selected.path.name,
        key=f"{key_prefix}_download_result",
    )


def _distribution_widgets(
    input_names: list[str],
    existing: list[DistributionSpec],
    key_prefix: str,
) -> list[DistributionSpec]:
    existing_by_name = {dist.name: dist for dist in existing}
    specs = []
    st.subheader("Distributions")
    for input_name in input_names:
        current = existing_by_name.get(input_name)
        safe_name = _safe_widget_name(input_name)
        dist_type_key = f"{key_prefix}_dist_type_{safe_name}"
        lower_key = f"{key_prefix}_dist_lower_{safe_name}"
        upper_key = f"{key_prefix}_dist_upper_{safe_name}"
        mean_key = f"{key_prefix}_dist_mean_{safe_name}"
        sigma_key = f"{key_prefix}_dist_sigma_{safe_name}"
        st.session_state.setdefault(
            dist_type_key,
            "Normal" if current is not None and current.dist_type == "Normal" else "Uniform",
        )
        st.session_state.setdefault(lower_key, current.params.get("lowerBound", "-10") if current else "-10")
        st.session_state.setdefault(upper_key, current.params.get("upperBound", "10") if current else "10")
        st.session_state.setdefault(mean_key, current.params.get("mean", "0") if current else "0")
        st.session_state.setdefault(sigma_key, current.params.get("sigma", "1") if current else "1")
        dist_type = st.selectbox(
            f"{input_name} distribution",
            ["Uniform", "Normal"],
            key=dist_type_key,
        )
        if dist_type == "Uniform":
            col1, col2 = st.columns(2)
            lower = col1.text_input(
                f"{input_name} lowerBound",
                key=lower_key,
            )
            upper = col2.text_input(
                f"{input_name} upperBound",
                key=upper_key,
            )
            specs.append(DistributionSpec(input_name, "Uniform", {"lowerBound": lower, "upperBound": upper}))
        else:
            col1, col2 = st.columns(2)
            mean = col1.text_input(
                f"{input_name} mean",
                key=mean_key,
            )
            sigma = col2.text_input(
                f"{input_name} sigma",
                key=sigma_key,
            )
            specs.append(DistributionSpec(input_name, "Normal", {"mean": mean, "sigma": sigma}))
    return specs


def _parse_line_table(text: str, expected: int) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = [part.strip() for part in line.split(",")]
        while len(parts) < expected:
            parts.append("")
        rows.append(parts[:expected])
    return rows


def _safe_widget_name(name: str) -> str:
    return name.replace(" ", "_") or "input"


def _builder_default_state_for_analysis(analysis_type: str) -> tuple[PoemInputState, str]:
    examples = discover_examples()
    by_name = {example.path.name: example for example in examples}
    selected = by_name.get(BUILDER_DEFAULT_EXAMPLES.get(analysis_type, ""))

    if selected is None:
        grouped = group_examples_by_analysis(examples)
        selected = next(iter(grouped.get(analysis_type, [])), None)

    if selected is not None:
        xml_text = load_example(selected.path)
        return state_from_xml(parse_xml_text(xml_text)), f"tests/{selected.path.name}"

    state = default_state()
    state.analysis_type = analysis_type
    state.limit = str(DEFAULT_LIMITS.get(analysis_type, 10))
    state.working_dir = DEFAULT_WORKING_DIRS.get(analysis_type, "workdir")
    state.distributions = default_distributions(state.inputs)
    return state, "built-in defaults"


def _load_builder_widget_state(
    key_prefix: str,
    state: PoemInputState,
    source: str,
    set_analysis: bool = True,
) -> None:
    st.session_state.state = state
    if set_analysis:
        st.session_state[f"{key_prefix}_analysis"] = state.analysis_type
    st.session_state[f"{key_prefix}_defaults_source"] = source
    st.session_state[f"{key_prefix}_limit"] = state.limit or str(DEFAULT_LIMITS.get(state.analysis_type, 10))
    st.session_state[f"{key_prefix}_batch"] = state.batch_size or "1"
    st.session_state[f"{key_prefix}_dynamic"] = state.dynamic
    st.session_state[f"{key_prefix}_working_dir"] = state.working_dir or DEFAULT_WORKING_DIRS.get(state.analysis_type, "workdir")
    st.session_state[f"{key_prefix}_inputs"] = join_csv(state.inputs)
    st.session_state[f"{key_prefix}_outputs"] = join_csv(state.outputs)
    st.session_state[f"{key_prefix}_pivot"] = state.pivot or "time"
    st.session_state[f"{key_prefix}_poly_order"] = state.polynomial_order or "2"
    st.session_state[f"{key_prefix}_sg_data"] = state.sparse_grid_data
    st.session_state[f"{key_prefix}_data"] = state.data
    st.session_state[f"{key_prefix}_initial_inputs"] = state.initial_inputs
    st.session_state[f"{key_prefix}_include_model"] = bool(state.models)

    model = state.models[0] if state.models else ModelSpec(inputs=state.inputs, outputs=state.outputs)
    st.session_state[f"{key_prefix}_model_name"] = model.name or "externalModel"
    st.session_state[f"{key_prefix}_model_module"] = model.module_to_load
    st.session_state[f"{key_prefix}_model_subtype"] = model.sub_type
    st.session_state[f"{key_prefix}_model_inputs"] = join_csv(model.inputs or state.inputs)
    st.session_state[f"{key_prefix}_model_outputs"] = join_csv(model.outputs or state.outputs)
    st.session_state[f"{key_prefix}_files"] = "\n".join(
        f"{item.name},{item.path},{item.file_type}" for item in state.files
    )
    st.session_state[f"{key_prefix}_functions"] = "\n".join(
        f"{item.name},{item.file},{join_csv(item.variables)}" for item in state.functions
    )
    st.session_state[f"{key_prefix}_likelihood"] = state.likelihood_model_xml

    distributions_by_name = {dist.name: dist for dist in state.distributions}
    for input_name in state.inputs:
        dist = distributions_by_name.get(input_name)
        safe_name = _safe_widget_name(input_name)
        dist_type = dist.dist_type if dist and dist.dist_type in {"Uniform", "Normal"} else "Uniform"
        params = dist.params if dist else {}
        st.session_state[f"{key_prefix}_dist_type_{safe_name}"] = dist_type
        st.session_state[f"{key_prefix}_dist_lower_{safe_name}"] = params.get("lowerBound", "-10")
        st.session_state[f"{key_prefix}_dist_upper_{safe_name}"] = params.get("upperBound", "10")
        st.session_state[f"{key_prefix}_dist_mean_{safe_name}"] = params.get("mean", "0")
        st.session_state[f"{key_prefix}_dist_sigma_{safe_name}"] = params.get("sigma", "1")


def _load_builder_defaults_for_selected_analysis(key_prefix: str) -> None:
    analysis = st.session_state[f"{key_prefix}_analysis"]
    state, source = _builder_default_state_for_analysis(analysis)
    _load_builder_widget_state(key_prefix, state, source, set_analysis=False)


def _ensure_builder_defaults(key_prefix: str) -> None:
    initialized_key = f"{key_prefix}_defaults_initialized"
    if st.session_state.get(initialized_key):
        return
    state, source = _builder_default_state_for_analysis(st.session_state.state.analysis_type)
    _load_builder_widget_state(key_prefix, state, source)
    st.session_state[initialized_key] = True


def render_builder_panel(key_prefix: str) -> str:
    st.subheader("Global Settings")
    _ensure_builder_defaults(key_prefix)
    current: PoemInputState = st.session_state.state

    analysis = st.selectbox(
        "AnalysisType",
        SUPPORTED_ANALYSES,
        format_func=lambda item: f"{item} - {ANALYSIS_LABELS.get(item, item)}",
        key=f"{key_prefix}_analysis",
        on_change=_load_builder_defaults_for_selected_analysis,
        args=(key_prefix,),
    )
    current = st.session_state.state
    st.caption(analysis_summary(analysis))
    st.caption(f"Defaults loaded from {st.session_state.get(f'{key_prefix}_defaults_source', 'built-in defaults')}")

    col1, col2, col3 = st.columns(3)
    limit = col1.text_input("limit", key=f"{key_prefix}_limit")
    batch_size = col2.text_input("batchSize", key=f"{key_prefix}_batch")
    dynamic = col3.checkbox("dynamic", key=f"{key_prefix}_dynamic")

    working_dir = st.text_input(
        "WorkingDir",
        key=f"{key_prefix}_working_dir",
    )
    inputs_text = st.text_input("Inputs", key=f"{key_prefix}_inputs")
    outputs_text = st.text_input("Outputs", key=f"{key_prefix}_outputs")
    input_names = split_csv(inputs_text)
    output_names = split_csv(outputs_text)

    pivot = ""
    if dynamic:
        pivot = st.text_input("pivot", key=f"{key_prefix}_pivot")

    polynomial_order = ""
    sparse_grid_data = ""
    data = ""
    initial_inputs = ""

    if analysis in {"sparse_grid_construction", "sparse_grid_rom"}:
        polynomial_order = st.text_input(
            "PolynomialOrder",
            key=f"{key_prefix}_poly_order",
        )
    if analysis == "sparse_grid_rom":
        sparse_grid_data = st.text_input("SparseGridData", key=f"{key_prefix}_sg_data")
    if analysis in {"train_rom", "bayesian_optimization"}:
        data = st.text_input("data", key=f"{key_prefix}_data")
    if analysis == "model_calibration":
        initial_inputs = st.text_input(
            "InitialInputs",
            key=f"{key_prefix}_initial_inputs",
        )

    distributions = _distribution_widgets(input_names, current.distributions, key_prefix)

    st.subheader("Models")
    include_model = st.checkbox(
        "Include ExternalModel",
        key=f"{key_prefix}_include_model",
    )
    models: list[ModelSpec] = []
    if include_model:
        model = current.models[0] if current.models else ModelSpec(inputs=input_names, outputs=output_names)
        col1, col2 = st.columns(2)
        model_name = col1.text_input("Model name", key=f"{key_prefix}_model_name")
        module_to_load = col2.text_input("ModuleToLoad", key=f"{key_prefix}_model_module")
        sub_type = st.text_input("subType", key=f"{key_prefix}_model_subtype")
        model_inputs = st.text_input(
            "Model inputs",
            key=f"{key_prefix}_model_inputs",
        )
        model_outputs = st.text_input(
            "Model outputs",
            key=f"{key_prefix}_model_outputs",
        )
        models.append(
            ModelSpec(
                name=model_name,
                module_to_load=module_to_load,
                sub_type=sub_type,
                inputs=split_csv(model_inputs),
                outputs=split_csv(model_outputs),
            )
        )

    st.subheader("Files")
    file_lines = st.text_area("Files as name,path,type", height=90, key=f"{key_prefix}_files")
    files = [FileInputSpec(name=row[0], path=row[1], file_type=row[2]) for row in _parse_line_table(file_lines, 3)]

    functions: list[FunctionSpec] = []
    if analysis == "bayesian_optimization":
        st.subheader("Functions")
        function_lines = st.text_area(
            "Functions as name,file,variables",
            height=90,
            key=f"{key_prefix}_functions",
        )
        functions = [
            FunctionSpec(name=row[0], file=row[1], variables=split_csv(row[2]))
            for row in _parse_line_table(function_lines, 3)
        ]

    likelihood_xml = ""
    if analysis == "model_calibration":
        st.subheader("LikelihoodModel")
        likelihood_xml = st.text_area(
            "LikelihoodModel XML",
            height=220,
            key=f"{key_prefix}_likelihood",
        )

    next_state = PoemInputState(
        analysis_type=analysis,
        limit=limit,
        inputs=input_names,
        outputs=output_names,
        dynamic=dynamic,
        pivot=pivot or "time",
        polynomial_order=polynomial_order or current.polynomial_order,
        sparse_grid_data=sparse_grid_data,
        data=data,
        initial_inputs=initial_inputs,
        working_dir=working_dir,
        batch_size=batch_size,
        job_name=current.job_name,
        distributions=distributions,
        models=models,
        files=files,
        functions=functions,
        likelihood_model_xml=likelihood_xml,
        raw_attributes=current.raw_attributes,
    )

    report = validate_state(next_state)
    display_report(report)
    preview_xml = state_to_xml_text(next_state)

    col1, col2 = st.columns([1, 1])
    if col1.button("Update current XML", type="primary", key=f"{key_prefix}_build"):
        st.session_state.state = next_state
        set_current_xml(preview_xml, "Builder draft")
        st.success("XML updated from builder.")

    if col2.button("Reset builder", key=f"{key_prefix}_reset"):
        reset, source = _builder_default_state_for_analysis(analysis)
        _load_builder_widget_state(key_prefix, reset, source)
        set_current_xml(state_to_xml_text(reset), f"Builder defaults: {source}")
        st.rerun()

    st.subheader("Preview")
    st.code(preview_xml, language="xml")
    return preview_xml


def render_example_selector() -> tuple[ExampleInfo | None, list[ExampleInfo]]:
    st.subheader("Example Library")
    examples = discover_examples()
    grouped = group_examples_by_analysis(examples)

    if not grouped:
        st.info("No examples were found.")
        return None, []

    analysis = st.selectbox(
        "Analysis type",
        options=sorted(grouped),
        format_func=lambda item: ANALYSIS_LABELS.get(item, item),
        key="example_analysis",
    )
    options = grouped.get(analysis, [])
    selected = st.selectbox(
        "Example input",
        options=options,
        format_func=lambda item: item.path.name,
        key="example_input",
    )

    if not selected:
        st.info("No examples were found for this analysis.")
        return None, []

    summary = selected.summary
    prereqs = prerequisite_chain(selected, examples)
    with st.expander("Example summary from XML"):
        st.write(
            {
                "Test": selected.test_name or "-",
                "Analysis": summary.analysis_type or "unknown",
                "Inputs": join_csv(summary.inputs) or "-",
                "Outputs": join_csv(summary.outputs) or "-",
                "Dynamic": "yes" if summary.dynamic else "no",
            }
        )

    if selected.prereq:
        st.info(f"Prerequisite test: {selected.prereq}")
        if prereqs:
            with st.expander("Prerequisite tests from tests/tests", expanded=True):
                rows = [
                    {
                        "Order": index,
                        "Test": item.test_name,
                        "Input": item.path.name,
                        "Expected outputs": join_csv(item.expected_outputs) or "-",
                    }
                    for index, item in enumerate(prereqs, start=1)
                ]
                st.dataframe(rows, width="stretch", hide_index=True)
        else:
            st.warning("The prerequisite test name was not found in tests/tests.")
    if selected.expected_outputs:
        with st.expander("Expected outputs from tests/tests"):
            st.write(selected.expected_outputs)

    xml_text = load_example(selected.path)
    with st.expander("Read-only example XML"):
        st.code(xml_text, language="xml")

    if st.button("Load example into workflow", type="primary", key="load_example"):
        set_current_xml(xml_text, f"Example: {selected.path.name}")
        st.success(f"Loaded {selected.path.name}")

    return selected, prereqs


def render_docs_panel() -> None:
    st.subheader("Supported Analyses")
    rows = [
        {
            "AnalysisType": analysis,
            "Name": ANALYSIS_LABELS.get(analysis, analysis),
            "Summary": analysis_summary(analysis),
            "Docs": str(docs_path_for_analysis(analysis).relative_to(DOCS_SOURCE_DIR))
            if docs_path_for_analysis(analysis)
            else "-",
        }
        for analysis in SUPPORTED_ANALYSES
    ]
    st.dataframe(rows, width="stretch", hide_index=True)

    st.subheader("Documentation")
    analysis = st.selectbox(
        "Analysis documentation",
        SUPPORTED_ANALYSES,
        format_func=lambda item: f"{item} - {ANALYSIS_LABELS.get(item, item)}",
        key="docs_analysis",
    )
    st.write(analysis_summary(analysis))
    path = docs_path_for_analysis(analysis)
    st.caption(str(path) if path else "No docs path available")

    rendered = render_doc_html(path)
    if rendered.error:
        st.warning(rendered.error)
        st.code(rendered.fallback_text, language="rst")
    else:
        components.html(rendered.html, height=820, scrolling=True)

    with st.expander("All docs files"):
        for doc_path in list_docs():
            st.write(str(doc_path.relative_to(DOCS_SOURCE_DIR)))


def _read_readme() -> str:
    path = REPO_ROOT / "README.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _readme_section(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == f"## {heading}":
            start = index
            break
    if start is None:
        return ""

    section: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        section.append(line)
    return "\n".join(section).strip()


def page_poem_intro() -> None:
    readme = _read_readme()
    intro = readme.split("## Requirements", 1)[0].strip() if readme else ""
    intro_lines = intro.splitlines()
    if intro_lines and intro_lines[0].strip() == "# POEM":
        intro = "\n".join(intro_lines[1:]).strip()

    st.title("POEM")
    if intro:
        st.markdown(intro)
    else:
        st.write("Platform of Optimal Experiment Management")

def page_example_workflow() -> None:
    st.title("Examples")
    st.write("Load a test XML example, edit it in the workspace, run POEM, and inspect generated files.")
    selected, prereqs = render_example_selector()
    st.divider()
    edited_xml = render_xml_editor_panel("example", "Edit Loaded XML", allow_upload=False)
    st.divider()
    pre_run_steps = [
        (f"{item.test_name} ({item.path.name})", item.path.name, load_example(item.path))
        for item in prereqs
    ]
    source_label = f"Example workflow draft: {selected.path.name}" if selected else "Example workflow draft"
    selected_input_name = selected.path.name if selected else COMMON_XML_NAMES["input"]
    workspace = render_run_panel(
        "example_run",
        edited_xml,
        source_label,
        copy_example_models,
        pre_run_steps,
        default_input_name=selected_input_name,
        default_output_name=f"raven_{selected_input_name}",
        default_token=f"example:{selected_input_name}",
    )
    st.divider()
    render_results_panel(workspace, "example_results")


def page_build_workflow() -> None:
    st.title("Build Workflow")
    st.write("Create a POEM input from form fields, generate RAVEN XML, and inspect run outputs.")
    render_status_cards()
    preview_xml = render_builder_panel("builder")
    st.divider()
    workspace = render_run_panel("builder_run", preview_xml, "Builder draft")
    st.divider()
    render_results_panel(workspace, "builder_results")


def page_docs_xml() -> None:
    st.title("Help")
    docs_tab, xml_tab = st.tabs(["Docs", "XML Editor"])
    with docs_tab:
        render_docs_panel()
    with xml_tab:
        render_current_xml_summary()
        render_xml_editor_panel("docs_xml", "Standalone XML Editor", allow_upload=True)


def main() -> None:
    ensure_session()
    pages = {
        "POEM": page_poem_intro,
        "Examples": page_example_workflow,
        "Build Workflow": page_build_workflow,
        "Help": page_docs_xml,
    }

    st.sidebar.title("POEM GUI")
    if st.session_state.get("active_page") not in pages:
        st.session_state.active_page = "POEM"

    for page_name in pages:
        selected = page_name == st.session_state.active_page
        if st.sidebar.button(
            page_name,
            key=f"nav_{page_name.lower().replace(' ', '_')}",
            type="primary" if selected else "secondary",
            use_container_width=True,
        ):
            st.session_state.active_page = page_name
            st.rerun()

    page = st.session_state.active_page
    pages[page]()


if __name__ == "__main__":
    main()
