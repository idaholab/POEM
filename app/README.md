# POEM Streamlit GUI

Run from the repository root:

```bash
uv sync --python 3.11
uv run --with-requirements app/requirements.txt streamlit run app/streamlit_app.py
```

The app stores generated inputs, generated RAVEN XML, and run logs under
`app/workspaces/` by default. The workspace contents are ignored by git.

Pages:

- `POEM`: project introduction.
- `Examples`: load XML examples from `tests/`, edit, validate, run prerequisite
  tests, run POEM, and inspect CSV/Python outputs.
- `Build Workflow`: select `AnalysisType`, build a custom XML input from
  test-backed defaults, run POEM, and visualize results.
- `Help`: rendered POEM documentation, supported analyses, and a standalone XML
  editor.

Generate-only mode is the default. Enable the RAVEN run option only when the
selected model dependencies are available.
