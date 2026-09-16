# AGENTS.md

## Project context

This repository contains a Streamlit application whose main entry file is `app.py`.
`app_cal_count.py` is the earlier CLI prototype.

## Working conventions

- Keep the implementation simple and explicit.
- Prefer a single-file script unless the project clearly grows beyond a small utility.
- Use Python 3 standard library features before adding third-party dependencies.
- Name functions and variables clearly; match the domain language used in the task.
- Preserve compatibility with the default Python runtime used in this workspace.
- Never commit `.env`, API keys, the virtual environment, uploaded images, or runtime data.

## Validation

When changing Python code, validate with the smallest relevant command:

- Syntax check: `python -m py_compile app.py`
- Runtime check: `python -m streamlit run app.py` when the app needs manual verification

## Expectations for AI coding agents

- Do not add unnecessary framework or project structure for a one-file script.
- If feature work grows, keep the structure easy to follow and avoid overengineering.
- Prefer targeted edits over broad refactors.
- When in doubt, document assumptions briefly in code comments rather than adding extra complexity.
