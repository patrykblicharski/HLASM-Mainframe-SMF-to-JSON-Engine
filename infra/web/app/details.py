"""Fetch full ClickHouse rows for the Details modal."""

from __future__ import annotations

from typing import Any

from . import db
from .helpers import scrub_text


ALLOWED_TABLES = frozenset(
    {
        "smf_14",
        "smf_15",
        "smf_17",
        "smf_30_1",
        "smf_30_2",
        "smf_30_3",
        "smf_30_4",
        "smf_30_5",
        "smf_30_6",
        "smf_42_5",
        "smf_42_6",
        "smf_61",
        "smf_65",
        "smf_66",
        "smf_80",
        "smf_89",
        "smf_92_1",
        "smf_92_2",
        "smf_92_10",
        "smf_92_11",
        "smf_92_14",
        "smf_92_16",
        "smf_119_1",
        "smf_119_2",
        "smf_119_3",
        "smf_119_5",
        "smf_119_6",
        "smf_119_10",
        "smf_119_70",
        "smf_119_72",
    }
)

ALLOWED_FILTERS = frozenset(
    {
        "job_name",
        "dsname",
        "volser",
        "volser_1",
        "volume_serial",
        "smf_system_id",
        "user_id",
        "racf_user",
        "event_code",
        "class_name",
        "old_resource",
        "program_name",
        "step_name",
        "job_class",
        "entry_name",
        "catalog_name",
        "remote_ip",
        "local_ip",
        "local_port",
        "remote_port",
        "resource_name",
        "as_name",
        "term_code",
        "connection_id",
        "ddname",
        "local_user",
        "tcp_stack",
        "event_date",
        "time",
        "date",
    }
)


def _quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _table_filters(table: str, filters: dict[str, str]) -> tuple[str, dict[str, str]]:
    """Build AND … predicates; map UI volser to the physical column for each table."""
    parts: list[str] = []
    applied: dict[str, str] = {}
    for key, raw in filters.items():
        if key not in ALLOWED_FILTERS:
            continue
        val = scrub_text(raw)
        if val == "":
            continue
        col = key
        if key == "volser":
            if table in ("smf_14", "smf_15"):
                col = "volser_1"
            elif table == "smf_17":
                col = "volume_serial"
            else:
                continue
        parts.append(f"{col} = {_quote(val)}")
        applied[col] = val
    sql = (" AND " + " AND ".join(parts)) if parts else ""
    return sql, applied


def fetch_full_details(
    tables: list[str],
    filters: dict[str, str],
    days: int,
    *,
    limit: int = 8,
) -> dict[str, Any]:
    """Return SELECT * sample rows per allowed table matching filters."""
    clean_tables: list[str] = []
    for t in tables:
        name = scrub_text(t).removeprefix("smf.")
        if name in ALLOWED_TABLES and name not in clean_tables:
            clean_tables.append(name)
    if not clean_tables:
        raise ValueError("no allowed tables")

    lim = max(1, min(int(limit), 25))
    day_sql = db.date_filter(days)
    sources: list[dict[str, Any]] = []
    applied_all: dict[str, str] = {}

    for table in clean_tables:
        filt_sql, applied = _table_filters(table, filters)
        applied_all.update(applied)
        try:
            matched = int(
                db.query_scalar(f"SELECT count() FROM smf.{table} WHERE {day_sql}{filt_sql}") or 0
            )
            rows = db.query(
                f"""
                SELECT *
                FROM smf.{table}
                WHERE {day_sql}{filt_sql}
                ORDER BY event_date DESC, time DESC
                LIMIT {lim}
                """
            )
            sources.append({"table": table, "matched": matched, "rows": rows, "error": None})
        except db.ClickHouseError as exc:
            sources.append({"table": table, "matched": 0, "rows": [], "error": str(exc)})

    return {
        "days": days,
        "filters": applied_all,
        "limit": lim,
        "sources": sources,
    }
