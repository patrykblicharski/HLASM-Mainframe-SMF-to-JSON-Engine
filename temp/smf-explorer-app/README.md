# SMF Explorer App

Production-oriented NiceGUI UI on top of IBM `smfexplorer` (z/OS Data Gatherer REST).

Each browser session logs in to its own Gatherer host (mock or real) and gets its own `Environment`. The sidebar menu is driven by **discover** (`get_available_records`) — only SMF types present in the connected dataset are listed.

## Requirements

- Python 3.9–3.11 (required by `smfexplorer`)
- `pandas<2.0`, `numpy<2.0` (pinned in `requirements.txt`)

## Setup

```powershell
cd smf-explorer-app
py -3.11 -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\pip install vendor\smfexplorer-1.1.13-py3-none-any.whl
```

Place the proprietary wheel under `vendor/` if it is not already there (see also `smf_webapp/vendor/`).

## Run

```powershell
# Optional but recommended for non-local use:
$env:SMFAPP_STORAGE_SECRET = "replace-with-a-long-random-string"

.\.venv\Scripts\python main.py
# → http://localhost:8080
```

### Login (mock)

| Field | Example |
|---|---|
| Connection URL | `http://127.0.0.1:9000/zosmf/zosdg/smf` |
| Username / Password | any (unless mock enforces `MOCK_SMF_USER` / `MOCK_SMF_PASSWORD`) |
| Verify TLS | off for mock HTTP |
| Dataset | `TEST.SMF.DATASET` or `DEV.SMF.SANDBOX` |

Start the mock first: `smf-mock` on port 9000.

## Features

- Discover-filtered menu (types + cross-analyses with satisfied dependencies)
- Time range, optional system filter (`of_system`), configurable row limit
- Curated columns / KPI / charts for SMF 30-4, 70-1, 71-1, 72-3, 74-1, 77-1
- Cross-analyses with time-aligned hourly joins (not ML)
- CSV / JSON / PDF export from the table toolbar

## Smoke test

```powershell
.\.venv\Scripts\python scripts\prod_smoke_test.py --url http://127.0.0.1:9000/zosmf/zosdg/smf --dataset TEST.SMF.DATASET --username u --password p --no-verify-ssl
```
