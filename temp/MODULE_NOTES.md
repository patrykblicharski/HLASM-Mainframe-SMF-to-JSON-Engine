# Module notes (for agents & developers)

Longer design context that used to live in file-header docstrings.
**Code files keep one-line module docstrings only.** Prefer this file when you need “why”, not “what”.

Project language: English (code, comments, docs). Chat with the owner may be Polish.

---

## `smf-explorer-app/`

### `main.py`
NiceGUI entry. No global Gatherer state — each browser session logs in and gets its own `Environment`. Windows: `start.bat`. Default URL: `http://localhost:8080`.

### `app_core/session.py`
**Only module that imports `smfexplorer`.** Never call `smfexplorer.setup()` (process-global). Use `new_environment(connection_string)` per session. Session id lives in `app.storage.user` (needs `storage_secret` in `ui.run`). Pattern mirrors `smf_webapp` cookie sessions.

### `app_core/config.py`
Host/credentials are **not** in settings — they come from the login form into the session so one deploy can hit mock + prod for different users.

### `app_core/query.py`
Builds `FieldRequest`, runs it, returns `list[dict]` for tables/charts. Pages must not import `smfexplorer` directly.

### `app_core/console_quit.py`
Background thread: console **Q** → `app.shutdown()`. Needs `ui.run(reload=False)`.

### `smf_types/catalog.py`
Generated first pass (`scripts/generate_catalog.py` + `fields_dump.json`). Titles from IBM docs; columns from field introspection; KPIs/charts start generic (`default_kpis`). Manual overrides: `curation.py`. Cross-analyses are **not** here — see `cross_analysis.py`.

### `smf_types/cross_analysis.py`
NOT-ML heuristics (aggregations, Pearson, linear extrapolation). Each analysis queries via `app_core/query`. Align series by **time** (hourly resample + join), not row index. Requires matching types in `session.available`.

### `smf_types/curation.py`
Hand-tuned column/KPI/chart overrides on top of the generated catalog.

### `smf_types/dictionaries.py`
Category labels + `CATEGORY_ORDER` for the sidebar.

### `webui/login.py`
Login form + `require_session` guard. Sets Gatherer connection into session storage.

### `webui/layout.py`
Header/sidebar/time-range. Menu filtered by `session.available` (discover). No RNG “live” mode — refresh = new query. Hours/dark mode in URL query params.

### `webui/pages.py`
Dashboard + per-type views. Session-guarded. Discover-driven menu; curated columns/KPIs for priority types.

### `webui/data_table.py` / `chart.py` / `kpi.py` / `theme.py` / `export_utils.py`
AG Grid table (search/sort/filter/columns/export), ECharts, KPI cards, day/night CSS, CSV/JSON/PDF export. PDF uses ASCII transliteration of Polish diacritics (`_PL_MAP`) because Helvetica is WinAnsi-only.

### `start.bat` + `start_tools.py`
Universal Windows launcher: pin Python, create/repair/reinstall `.venv`, optional minimal-runtime ZIP vs python.org download, splash, colored console. Config block at top of `.bat`. `start_en.bat` is an alias. Helpers: `find-python`, `check-venv`, `fix-venv`, `build-runtime`.

### Scripts (not imported by the app)
| Script | Role |
|--------|------|
| `generate_catalog.py` | Build `catalog.py` from `fields_dump.json` |
| `introspect_fields.py` | Dump `smfexplorer.fields.SMF*` → JSON |
| `fix_venv_paths.py` | Legacy path fixer (launcher prefers `start_tools.py fix-venv`) |
| `prod_smoke_test.py` | Manual cutover smoke against real Gatherer — see `PROD_CUTOVER_PLAN.md` §4 |

---

## `smf-mock/`

FastAPI stand-in for z/OS Data Gatherer SMF REST. Serves real IBM `openapi_spec.json` at `/v3/api-docs`; generates schema-accurate fake records for all 47 type/subtype pairs. Does **not** filter by time/system/selectors; `systemName` is cosmetic. Error injection: `?_mock_status=`. Record count: `?count=N`.

---

## `smf_webapp/`

Earlier FastAPI + vanilla JS client. Same multi-session idea (`new_environment` per cookie). Minimal UI (table only). Main product UI is `smf-explorer-app/`.

---

## Related docs
- `CLAUDE.md` — repo map, run commands, architecture summary
- `PROD_CUTOVER_PLAN.md` — mock → real z/OS checklist
- Component READMEs under each package folder
