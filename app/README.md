# POEM Streamlit GUI

Run from the repository root:

```bash
uv sync --python 3.11
uv run --with-requirements app/requirements.txt streamlit run app/streamlit_app.py
```

The app stores generated inputs, generated RAVEN XML, and run logs under
`app/workspaces/` by default. The workspace contents are ignored by git.
