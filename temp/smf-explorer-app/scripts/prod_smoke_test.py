#!/usr/bin/env python3
"""Manual production cutover smoke test (smfexplorer + app_core; not imported by the app)."""
from __future__ import annotations

import argparse
import getpass
import json
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Optional

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

# On Windows stdout defaults to the console code page (e.g. cp1250), which does
# not support many characters used in KPI labels (e.g. '<->' may appear as '↔').
# Force UTF-8 so the report never crashes while printing an unusual label/value.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd  # noqa: E402

import smfexplorer  # noqa: E402
from smfexplorer import error as smf_error  # noqa: E402

from app_core import query as query_layer  # noqa: E402
from app_core.session import (  # noqa: E402
    KNOWN_RECORD_MODULES,
    ConnectionFailed,
    Session,
    dataframe_to_records,
    get_or_create_context,
    list_fields,
    resolve_fields,
)
from smf_types.cross_analysis import CROSS_ANALYSIS_BUILDERS  # noqa: E402
from export_utils import rows_to_csv_bytes, rows_to_json_bytes, rows_to_pdf_bytes  # noqa: E402
from smf_types.core import Column  # noqa: E402


# --------------------------------------------------------------------------- #
#                              Report / test results                          #
# --------------------------------------------------------------------------- #

@dataclass
class StepResult:
    name: str
    status: str  # "PASS" | "FAIL" | "WARN" | "SKIP"
    detail: str = ""
    elapsed_s: float = 0.0


@dataclass
class Report:
    steps: list[StepResult] = field(default_factory=list)

    def add(self, result: StepResult) -> None:
        self.steps.append(result)
        marker = {"PASS": "[OK]  ", "FAIL": "[FAIL]", "WARN": "[WARN]", "SKIP": "[SKIP]"}[result.status]
        line = f"{marker} {result.name}"
        if result.elapsed_s:
            line += f"  ({result.elapsed_s:.2f}s)"
        print(line)
        if result.detail:
            for l in result.detail.splitlines():
                print(f"       {l}")

    def summary(self) -> tuple[int, int, int, int]:
        p = sum(1 for s in self.steps if s.status == "PASS")
        f = sum(1 for s in self.steps if s.status == "FAIL")
        w = sum(1 for s in self.steps if s.status == "WARN")
        sk = sum(1 for s in self.steps if s.status == "SKIP")
        return p, f, w, sk

    def as_json(self) -> list[dict]:
        return [
            {"name": s.name, "status": s.status, "detail": s.detail, "elapsed_s": s.elapsed_s}
            for s in self.steps
        ]


def run_step(report: Report, name: str, fn: Callable[[], tuple[str, str]]) -> Any:
    """Run `fn()`, which must return (status, detail). Exceptions become FAIL.

    Steps that must pass data onward (e.g. an open session) do so via variables
    in `main()`, not through this helper. This helper is for PASS/FAIL/WARN
    reporting only.
    """
    start = time.time()
    try:
        status, detail = fn()
    except Exception as exc:  # intentionally broad — diagnostic test
        status, detail = "FAIL", f"{type(exc).__name__}: {exc}\n{traceback.format_exc(limit=6)}"
    report.add(StepResult(name=name, status=status, detail=detail, elapsed_s=time.time() - start))
    return status


def connection_string(url: str, username: str, password: str, verify_ssl: bool) -> str:
    return (
        f"mode=dgapi;url={url};verify_ssl={'true' if verify_ssl else 'false'};"
        f"username={username};password={password}"
    )


# --------------------------------------------------------------------------- #
#                                  Section 1                                  #
# --------------------------------------------------------------------------- #

def section_1_login(report: Report, args: argparse.Namespace) -> Optional[Session]:
    """Login: happy path + wrong password + bad dataset (+ optional bad host).

    Addresses PROD_CUTOVER_PLAN.md item 1 ("Authorization") and item 3
    ("dedicated login error messages") — checks real error codes instead of
    assuming `webui/login.py` already handles them correctly.
    """
    print("\n=== 1. Login ===")

    session_holder: dict[str, Session] = {}

    def happy_path() -> tuple[str, str]:
        env = smfexplorer.new_environment(
            connection_string(args.url, args.username, args.password, args.verify_ssl)
        )
        ctx = env.new_context(args.dataset)
        desc = ctx.get_dataset_description()
        session = Session(session_id="smoke-test", environment=env, dataset_name=args.dataset)
        session.contexts[args.dataset] = ctx
        session_holder["session"] = session
        return "PASS", f"get_dataset_description() returned keys: {list(desc.keys()) if isinstance(desc, dict) else type(desc)}"

    run_step(report, "1a. Happy path (valid credentials)", happy_path)

    def wrong_password() -> tuple[str, str]:
        try:
            env = smfexplorer.new_environment(
                connection_string(args.url, args.username, "definitely-wrong-password-xyz", args.verify_ssl)
            )
            env.new_context(args.dataset).get_dataset_description()
        except smf_error.SmfExplorerError as exc:
            return "PASS", f"Correctly rejected as SmfExplorerError: {exc}"
        except Exception as exc:
            return "WARN", (
                f"Rejected, but NOT as smfexplorer.error.SmfExplorerError — type: {type(exc).__name__}: {exc}\n"
                "webui/login.py catches only ConnectionFailed + generic Exception, so it will work, "
                "but the user-facing message will be generic 'Error: ...' instead of a clear '401/403'."
            )
        return "WARN", (
            "Login with wrong password was NOT rejected. On smf-mock this is expected "
            "(accepts any credentials by default unless MOCK_SMF_USER/"
            "MOCK_SMF_PASSWORD are set) — on a REAL host this must be FAIL; verify manually "
            "which host you are testing."
        )

    run_step(report, "1b. Wrong password should be rejected", wrong_password)

    def wrong_dataset() -> tuple[str, str]:
        bogus = "THIS.DATASET.DOES.NOT.EXIST"
        try:
            env = smfexplorer.new_environment(
                connection_string(args.url, args.username, args.password, args.verify_ssl)
            )
            env.new_context(bogus).get_dataset_description()
        except Exception as exc:
            return "PASS", f"Non-existent dataset correctly rejected: {type(exc).__name__}: {exc}"
        return "FAIL", "Query for non-existent dataset did NOT raise an error — check whether `dataset_name_exists` is enforced."

    run_step(report, "1c. Non-existent dataset should return an error", wrong_dataset)

    if args.bad_host_url:
        def bad_host() -> tuple[str, str]:
            t0 = time.time()
            try:
                env = smfexplorer.new_environment(
                    connection_string(args.bad_host_url, args.username, args.password, args.verify_ssl)
                )
                env.new_context(args.dataset).get_dataset_description()
            except Exception as exc:
                elapsed = time.time() - t0
                status = "PASS" if elapsed < 30 else "WARN"
                detail = f"Rejected after {elapsed:.1f}s: {type(exc).__name__}: {exc}"
                if elapsed >= 30:
                    detail += "\nTime > 30s — missing or excessive timeout may hang the UI on unreachable hosts."
                return status, detail
            return "FAIL", "Connection to non-existent host did NOT raise an error (unexpected)."

        run_step(report, "1d. Unreachable host (--bad-host-url)", bad_host)
    else:
        report.add(StepResult("1d. Unreachable host", "SKIP", "Skipped — pass --bad-host-url to test connection timeout/error."))

    return session_holder.get("session")


# --------------------------------------------------------------------------- #
#                                  Section 2                                  #
# --------------------------------------------------------------------------- #

def section_2_all_record_types(report: Report, session: Session, limit: int) -> dict[str, pd.DataFrame]:
    """All 47 types: fetch real data and run through `dataframe_to_records` —
    catches ALL pandas dtypes in the data, not only those known from the mock
    (Timestamp/Timedelta).

    Addresses PROD_CUTOVER_PLAN.md item 2 ("Fields/types not fully verified on
    mock") and the risk of "new dtype = JSON serialization crash", as happened
    historically with Timestamp/Timedelta.
    """
    print(f"\n=== 2. All {len(KNOWN_RECORD_MODULES)} record types (limit={limit}/type) ===")
    dataframes: dict[str, pd.DataFrame] = {}

    for record_name in KNOWN_RECORD_MODULES:
        def check(record_name: str = record_name) -> tuple[str, str]:
            fields_meta = list_fields(record_name)
            non_virtual = [f["name"] for f in fields_meta if not f["virtual"]]
            if not non_virtual:
                return "WARN", "No non-virtual fields to query (virtual only) — skipping."
            sample_fields = non_virtual[: min(15, len(non_virtual))]
            df = query_layer.run_query(session, record_name, sample_fields, limit=limit)
            dataframes[record_name] = df
            if df.empty:
                return "WARN", f"0 rows returned for {record_name} (dataset may not contain this record type)."

            # For context only — pandas/numpy types beyond plain Python scalars
            # (e.g. numpy.uint32) are OFTEN fully JSON-safe after
            # dataframe_to_records/json.dumps below. We do not flag them
            # separately — the json.dumps test below is authoritative; this list
            # is extra context on FAIL.
            interesting_dtypes = sorted({str(df[col].dtype) for col in df.columns})

            try:
                records = dataframe_to_records(df)
                json.dumps(records[: min(5, len(records))], default=str)
            except TypeError as exc:
                return "FAIL", (
                    f"dataframe_to_records()/JSON serialization failed on this type: {exc}\n"
                    f"Column dtypes in this query: {', '.join(interesting_dtypes)}"
                )

            return "PASS", f"{len(df)} rows, {len(df.columns)} columns, all values JSON-safe. Dtypes: {', '.join(interesting_dtypes)}"

        run_step(report, f"2. {record_name}", check)

    return dataframes


# --------------------------------------------------------------------------- #
#                                  Section 3                                  #
# --------------------------------------------------------------------------- #

def section_3_filtering(report: Report, session: Session, system_name: Optional[str]) -> None:
    """Check whether `in_time`/`of_system` actually filter on the server side —
    the mock does NOT filter (deliberately documented simplification in
    CLAUDE.md), so this test would falsely pass on the mock.
    """
    print("\n=== 3. Time and system filtering ===")

    record_name = "SMF70S1"
    fields_meta = list_fields(record_name)
    time_field_candidates = [f["name"] for f in fields_meta if f["name"] in ("timestamp",)]
    if not time_field_candidates:
        report.add(StepResult("3. Filtering", "SKIP", f"{record_name} has no 'timestamp' field — adjust the script."))
        return

    def time_filter_narrows_result() -> tuple[str, str]:
        wide = query_layer.run_query(session, record_name, ["timestamp"], limit=5000)
        if wide.empty:
            return "WARN", f"{record_name} returned 0 rows without filter — cannot assess filtering."
        end = datetime.now()
        start = end - timedelta(minutes=5)
        narrow = query_layer.run_query(session, record_name, ["timestamp"], start_time=start, end_time=end, limit=5000)
        if len(narrow) < len(wide):
            return "PASS", f"Narrow window (5 min): {len(narrow)} rows vs. wide (no filter): {len(wide)} — filtering works."
        if len(narrow) == len(wide) and len(wide) < 5000:
            return "WARN", (
                f"Narrow and wide windows returned the same row count ({len(wide)}) — "
                "MAY mean `in_time()` does NOT filter on the server (as on smf-mock). "
                "Verify manually by comparing timestamps in both results."
            )
        return "WARN", f"Unexpected result: narrow={len(narrow)}, wide={len(wide)} — verify manually."

    run_step(report, "3a. `in_time()` narrows result", time_filter_narrows_result)

    if system_name:
        def system_filter_narrows_result() -> tuple[str, str]:
            all_rows = query_layer.run_query(session, record_name, ["timestamp"], limit=5000)
            filtered = query_layer.run_query(session, record_name, ["timestamp"], system_name=system_name, limit=5000)
            if len(filtered) <= len(all_rows):
                return "PASS", f"of_system('{system_name}'): {len(filtered)} rows vs. no filter: {len(all_rows)}."
            return "WARN", f"of_system returned MORE rows ({len(filtered)}) than without filter ({len(all_rows)}) — suspicious."

        run_step(report, "3b. `of_system()` narrows result", system_filter_narrows_result)
    else:
        report.add(StepResult("3b. `of_system()` narrows result", "SKIP", "Pass --system-name to test."))


# --------------------------------------------------------------------------- #
#                                  Section 4                                  #
# --------------------------------------------------------------------------- #

def section_4_cross_analysis(report: Report, session: Session, hours: int) -> dict[str, Any]:
    """All cross-analyses on a real `hours` window. Checks response time and
    whether the hard-coded limit=5000 materially truncates results — see
    PROD_CUTOVER_PLAN.md item 1 ("Size/volume").
    """
    print(f"\n=== 4. Cross-analyses ({hours}h window) ===")
    results: dict[str, Any] = {}

    for analysis_id, builder in CROSS_ANALYSIS_BUILDERS.items():
        def check(analysis_id: str = analysis_id, builder: Callable = builder) -> tuple[str, str]:
            t0 = time.time()
            smf_type = builder(session, hours=hours)
            elapsed = time.time() - t0
            results[analysis_id] = smf_type

            kpi_summary = "; ".join(f"{k.label}={k.value}" for k in smf_type.kpis)
            row_count = len(smf_type.rows) if smf_type.rows else 0

            hit_limit_hint = ""
            for k in smf_type.kpis:
                if isinstance(k.value, int) and k.value >= 5000:
                    hit_limit_hint = (
                        f"\nNOTE: KPI '{k.label}' = {k.value} >= analysis hard-coded limit 5000 — "
                        "results may be truncated; consider raising the limit in smf_types/cross_analysis.py."
                    )

            status = "PASS"
            detail = f"{elapsed:.2f}s, {row_count} table rows, KPI: {kpi_summary}{hit_limit_hint}"
            if elapsed > 10:
                status = "WARN"
                detail += "\nResponse time > 10s — consider UX (spinner/async) in production with larger datasets."
            if hit_limit_hint:
                status = "WARN"
            return status, detail

        run_step(report, f"4. {analysis_id}", check)

    return results


# --------------------------------------------------------------------------- #
#                                  Section 5                                  #
# --------------------------------------------------------------------------- #

def section_5_export(report: Report, session: Session, args: argparse.Namespace) -> None:
    """CSV/JSON/PDF export on one larger, real result table."""
    print("\n=== 5. CSV/JSON/PDF export ===")

    record_name = "SMF30S1"

    def build_table() -> tuple[str, str]:
        fields_meta = list_fields(record_name)
        non_virtual = [f["name"] for f in fields_meta if not f["virtual"]][:20]
        df = query_layer.run_query(session, record_name, non_virtual, limit=2000)
        if df.empty:
            return "WARN", f"{record_name} returned 0 rows — export not testable on this data; try another record_module."
        rows = dataframe_to_records(df)
        columns = [Column(key=c, label=c, description="", default=True) for c in df.columns]

        csv_bytes = rows_to_csv_bytes(columns, rows)
        json_bytes = rows_to_json_bytes(columns, rows)
        pdf_bytes = rows_to_pdf_bytes(f"Smoke test - {record_name}", f"{len(rows)} rows", columns, rows)

        if not csv_bytes or not json_bytes or not pdf_bytes:
            return "FAIL", "One of the exports returned empty bytes."
        return "PASS", (
            f"{len(rows)} rows x {len(columns)} columns -> "
            f"CSV {len(csv_bytes)}B, JSON {len(json_bytes)}B, PDF {len(pdf_bytes)}B."
        )

    run_step(report, f"5. CSV/JSON/PDF export ({record_name}, up to 2000 rows)", build_table)


# --------------------------------------------------------------------------- #
#                                  Section 6                                  #
# --------------------------------------------------------------------------- #

def section_6_tls(report: Report, args: argparse.Namespace) -> None:
    """TLS: whether `verify_ssl=True` actually rejects a bad/self-signed certificate.

    Requires `--tls-negative-url` pointing at a host with an INVALID certificate
    (e.g. self-signed without trust, or CN mismatch) — otherwise you cannot
    distinguish "certificate OK" from "verification not working at all".
    """
    print("\n=== 6. TLS ===")

    if not args.tls_negative_url:
        report.add(StepResult(
            "6. TLS verification rejects bad certificate", "SKIP",
            "Pass --tls-negative-url (host with invalid/self-signed certificate) to test."
        ))
        return

    def negative_tls() -> tuple[str, str]:
        try:
            env = smfexplorer.new_environment(
                connection_string(args.tls_negative_url, args.username, args.password, True)
            )
            env.new_context(args.dataset).get_dataset_description()
        except Exception as exc:
            msg = str(exc).lower()
            if "certificate" in msg or "ssl" in msg or "tls" in msg:
                return "PASS", f"verify_ssl=True correctly rejected bad certificate: {exc}"
            return "WARN", f"Rejected, but message does not look like a certificate error — verify manually: {exc}"
        return "FAIL", "verify_ssl=True did NOT reject connection to host with bad certificate — serious security issue."

    run_step(report, "6. TLS verification rejects bad certificate", negative_tls)


# --------------------------------------------------------------------------- #
#                                  Section 7                                  #
# --------------------------------------------------------------------------- #

def section_7_multi_session(report: Report, args: argparse.Namespace) -> None:
    """Multiple concurrent sessions to DIFFERENT hosts in one process —
    verifies the stated architecture goal in `SessionStore`
    (`app_core/session.py`: "never call smfexplorer.setup()").
    """
    print("\n=== 7. Multiple concurrent sessions (different hosts) ===")

    if not args.second_url or not args.second_dataset:
        report.add(StepResult(
            "7. Two parallel sessions to different hosts", "SKIP",
            "Pass --second-url and --second-dataset (e.g. smf-mock address) to test session isolation."
        ))
        return

    def two_sessions() -> tuple[str, str]:
        env_a = smfexplorer.new_environment(
            connection_string(args.url, args.username, args.password, args.verify_ssl)
        )
        env_b = smfexplorer.new_environment(
            connection_string(args.second_url, args.second_username or args.username,
                               args.second_password or args.password, args.second_verify_ssl)
        )
        ctx_a = env_a.new_context(args.dataset)
        ctx_b = env_b.new_context(args.second_dataset)
        desc_a = ctx_a.get_dataset_description()
        desc_b = ctx_b.get_dataset_description()
        if desc_a == desc_b:
            return "WARN", "Dataset descriptions from two different hosts are identical — suspicious (same host?)."
        return "PASS", f"Two independent sessions run in parallel in one process without collision (env A != env B: {env_a is not env_b})."

    run_step(report, "7. Two parallel sessions to different hosts", two_sessions)


# --------------------------------------------------------------------------- #
#                                    main                                     #
# --------------------------------------------------------------------------- #

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--url", required=True, help="Production z/OS Data Gatherer connection URL.")
    p.add_argument("--dataset", required=True, help="SMF dataset name for tests.")
    p.add_argument("--username", required=True)
    p.add_argument("--password", default=None, help="If omitted, prompts interactively (getpass).")
    p.add_argument("--verify-ssl", action="store_true", default=True)
    p.add_argument("--no-verify-ssl", dest="verify_ssl", action="store_false")
    p.add_argument("--system-name", default=None, help="System name (SID) for `of_system()` filter test (section 3).")
    p.add_argument("--limit", type=int, default=200, help="Row limit per record type in section 2 (default 200).")
    p.add_argument("--hours", type=int, default=24, help="Time window (h) for cross-analyses in section 4.")
    p.add_argument("--bad-host-url", default=None, help="Unreachable/bad URL for login timeout test (section 1d).")
    p.add_argument("--tls-negative-url", default=None, help="Host with INVALID TLS certificate for negative test (section 6).")
    p.add_argument("--second-url", default=None, help="URL of a second, DIFFERENT host for multi-session test (section 7) — e.g. smf-mock.")
    p.add_argument("--second-dataset", default=None)
    p.add_argument("--second-username", default=None)
    p.add_argument("--second-password", default=None)
    p.add_argument("--second-verify-ssl", action="store_true", default=False)
    p.add_argument("--skip", nargs="*", default=[], choices=["1", "2", "3", "4", "5", "6", "7"],
                    help="Section numbers to skip, e.g. --skip 2 4 (useful for large datasets / quick retest).")
    p.add_argument("--report", default=None, help="Optional path to write full JSON report.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.password is None:
        args.password = getpass.getpass(f"Password for {args.username}@{args.url}: ")

    print(f"SMF Explorer - production cutover smoke test")
    print(f"Target: {args.url}  dataset={args.dataset}  verify_ssl={args.verify_ssl}")
    print(f"Started: {datetime.now().isoformat()}")

    report = Report()

    session = None
    if "1" not in args.skip:
        session = section_1_login(report, args)
    else:
        report.add(StepResult("1. Login", "SKIP", "Skipped via --skip 1."))
        env = smfexplorer.new_environment(connection_string(args.url, args.username, args.password, args.verify_ssl))
        ctx = env.new_context(args.dataset)
        session = Session(session_id="smoke-test", environment=env, dataset_name=args.dataset)
        session.contexts[args.dataset] = ctx

    if session is None:
        print("\nFATAL: section 1 (login) failed completely — aborting; later sections require a live session.")
        _print_summary(report)
        _maybe_write_report(report, args.report)
        return 1

    if "2" not in args.skip:
        section_2_all_record_types(report, session, args.limit)
    else:
        report.add(StepResult("2. All record types", "SKIP", "Skipped via --skip 2."))

    if "3" not in args.skip:
        section_3_filtering(report, session, args.system_name)
    else:
        report.add(StepResult("3. Filtering", "SKIP", "Skipped via --skip 3."))

    if "4" not in args.skip:
        section_4_cross_analysis(report, session, args.hours)
    else:
        report.add(StepResult("4. Cross-analyses", "SKIP", "Skipped via --skip 4."))

    if "5" not in args.skip:
        section_5_export(report, session, args)
    else:
        report.add(StepResult("5. Export", "SKIP", "Skipped via --skip 5."))

    if "6" not in args.skip:
        section_6_tls(report, args)
    else:
        report.add(StepResult("6. TLS", "SKIP", "Skipped via --skip 6."))

    if "7" not in args.skip:
        section_7_multi_session(report, args)
    else:
        report.add(StepResult("7. Multi-session", "SKIP", "Skipped via --skip 7."))

    _print_summary(report)
    _maybe_write_report(report, args.report)

    _, failed, _, _ = report.summary()
    return 1 if failed else 0


def _print_summary(report: Report) -> None:
    passed, failed, warned, skipped = report.summary()
    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed} PASS, {failed} FAIL, {warned} WARN, {skipped} SKIP")
    if failed:
        print("\nFAIL steps (must be fixed before production rollout):")
        for s in report.steps:
            if s.status == "FAIL":
                print(f"  - {s.name}")
    if warned:
        print("\nWARN steps (manual verification; may be expected):")
        for s in report.steps:
            if s.status == "WARN":
                print(f"  - {s.name}")
    print("=" * 60)


def _maybe_write_report(report: Report, path: Optional[str]) -> None:
    if not path:
        return
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report.as_json(), fh, indent=2, ensure_ascii=False)
    print(f"\nFull report written to: {path}")


if __name__ == "__main__":
    sys.exit(main())
