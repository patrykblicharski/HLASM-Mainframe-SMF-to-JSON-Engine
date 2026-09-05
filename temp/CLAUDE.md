# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Project language:** English for code, comments, and documentation. Conversation with the human owner may be in Polish, but all artifacts in the repo should remain in English.

**Module design notes:** longer “why” context lives in [`MODULE_NOTES.md`](MODULE_NOTES.md). Keep file-header docstrings to one short line.

## Project goal (target, from the project description)

A web application for fetching, decoding, and presenting SMF (System Management Facilities) data from z/OS in a readable form. Data is ultimately fetched via IBM z/OS Data Gatherer (REST API) and processed with [IBM SMF Explorer](https://github.com/IBM/IBM-SMF-Explorer) (the `smfexplorer` library). Future phase: an AI module for anomaly detection and event prediction based on SMF records.

## Repository structure

```
SMF-Project/
├── smf-explorer-app/   — main app: NiceGUI UI + real smfexplorer (per-browser sessions)
├── smf-mock/           — sandbox mock of z/OS Data Gatherer REST API (for smfexplorer without a z/OS host)
├── smf_webapp/         — earlier minimal FastAPI + vanilla-JS + smfexplorer prototype
└── smf119-app/         — offline SMF Type 119 decoder (ezasmf/ezbnmmpc layouts; no Gatherer)
```

Components are not wired together in code — there are no shared modules or cross-imports. Treat them as separate applications in one repository.

Removed prototype `smf-explorer-nicegui/` (100% synthetic data, no `smfexplorer`) — replaced by `smf-explorer-app/`.

## Environments (venv) — one per component

Each component has its **own, isolated** `.venv` (Python 3.11 — required by `smfexplorer`: 3.9–3.11, `pandas<2.0`/`numpy<2.0`). Isolation is intentional: `smf-mock` may use newer dependency versions, while `smf-explorer-app` / `smf_webapp` must stay on IBM pins.

```bash
py -3.11 -m venv smf-explorer-app/.venv
py -3.11 -m venv smf-mock/.venv
py -3.11 -m venv smf_webapp/.venv
```

## Commands

### `smf-explorer-app/` (port 8080)

Windows (recommended):

```bat
cd smf-explorer-app
start.bat
```

Manual:

```bash
cd smf-explorer-app
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\pip install vendor/smfexplorer-1.1.13-py3-none-any.whl
.venv\Scripts\python main.py
# → http://localhost:8080
# In the console: Q key shuts down the server (app.shutdown).
```

### `smf-mock/` (port 9000)

```bash
cd smf-mock
.venv\Scripts\pip install -r requirements-mock.txt
.venv\Scripts\python -m uvicorn mock_server.main:app --port 9000 --reload
# → http://127.0.0.1:9000
```

### `smf_webapp/` (port 8000)

```bash
cd smf_webapp
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\pip install vendor/smfexplorer-1.1.13-py3-none-any.whl
.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
# → http://localhost:8000
```

### `smf119-app/` (desktop Tkinter; no server)

```bash
cd smf119-app
py -3 main.py
# Offline SMF Type 119 dump explorer (stdlib only)
```

### Server testing pattern (bash)

Long-running server processes — start, poll until the port is ready, and run HTTP tests in a single bash invocation:

```bash
python main.py &                                    # smf-explorer-app, port 8080
# or: uvicorn mock_server.main:app --port 9000 &   # smf-mock
# or: uvicorn app.main:app --port 8000 &           # smf_webapp
SERVER_PID=$!
# poll curl until the port responds, then run HTTP tests
curl ...
kill $SERVER_PID
```

No unit tests in the repository — verify manually by starting the server and checking in the browser / with curl.

## Architecture — `smf-explorer-app/`

Main production application: NiceGUI + real `smfexplorer` wheel. Each browser session signs in at `/login` to its own Gatherer host (mock or z/OS) and gets its own `Environment` (`app_core/session.py`) — no global data state.

- `main.py` — `ui.run` (port 8080); `app_core/console_quit.py` — Q key in the console shuts down the server.
- `start.bat` + `start_tools.py` — universal Windows launcher (config at top of `.bat`): `.venv`, Python pin, optional ZIP runtime / installer download, deps, start.
- `app_core/` — config, `smfexplorer` session, query layer.
- `smf_types/` — SMF type catalog, cross-analyses (non-ML), DataFrame → UI mapping.
- `webui/` — login, dashboard, type views, KPI/charts/tables/export.
- `vendor/smfexplorer-1.1.13-py3-none-any.whl` — IBM wheel.

Connecting to the mock: URL `http://127.0.0.1:9000/zosmf/zosdg/smf`, dataset `TEST.SMF.DATASET` / `DEV.SMF.SANDBOX`, TLS off. Cutover plan for a real host: `PROD_CUTOVER_PLAN.md`.

## Architecture — `smf-mock/`

**This is not another UI version.** It is a FastAPI stand-in for *z/OS Data Gatherer: SMF Data REST Services*, so `smf-explorer-app/` / `smf_webapp/` can be developed without a z/OS host.

- `mock_server/main.py` — FastAPI endpoints (api-docs, discover, type/subtype), Basic auth, `?_mock_status=...`.
- `mock_server/generator.py` — fake records from OpenAPI schemas (47 type/subtype pairs).
- `mock_server/datasets.py` — `TEST.SMF.DATASET`, `DEV.SMF.SANDBOX`.
- `mock_server/openapi_spec.json` — full IBM spec.

**Known simplifications:** no real filtering by time/system; random data without business correlations; schema-accurate field names. Pitfall: Python 3.12 + `pandas>=2.0` breaks `smfexplorer` on text fields — use 3.9–3.11 / `pandas<2.0`.

## Architecture — `smf_webapp/`

Earlier minimal FastAPI + vanilla-JS + `smfexplorer` prototype (results table, no charts/export). Still useful as a thin API client; the main UI is `smf-explorer-app/`.

- `app/core/smf_session.py` — only place that imports `smfexplorer`; sessions per cookie, `new_environment(...)`.
- `app/api/` — connection / discovery / query.
- `app/static/index.html` — frontend.
- `vendor/smfexplorer-1.1.13-py3-none-any.whl`.

## Open questions / to decide

- Keep `smf_webapp/` in parallel, or eventually retire it in favor of `smf-explorer-app/` alone?
- Target database / persistence for historical data (currently: in-process memory / query result).
- AI approach for cross-analyses (heuristics vs. real ML) — current analyses are intentionally non-ML.
- Cutover to real z/OS — checklist in `PROD_CUTOVER_PLAN.md`.
