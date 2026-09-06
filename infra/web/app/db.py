"""ClickHouse HTTP client helpers."""

from __future__ import annotations

import csv
import io
from typing import Any, Iterable, Optional
from urllib.parse import quote

import requests
from flask import current_app


class ClickHouseError(RuntimeError):
    pass


def _auth() -> tuple[str, str]:
    return (
        current_app.config["CLICKHOUSE_USER"],
        current_app.config["CLICKHOUSE_PASSWORD"],
    )


def query(
    sql: str,
    *,
    params: Optional[dict[str, Any]] = None,
    columns: bool = True,
) -> list[dict[str, Any]]:
    """Run SQL and return list of dict rows (JSONEachRow)."""
    url = current_app.config["CLICKHOUSE_URL"].rstrip("/") + "/"
    database = current_app.config["CLICKHOUSE_DATABASE"]
    timeout = current_app.config["QUERY_TIMEOUT"]
    fmt = "JSONEachRow" if columns else "TabSeparated"
    body = sql.strip().rstrip(";") + f" FORMAT {fmt}"
    if params:
        for key, value in params.items():
            body = body.replace("{" + key + ":String}", _quote_str(value))
            body = body.replace("{" + key + ":UInt32}", str(int(value)))
            body = body.replace("{" + key + ":Int32}", str(int(value)))
    try:
        resp = requests.post(
            url,
            params={"database": database},
            data=body.encode("utf-8"),
            auth=_auth(),
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise ClickHouseError(f"ClickHouse unreachable: {exc}") from exc
    if resp.status_code != 200:
        raise ClickHouseError(f"HTTP {resp.status_code}: {resp.text[:800]}")
    rows: list[dict[str, Any]] = []
    for line in resp.text.splitlines():
        line = line.strip()
        if not line:
            continue
        import json

        rows.append(json.loads(line))
    return rows


def query_scalar(sql: str, **kwargs: Any) -> Any:
    rows = query(sql, **kwargs)
    if not rows:
        return None
    return next(iter(rows[0].values()))


def _quote_str(value: Any) -> str:
    s = str(value).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{s}'"


def csv_export(rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in fieldnames})
    return buf.getvalue()


def safe_ident(name: str) -> str:
    if not name or not all(c.isalnum() or c == "_" for c in name):
        raise ValueError(f"unsafe identifier: {name!r}")
    return name


def date_filter(days: int, column: str = "event_date") -> str:
    days = max(1, min(int(days), 90))
    # Compare as Date so DateTime midnight dumps and CH Date columns align.
    return f"toDate({column}) >= today() - {days}"
