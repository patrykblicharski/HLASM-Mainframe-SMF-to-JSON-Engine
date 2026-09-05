"""Builds smfexplorer requests and converts result DataFrames for the web UI."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import pandas as pd

from app_core.session import (
    Session,
    dataframe_to_records,
    get_or_create_context,
    known_field_names,
    resolve_fields,
)


def filter_known_fields(record_name: str, field_names: List[str]) -> List[str]:
    return known_field_names(record_name, field_names)


def run_query(
    session: Session,
    record_name: str,
    field_names: List[str],
    *,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    system_name: Optional[str] = None,
    limit: Optional[int] = None,
) -> pd.DataFrame:
    """Runs a query for fields `field_names` of record `record_name` in the context
    of the dataset assigned to the session. Returns a raw `pandas.DataFrame`.
    """
    ctx = get_or_create_context(session, session.dataset_name)
    fields = resolve_fields(record_name, field_names)

    request = ctx.request(fields)
    if start_time is not None or end_time is not None:
        request = request.in_time(start_time, end_time)
    if system_name is None:
        system_name = session.system_name
    if limit is None:
        limit = session.query_limit
    if system_name:
        request = request.of_system(system_name)
    if limit is not None and limit > 0:
        request = request.limit(limit)

    return request.run()


def run_query_records(
    session: Session,
    record_name: str,
    field_names: List[str],
    **kwargs,
) -> list[dict]:
    """Like `run_query`, but returns `list[dict]` — format ready for AG Grid /
    ECharts / export.
    """
    df = run_query(session, record_name, field_names, **kwargs)
    return dataframe_to_records(df)


def get_available_records(session: Session) -> pd.DataFrame:
    """Returns a DataFrame (type, subtype, count) of records available in the dataset
    assigned to the session — for discovery of which types actually have data.
    """
    ctx = get_or_create_context(session, session.dataset_name)
    return ctx.get_available_records()


def refresh_available(session: Session) -> dict[tuple[int, int], int]:
    """Refreshes `session.available` from `get_available_records()`.

    Returns the updated `(type, subtype) -> count` mapping. Rows without
    valid type/subtype are skipped.
    """
    df = get_available_records(session)
    available: dict[tuple[int, int], int] = {}
    if df is not None and not df.empty:
        for row in df.to_dict(orient="records"):
            try:
                smf_type = int(row["type"])
                subtype = int(row["subtype"])
                count = int(row.get("count") or 0)
            except (KeyError, TypeError, ValueError):
                continue
            available[(smf_type, subtype)] = count
    session.available = available
    return available


def get_dataset_description(session: Session) -> dict:
    ctx = get_or_create_context(session, session.dataset_name)
    return ctx.get_dataset_description()
