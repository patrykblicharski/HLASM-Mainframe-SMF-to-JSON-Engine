# Mock z/OS Data Gatherer (sandbox server)

A local, fully functional stand-in for *z/OS Data Gatherer: SMF Data REST
Services*, so you can develop `smf_webapp` without access to a real z/OS host.

**This is not a hard-coded stub** — the server loads the real
`openapi_spec.json` file you provide (your `api-docs__1_.json`) and:
- serves it byte-for-byte at `/v3/api-docs` (exactly where `smfexplorer`
  actually fetches it on every connection to verify the right server and build
  its internal field map),
- generates fake records **recursively from real schemas** — for
  EVERY one of the 47 SMF type/subtype pairs described in the spec (not just a subset), with
  correct data types, nested sections (`$ref`), repeating sections
  (indexed maps), and array fields — in exactly the format the `smfexplorer` parser expects.

## Verified (tested directly with your `smfexplorer` wheel)

- `GET /v3/api-docs` → title `"z/OS Data Gatherer: SMF Data REST Services"`
  (`Environment.check()` passes)
- `ctx.get_available_records()` → 47 type/subtype rows with record counts
- `ctx.get_dataset_description()` → correct `count`, `system_ids`
- `ctx.request([...]).limit(n).run()` → a real `pandas.DataFrame` with
  correct dtypes (tested integer fields from `SMF74S4`)
- Unknown dataset discovery → 404 (like the real server)
- Error simulation (`?_mock_status=429` etc.) → any HTTP status on demand

### Known pitfall (not in the mock, in the test environment)
During tests in this environment (Python 3.12 + forced newer `pandas`,
because `smfexplorer` officially supports only Python 3.9–3.11 with `pandas<2.0`)
I hit `AttributeError: 'StringDtype' object has no attribute
'itemsize'` on text fields — an error inside **`smfexplorer`**
with an unsupported pandas version, not a mock-server bug (numeric fields
passed fine with correct dtypes). On your environment with
Python 3.11 and standard `pandas<2.0` (as `smfexplorer` declares in its
dependencies) this should not occur — but it is one of the first things to verify if you see a similar error.

## Running

```powershell
python -m venv .venv-mock
.venv-mock\Scripts\activate
pip install -r requirements-mock.txt
uvicorn mock_server.main:app --port 9000 --reload
```

The server starts at `http://127.0.0.1:9000`. `GET /` shows status and
a list of known datasets/types.

## Connecting `smf_webapp` to the sandbox

In the connection form in `smf_webapp` (or directly in test code)
use:

| Field | Value |
|---|---|
| Connection URL | `http://127.0.0.1:9000/zosmf/zosdg/smf` |
| Username | any, e.g. `demo` |
| Password | any, e.g. `demo` |
| Verify TLS | **off** (mock has no HTTPS) |
| Dataset name | `TEST.SMF.DATASET` or `DEV.SMF.SANDBOX` |

Both datasets have generated record counts for all 47
SMF type/subtype pairs, so the discovery view in `smf_webapp` shows a full,
realistic list to choose from.

## Controlling mock behavior

- **Number of generated records per request**: default 15; override with
  `?count=N` on the request URL (dev-only extension,
  not present on the real API — `smf_webapp` does not send it, but you can
  append it manually when testing with curl/Swagger).
- **Forcing HTTP errors**: add `?_mock_status=401` (or 403/404/
  429/500) to ANY request to test how `smf_webapp`
  handles that error instead of a normal response.
- **Requiring specific credentials**: set environment variables
  `MOCK_SMF_USER`/`MOCK_SMF_PASSWORD` before starting the server to
  disable the default "accept any password" mode and test 401.
- **Adding more fake datasets**: edit `mock_server/datasets.py`.

## What the mock does NOT do (known simplifications)

- It does not filter results by `startTime`/`endTime` or by query-selector fields
  (`SMF74_SUBTYPE4=...` etc.) — it always returns ALL
  fields of a section. That is harmless: the `smfexplorer` parser only reads
  the fields you actually requested; it ignores the rest.
- `systemName` is only cosmetically injected into `*SID` fields in the
  generated record; it is not a real filter.
- Data is fully random — no meaningful business correlations
  (e.g. job duration vs. CPU usage), so it is not suitable for testing
  charts/analyses with realistic content, only integration tests
  (whether data flows correctly through the whole stack).
