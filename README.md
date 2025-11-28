# gchat-history-dumper

`gchat-history-dumper` is a small CLI tool that exports **Google Chat** messages
from spaces visible to a **Chat app** (service account based).

- Exports messages to **JSON Lines** (`.jsonl`) per space.
- Supports **all spaces** or a **selected list**.
- Supports incremental sync via a **checkpoint file**.
- Optional `--since` parameter to limit by date.

> ⚠️ This uses the **Google Chat API**, not Google Takeout nor Google Vault.  
> It can only see spaces/messages that your Chat app (service account) is allowed to see.

---

## Features

- List spaces visible to the app.
- Dump one or many spaces to JSONL.
- Incremental sync:
  - Per-space checkpoint with last seen timestamp.
- Optional exclusion of direct messages (DMs).

---

## Installation

```bash
pip install gchat-history-dumper
# or from source:
# pip install .
```

---

## Development

This repo is intentionally small; the points below keep day-to-day dev focused.

### Prereqs

- Python >= 3.9
- Service account JSON with Chat API scopes; set `GOOGLE_APPLICATION_CREDENTIALS` to its path for local runs.

### Local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

- Package code should live under `gchat_dumper/` with `cli.py` exposing `main()` (the `gchat-dump` entrypoint).
- Add fixtures under `tests/fixtures/` and sample commands under `examples/` when introducing new behavior.

### Working locally

- Keep changes small: add one feature or bugfix per branch/PR.
- Prefer manual smoke tests against a dedicated test space; avoid production spaces and personal chats.
- Use `python -m gchat_dumper.cli --help` to quickly verify CLI wiring after edits.

### Quality bar

- Add or update tests with `pytest` for any new option, API call, or edge case you touch.
- Lint/format before sending for review: `ruff check .` and `black .` (install if missing).
- Type-hint public functions and keep API error handling explicit (no silent retries).

### Release checklist

- Bump `version` in `pyproject.toml` using semver once a change is ready to ship.
- Build and validate artifacts: `python -m build` then `twine check dist/*`.
- Tag releases `vX.Y.Z` and capture a short change summary in the README or a changelog entry.
