#!/usr/bin/env python3
"""Generate clickhouse/init.sql from schema_fields.txt or live smf2json maps.

Usage (from repo root):
  python infra/scripts/gen_init_sql.py
  python infra/scripts/gen_init_sql.py --from-maps   # requires PYTHONPATH=python
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DUMP = ROOT / "infra" / "clickhouse" / "schema_fields.txt"
OUT = ROOT / "infra" / "clickhouse" / "init.sql"

HEADER = """\
-- Auto-generated SMF ClickHouse schema for smf2json maps.
-- Regenerate: python infra/scripts/gen_init_sql.py
-- All mapped columns are String (smf2json CSV values are always strings).
-- Retention: 10 days via TTL on event_date.

CREATE DATABASE IF NOT EXISTS smf;

"""

FOOTER = """
-- ---------------------------------------------------------------------------
-- Lightweight rollup tables for Grafana (filled by scripts/refresh_stats.sh)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS smf.stats_records_daily
(
    event_date Date,
    table_name LowCardinality(String),
    smf_system_id LowCardinality(String),
    row_count UInt64
)
ENGINE = SummingMergeTree(row_count)
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, table_name, smf_system_id)
TTL event_date + INTERVAL 10 DAY;

CREATE TABLE IF NOT EXISTS smf.stats_tcp_hourly
(
    hour DateTime,
    smf_system_id LowCardinality(String),
    tcp_stack LowCardinality(String),
    conn_count UInt64,
    in_bytes UInt64,
    out_bytes UInt64
)
ENGINE = SummingMergeTree((conn_count, in_bytes, out_bytes))
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, smf_system_id, tcp_stack)
TTL toDate(hour) + INTERVAL 10 DAY;

CREATE TABLE IF NOT EXISTS smf.stats_dataset_daily
(
    event_date Date,
    smf_system_id LowCardinality(String),
    direction LowCardinality(String),
    job_name LowCardinality(String),
    dsname String,
    row_count UInt64,
    excp_sum UInt64
)
ENGINE = SummingMergeTree((row_count, excp_sum))
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, smf_system_id, direction, job_name, dsname)
TTL event_date + INTERVAL 10 DAY;

CREATE TABLE IF NOT EXISTS smf.stats_racf_daily
(
    event_date Date,
    smf_system_id LowCardinality(String),
    event_code String,
    user_id LowCardinality(String),
    job_name LowCardinality(String),
    row_count UInt64
)
ENGINE = SummingMergeTree(row_count)
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, smf_system_id, event_code, user_id, job_name)
TTL event_date + INTERVAL 10 DAY;

CREATE TABLE IF NOT EXISTS smf.stats_ftp_daily
(
    event_date Date,
    smf_system_id LowCardinality(String),
    direction LowCardinality(String),
    local_user LowCardinality(String),
    bytes_sum UInt64,
    xfer_count UInt64
)
ENGINE = SummingMergeTree((bytes_sum, xfer_count))
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, smf_system_id, direction, local_user)
TTL event_date + INTERVAL 10 DAY;

CREATE TABLE IF NOT EXISTS smf.stats_jobs_daily
(
    event_date Date,
    smf_system_id LowCardinality(String),
    smf_subtype String,
    job_name LowCardinality(String),
    row_count UInt64
)
ENGINE = SummingMergeTree(row_count)
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, smf_system_id, smf_subtype, job_name)
TTL event_date + INTERVAL 10 DAY;
"""

TABLE_RE = re.compile(r"^--- (smf_\S+) \((\d+) fields\) ---$")


def ch_type(ftype: str, key: str) -> str:
    """Map SMF converter ftype → ClickHouse column type (String-safe for CSV)."""
    # Keep everything String for reliable CSVWithNames loads (empty cells = "").
    # LowCardinality helps repeated SIDs / job names.
    lc_keys = {
        "smf_system_id",
        "smf_subsystem_id",
        "job_name",
        "ddname",
        "sys_name",
        "sysplex_name",
        "tcp_stack",
        "user_id",
        "racf_user",
        "step_name",
        "program_name",
        "smf_record_type",
        "smf_subtype",
    }
    if key in lc_keys:
        return "LowCardinality(String)"
    return "String"


def table_sql(name: str, cols: list[tuple[str, str]]) -> str:
    body: list[str] = []
    for key, ftype in cols:
        body.append(f"    `{key}` {ch_type(ftype, key)}")
    body.append("    ingested_at DateTime DEFAULT now()")
    if any(k == "date" for k, _ in cols):
        body.append(
            "    event_date Date MATERIALIZED "
            "toDateOrZero(parseDateTimeBestEffortOrZero(`date`))"
        )
    else:
        body.append("    event_date Date MATERIALIZED toDate(ingested_at)")

    order = ["event_date"]
    if any(k == "smf_system_id" for k, _ in cols):
        order.append("smf_system_id")
    if any(k == "job_name" for k, _ in cols):
        order.append("job_name")
    elif any(k == "time" for k, _ in cols):
        order.append("`time`")

    return "\n".join(
        [
            f"CREATE TABLE IF NOT EXISTS smf.{name}",
            "(",
            ",\n".join(body),
            ")",
            "ENGINE = MergeTree",
            "PARTITION BY event_date",
            f"ORDER BY ({', '.join(order)})",
            "TTL event_date + INTERVAL 10 DAY",
            "SETTINGS index_granularity = 8192;",
            "",
        ]
    )


def parse_dump(path: Path) -> list[tuple[str, list[tuple[str, str]]]]:
    tables: list[tuple[str, list[tuple[str, str]]]] = []
    current: str | None = None
    cols: list[tuple[str, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip("\n")
        m = TABLE_RE.match(line)
        if m:
            if current is not None:
                tables.append((current, cols))
            current = m.group(1)
            cols = []
            continue
        if current is None or not line or line.startswith("==="):
            continue
        if "\t" not in line:
            continue
        key, ftype = line.split("\t", 1)
        cols.append((key.strip(), ftype.strip()))
    if current is not None:
        tables.append((current, cols))
    return tables


def from_maps() -> list[tuple[str, list[tuple[str, str]]]]:
    sys.path.insert(0, str(ROOT / "python"))
    from smf2json.maps import MAPS_BY_SUBTYPE, MAPS_BY_TYPE  # type: ignore

    tables: list[tuple[str, list[tuple[str, str]]]] = []
    for rty, fields in sorted(MAPS_BY_TYPE.items()):
        tables.append(
            (f"smf_{rty}", [(f.json_key, f.ftype) for f in fields])
        )
    for (rty, sty), fields in sorted(MAPS_BY_SUBTYPE.items()):
        tables.append(
            (f"smf_{rty}_{sty}", [(f.json_key, f.ftype) for f in fields])
        )
    return tables


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-maps", action="store_true")
    args = ap.parse_args()

    if args.from_maps:
        tables = from_maps()
    else:
        if not SCHEMA_DUMP.is_file():
            print(f"Missing {SCHEMA_DUMP}; use --from-maps", file=sys.stderr)
            return 1
        tables = parse_dump(SCHEMA_DUMP)

    parts = [HEADER]
    parts.append(f"-- Tables: {len(tables)}\n")
    for name, cols in tables:
        parts.append(f"-- {name} ({len(cols)} columns)")
        parts.append(table_sql(name, cols))
    parts.append(FOOTER)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(parts), encoding="utf-8", newline="\n")
    print(f"Wrote {OUT} ({len(tables)} tables)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
