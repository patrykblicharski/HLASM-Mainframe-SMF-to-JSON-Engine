# Cutover plan from `smf-mock` to real z/OS Data Gatherer

This file is a checklist of items to change, implement, or test when
`smf-explorer-app` (and optionally `smf_webapp`) stop connecting to
`smf-mock` (`http://127.0.0.1:9000/...`) and start connecting to a real
z/OS Data Gatherer host. Nothing below is done yet — this is a plan for
later, written on 2026-07-12 based on what is already known about
mock vs. production differences from work on the project so far.

## 1. Mock vs. production differences to verify/handle

Per "Known simplifications" in `CLAUDE.md` — `smf-mock` is
schema-accurate (field names/structure 1:1 with the real OpenAPI spec), but
**values** are intentionally simplified. Specific differences that stop being
harmless in production:

- **Time and field filtering.** The mock ignores `startTime`/`endTime` and
  always returns all fields in a section — it always returns data regardless of
  the requested window. Verify whether the real endpoint actually filters
  on `in_time(start, end)` as assumed by `app_core/query.py::run_query`, and
  whether responses from large time windows (e.g. `hours=24` in cross-analyses)
  return dramatically larger data volumes than the mock (the 5000-record
  limit in `smf_types/cross_analysis.py` may be too low/too high —
  test real response sizes and query times).
- **`systemName`.** The mock only cosmetically injects a value into
  `*SID` fields; it does not filter. Confirm that `of_system(system_name)`
  actually filters on the production API side (no UI path has tested real
  per-system filtering yet).
- **Real business correlations.** The mock generates mostly random data,
  without meaningful dependencies between fields (except recently fixed:
  `BIN_STR` flag bits and realistic `interval` vs. `cpu_wait_time`/
  `cpu_parked_time` for SMF70). Cross-analyses (`x-cpu-batch`,
  `x-wlm-bottleneck`, `x-paging-pressure`, `x-enqueue-contention`,
  `x-job-risk`, `x-cpu-forecast`) were designed and tested on mock
  data — **their thresholds/heuristics (e.g. 90th percentile CPU in `x-job-risk`,
  "swappingActive" threshold in `x-paging-pressure`) must be recalibrated on
  real production value distributions**, because current ones may be tuned to
  mock data scale/distribution.
- **Authorization.** The mock accepts any credentials by default (unless
  `MOCK_SMF_USER`/`MOCK_SMF_PASSWORD` are set). Test the full 401/403 error
  path with a real host — whether `webui/login.py::do_login`
  catches and clearly communicates bad credentials (currently
  it only catches `ConnectionFailed` and a generic `Exception`; there is no
  dedicated handling for 401 vs. 403 vs. timeout).
- **TLS.** The mock has no HTTPS (`verify_ssl` in the connection string is set to
  `false` at login). In production the z/OS host almost certainly requires HTTPS with
  a valid certificate (or self-signed, requiring explicit trust).
  Required:
  - change the default `verify_ssl` checkbox in `webui/login.py` to
    `True` for production deployment (or at least warn in the UI when
    the user disables verification),
  - verify whether `smfexplorer`/`dgapi` supports a custom CA bundle
    (corporate self-signed z/OS certs) and whether a field is needed to
    specify a CA path.
- **429/500 error codes.** The mock simulates them only on demand
  (`?_mock_status=...`). Test real behavior under production Gatherer
  load/limits — whether `app_core/session.py`
  and `query.py` have sensible retry/backoff (currently none — every error
  propagates straight to the UI as an exception).
- **Dataset size/volume.** Mock datasets (`TEST.SMF.DATASET`,
  `DEV.SMF.SANDBOX`) have small, fixed record counts.
  Real SMF datasets can be orders of magnitude larger — test performance of
  `ctx.request(...).limit(n).run()` and AG Grid/ECharts rendering
  at real volumes (pagination? `limit` is currently hard-coded to
  5000 in cross-analyses, likely too small/too large depending on
  time range).

## 2. Fields/types not fully verified on the mock

- **`SMF99S2` / `ai_data0`** — existing, unfixed bug: the mock generates
  a random string for this field, while `smfexplorer`'s `core.hex2int`
  post-processor expects hex values (`ValueError: invalid literal for
  int() with base 16`). Because the mock generates that string randomly, catalog
  `99-2` **currently always crashes** regardless of data. On production,
  real data should be valid hex — **but this must actually be
  tested against the real API**, because it may reveal
  missing error handling in `smf_types/catalog.py`/`webui/` when
  a field has an unexpected format.
- **Other fields with `x-zml-datatype: BIN_STR`** (455 occurrences in the spec; see
  `smf-mock/mock_server/generator.py::_random_bit_string`) — only partially fixed
  (for `SMF70CNF`/`cpu_is_online`). Worth reviewing whether other flags decoded by `core.flags`/`core.multiflags`
  in other record types (e.g. SMF74, SMF79) have sensible UI counterparts
  (columns/KPI) worth verifying on real data — so far only SMF70 was verified.
- **`PACKED_TIME_2/3/4` and `SIGNED` fields with `format: time`** — only partially
  unified (`_random_time_str` now distinguishes only `TOD` vs.
  everything else). We have not checked whether other variants (`PACKED_TIME_2`,
  `PACKED_TIME_4`, `SIGNED`) in real data have sensible ranges aligned
  with what the generator assumes — that affects only the mock, but at
  cutover remove any assumption of "synthetic realism"
  and rely only on real values.

## 3. Configuration changes for production deployment

- `app_core/config.py::Settings.storage_secret` — currently
  `"dev-only-change-me"`. **Must** be overridden with environment variable
  `SMFAPP_STORAGE_SECRET` in production (otherwise signing
  `app.storage.user` in NiceGUI is trivial to forge).
- `session_ttl_seconds` (4h) — reconsider against real corporate
  security/session policy (may be too long/too short).
- Production Gatherer URL/dataset are not hard-coded anywhere (good —
  entered by the user on `/login`), but consider:
  - an allowlist of permitted hosts (currently any URL entered by the
    user goes straight to `smfexplorer.new_environment`, which
    may be OK for privileged operators, but confirm with
    the user whether that is intentional),
  - password retention policy — currently `connection_string` (with password in
    plain text) is held in process memory in `Session.environment`
    (live object, not serializable) — verify that logs/tracebacks do not
    expose the connection string with password (e.g. in
    `ConnectionFailed` messages, which are the stringified exception).
- HTTPS/reverse proxy in front of `smf-explorer-app` itself (NiceGUI dev
  server) — `CLAUDE.md` already flags this as an open item for `smf_webapp`;
  it applies to `smf-explorer-app` as well.

## 4. Tests to run on first real connection

1. Login with real credentials — happy path + wrong password +
   unreachable host (timeout) + no permission to the dataset.
2. For each of the 47 types in `KNOWN_RECORD_MODULES` (`app_core/session.py`):
   run a query for all fields and verify that `dataframe_to_records`
   serializes the result correctly (no new pandas dtypes not seen on the mock
   — e.g. `category`, `Int64` with real NaN patterns).
3. All 6 cross-analyses on a real, large time window (24h, then
   try a longer window) — check response times, 5000-record
   limit, chart/KPI sanity (thresholds from section 1 may need
   recalibration).
4. CSV/JSON/PDF export on real, large result tables — check
   performance and character encoding correctness.
5. Multiple concurrent users connecting to **different**
   z/OS hosts at once (declared goal of `SessionStore` architecture) — not
   tested yet even on the mock with more than one session
   at a time.
6. Session TTL (4h) and behavior after expiry — whether the UI clearly redirects
   to login without losing unsaved view settings.

## 5. Non-blocking but worth considering before production

- Retry/backoff for 429/5xx from the real API (see section 1).
- Dedicated login error messages (401 vs. 403 vs. connection
  refused vs. TLS handshake failure) instead of generic
  `f"Error: {exc}"` in `webui/login.py`.
- Rate limiting / protection against accidentally oversized queries
  (`limit` with no upper cap from user input — currently only
  cross-analyses have a hard 5000 limit; ordinary catalog queries have no
  visible cap in `webui/`).
