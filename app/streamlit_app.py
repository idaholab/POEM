from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

from poem_gui.config import (
    ANALYSIS_LABELS,
    COMMON_XML_NAMES,
    DEFAULT_LIMITS,
    DEFAULT_WORKING_DIRS,
    DEFAULT_WORKSPACE,
    SUPPORTED_ANALYSES,
)
from poem_gui.docs import analysis_summary, docs_path_for_analysis, list_docs, read_doc_excerpt
from poem_gui.examples import discover_examples, group_examples_by_analysis, load_example
from poem_gui.results import is_table_file, is_text_file, list_result_files, read_text_preview
from poem_gui.runner import environment_status, raven_available, run_poem, write_run_log
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


def set_current_xml(xml_text: str) -> None:
    st.session_state.xml_text = xml_text
    st.session_state.xml_editor_text = xml_text
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
    col1, col2, col3 = st.columns(3)
    col1.metric("Python", Path(str(status["python"])).name)
    col2.metric("POEM command", "found" if status["poem_on_path"] else "module fallback")
    col3.metric("RAVEN", "found" if status["raven_framework_on_path"] else "not on PATH")
    with st.expander("Environment details"):
        st.json(status)


def page_home() -> None:
    st.title("POEM")
    st.caption("Platform of Optimal Experiment Management")
    st.write(
        "Use this local interface to load POEM XML examples, build new inputs, "
        "validate them, generate RAVEN XML, and inspect run outputs."
    )
    render_status_cards()

    st.subheader("Supported analyses")
    rows = [
        {
            "AnalysisType": analysis,
            "Name": ANALYSIS_LABELS.get(analysis, analysis),
            "Summary": analysis_summary(analysis),
        }
        for analysis in SUPPORTED_ANALYSES
    ]
    st.dataframe(rows, width="stretch", hide_index=True)


def page_examples() -> None:
    st.title("Examples")
    examples = discover_examples()
    grouped = group_examples_by_analysis(examples)

    analysis = st.selectbox(
        "Analysis type",
        options=sorted(grouped),
        format_func=lambda item: ANALYSIS_LABELS.get(item, item),
    )
    options = grouped.get(analysis, [])
    selected = st.selectbox(
        "Example input",
        options=options,
        format_func=lambda item: item.path.name,
    )

    if not selected:
        st.info("No examples were found.")
        return

    summary = selected.summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Analysis", summary.analysis_type or "unknown")
    col2.metric("Inputs", join_csv(summary.inputs) or "-")
    col3.metric("Outputs", join_csv(summary.outputs) or "-")
    col4.metric("Dynamic", "yes" if summary.dynamic else "no")

    if selected.prereq:
        st.info(f"Prerequisite test: {selected.prereq}")
    if selected.skip:
        st.warning(f"Skip marker: {selected.skip}")
    if selected.expected_outputs:
        with st.expander("Expected outputs from tests/tests"):
            st.write(selected.expected_outputs)

    xml_text = load_example(selected.path)
    st.code(xml_text, language="xml")

    if st.button("Load example into editor", type="primary"):
        set_current_xml(xml_text)
        st.success(f"Loaded {selected.path.name}")


def _distribution_widgets(input_names: list[str], existing: list[DistributionSpec]) -> list[DistributionSpec]:
    existing_by_name = {dist.name: dist for dist in existing}
    specs = []
    st.subheader("Distributions")
    for input_name in input_names:
        current = existing_by_name.get(input_name)
        dist_type = st.selectbox(
            f"{input_name} distribution",
            ["Uniform", "Normal"],
            index=0 if current is None or current.dist_type != "Normal" else 1,
            key=f"dist_type_{input_name}",
        )
        if dist_type == "Uniform":
            col1, col2 = st.columns(2)
            lower = col1.text_input(
                f"{input_name} lowerBound",
                value=(current.params.get("lowerBound", "-10") if current else "-10"),
                key=f"dist_lower_{input_name}",
            )
            upper = col2.text_input(
                f"{input_name} upperBound",
                value=(current.params.get("upperBound", "10") if current else "10"),
                key=f"dist_upper_{input_name}",
            )
            specs.append(DistributionSpec(input_name, "Uniform", {"lowerBound": lower, "upperBound": upper}))
        else:
            col1, col2 = st.columns(2)
            mean = col1.text_input(
                f"{input_name} mean",
                value=(current.params.get("mean", "0") if current else "0"),
                key=f"dist_mean_{input_name}",
            )
            sigma = col2.text_input(
                f"{input_name} sigma",
                value=(current.params.get("sigma", "1") if current else "1"),
                key=f"dist_sigma_{input_name}",
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


def page_builder() -> None:
    st.title("Builder")
    current: PoemInputState = st.session_state.state

    analysis = st.selectbox(
        "AnalysisType",
        SUPPORTED_ANALYSES,
        index=SUPPORTED_ANALYSES.index(current.analysis_type) if current.analysis_type in SUPPORTED_ANALYSES else 0,
        format_func=lambda item: f"{item} - {ANALYSIS_LABELS.get(item, item)}",
    )
    st.caption(analysis_summary(analysis))

    col1, col2, col3 = st.columns(3)
    limit = col1.text_input("limit", value=current.limit or str(DEFAULT_LIMITS.get(analysis, 10)))
    batch_size = col2.text_input("batchSize", value=current.batch_size or "1")
    dynamic = col3.checkbox("dynamic", value=current.dynamic)

    working_dir = st.text_input("WorkingDir", value=current.working_dir or DEFAULT_WORKING_DIRS.get(analysis, "workdir"))
    inputs_text = st.text_input("Inputs", value=join_csv(current.inputs))
    outputs_text = st.text_input("Outputs", value=join_csv(current.outputs))
    input_names = split_csv(inputs_text)
    output_names = split_csv(outputs_text)

    pivot = ""
    if dynamic:
        pivot = st.text_input("pivot", value=current.pivot or "time")

    polynomial_order = ""
    sparse_grid_data = ""
    data = ""
    initial_inputs = ""

    if analysis in {"sparse_grid_construction", "sparse_grid_rom"}:
        polynomial_order = st.text_input("PolynomialOrder", value=current.polynomial_order or "2")
    if analysis == "sparse_grid_rom":
        sparse_grid_data = st.text_input("SparseGridData", value=current.sparse_grid_data)
    if analysis in {"train_rom", "bayesian_optimization"}:
        data = st.text_input("data", value=current.data)
    if analysis == "model_calibration":
        initial_inputs = st.text_input("InitialInputs", value=current.initial_inputs)

    distributions = _distribution_widgets(input_names, current.distributions)

    st.subheader("Models")
    include_model = st.checkbox("Include ExternalModel", value=bool(current.models) or analysis not in {"lhs", "mc"})
    models: list[ModelSpec] = []
    if include_model:
        model = current.models[0] if current.models else ModelSpec(inputs=input_names, outputs=output_names)
        col1, col2 = st.columns(2)
        model_name = col1.text_input("Model name", value=model.name or "externalModel")
        module_to_load = col2.text_input("ModuleToLoad", value=model.module_to_load)
        sub_type = st.text_input("subType", value=model.sub_type)
        model_inputs = st.text_input("Model inputs", value=join_csv(model.inputs or input_names))
        model_outputs = st.text_input("Model outputs", value=join_csv(model.outputs or output_names))
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
    file_lines_default = "\n".join(f"{item.name},{item.path},{item.file_type}" for item in current.files)
    file_lines = st.text_area("Files as name,path,type", value=file_lines_default, height=90)
    files = [FileInputSpec(name=row[0], path=row[1], file_type=row[2]) for row in _parse_line_table(file_lines, 3)]

    functions: list[FunctionSpec] = []
    if analysis == "bayesian_optimization":
        st.subheader("Functions")
        function_lines_default = "\n".join(
            f"{item.name},{item.file},{join_csv(item.variables)}" for item in current.functions
        )
        function_lines = st.text_area("Functions as name,file,variables", value=function_lines_default, height=90)
        functions = [
            FunctionSpec(name=row[0], file=row[1], variables=split_csv(row[2]))
            for row in _parse_line_table(function_lines, 3)
        ]

    likelihood_xml = ""
    if analysis == "model_calibration":
        st.subheader("LikelihoodModel")
        default_likelihood = current.likelihood_model_xml or (
            '<LikelihoodModel type="normal">\n'
            "  <simTargets>eta</simTargets>\n"
            '  <expTargets shape="1,1" computeCov="False" correlation="False">0.0</expTargets>\n'
            '  <expCov diag="True">0.02</expCov>\n'
            "</LikelihoodModel>"
        )
        likelihood_xml = st.text_area("LikelihoodModel XML", value=default_likelihood, height=220)

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
        distributions=distributions,
        models=models,
        files=files,
        functions=functions,
        likelihood_model_xml=likelihood_xml,
    )

    report = validate_state(next_state)
    display_report(report)

    col1, col2 = st.columns([1, 1])
    if col1.button("Build XML", type="primary"):
        xml_text = state_to_xml_text(next_state)
        st.session_state.state = next_state
        set_current_xml(xml_text)
        st.success("XML updated from builder.")

    if col2.button("Reset builder"):
        reset = default_state()
        st.session_state.state = reset
        set_current_xml(state_to_xml_text(reset))
        st.rerun()

    st.subheader("Preview")
    st.code(state_to_xml_text(next_state), language="xml")


def page_xml_editor() -> None:
    st.title("XML Editor")

    uploaded = st.file_uploader("Upload POEM XML", type=["xml"])
    if uploaded is not None:
        set_current_xml(uploaded.getvalue().decode("utf-8"))
        st.success(f"Loaded {uploaded.name}")

    xml_text = st.text_area("POEM XML", value=st.session_state.xml_editor_text, height=520, key="xml_editor_area")

    col1, col2, col3 = st.columns(3)
    if col1.button("Validate XML", type="primary"):
        report = validate_xml_text(xml_text)
        display_report(report)
    if col2.button("Use this XML"):
        set_current_xml(xml_text)
        st.success("Current XML updated.")
    if col3.download_button("Download XML", data=xml_text, file_name=COMMON_XML_NAMES["input"], mime="application/xml"):
        pass

    summary = summarize_xml(None, xml_text)
    with st.expander("Parsed summary", expanded=True):
        st.json(summary.__dict__)


def page_run() -> None:
    st.title("Run")
    workspace = Path(st.text_input("Workspace", value=st.session_state.workspace)).expanduser()
    st.session_state.workspace = str(workspace)

    col1, col2 = st.columns(2)
    input_name = col1.text_input("POEM input file name", value=COMMON_XML_NAMES["input"])
    output_name = col2.text_input("Generated RAVEN XML file name", value=COMMON_XML_NAMES["generated"])
    full_run = st.checkbox("Run RAVEN after generating XML", value=False)

    if full_run and not raven_available():
        st.warning("RAVEN executable was not found on PATH. Generate-only mode is recommended.")

    input_path = workspace / input_name
    output_path = workspace / output_name
    report = validate_xml_text(st.session_state.xml_text)
    display_report(report)

    col1, col2 = st.columns(2)
    if col1.button("Save current XML"):
        write_xml(input_path, st.session_state.xml_text)
        st.success(f"Saved {input_path}")

    if col2.button("Run POEM", type="primary", disabled=not report.ok):
        write_xml(input_path, st.session_state.xml_text)
        with st.spinner("Running POEM"):
            result = run_poem(input_path=input_path, output_path=output_path, no_run=not full_run)
            log_path = write_run_log(workspace, result)
        st.session_state.last_run = result
        if result.return_code == 0:
            st.success(f"POEM completed. Log: {log_path}")
        else:
            st.error(f"POEM failed with return code {result.return_code}. Log: {log_path}")

    if st.session_state.last_run is not None:
        result = st.session_state.last_run
        st.subheader("Last run")
        st.code(" ".join(result.command), language="bash")
        st.write(f"Return code: `{result.return_code}`")
        if result.stdout:
            with st.expander("stdout", expanded=True):
                st.code(result.stdout)
        if result.stderr:
            with st.expander("stderr", expanded=True):
                st.code(result.stderr)


def page_results() -> None:
    st.title("Results")
    workspace = Path(st.text_input("Workspace directory", value=st.session_state.workspace)).expanduser()
    files = list_result_files(workspace)
    if not files:
        st.info("No result files were found in this workspace.")
        return

    selected = st.selectbox("Result file", files, format_func=lambda item: f"{item.relative_path} ({item.size} bytes)")
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
    )


def page_docs() -> None:
    st.title("Docs")
    analysis = st.selectbox(
        "Analysis documentation",
        SUPPORTED_ANALYSES,
        format_func=lambda item: f"{item} - {ANALYSIS_LABELS.get(item, item)}",
    )
    st.write(analysis_summary(analysis))
    path = docs_path_for_analysis(analysis)
    st.caption(str(path) if path else "No docs path available")
    st.code(read_doc_excerpt(path), language="rst")

    with st.expander("All docs files"):
        for doc_path in list_docs():
            st.write(str(doc_path))


def page_settings() -> None:
    st.title("Settings")
    workspace = st.text_input("Default workspace", value=st.session_state.workspace)
    if st.button("Save settings", type="primary"):
        Path(workspace).expanduser().mkdir(parents=True, exist_ok=True)
        st.session_state.workspace = workspace
        st.success("Settings saved.")

    st.subheader("Current XML state")
    st.json(
        {
            "analysis_type": st.session_state.state.analysis_type,
            "inputs": st.session_state.state.inputs,
            "outputs": st.session_state.state.outputs,
            "workspace": st.session_state.workspace,
            "python": sys.executable,
        }
    )


def main() -> None:
    ensure_session()
    pages = {
        "Home": page_home,
        "Examples": page_examples,
        "Builder": page_builder,
        "XML Editor": page_xml_editor,
        "Run": page_run,
        "Results": page_results,
        "Docs": page_docs,
        "Settings": page_settings,
    }

    st.sidebar.title("POEM GUI")
    page = st.sidebar.radio("Page", list(pages))
    st.sidebar.divider()
    st.sidebar.caption("Current analysis")
    st.sidebar.write(st.session_state.state.analysis_type)
    st.sidebar.caption("Workspace")
    st.sidebar.write(st.session_state.workspace)

    pages[page]()


if __name__ == "__main__":
    main()
