"""Shared time-window params: relative days, custom dates, hour brush."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flask import g, has_request_context, request

from .helpers import scrub_text


def _esc(value: str) -> str:
    return scrub_text(value).replace("'", "\\'")


@dataclass
class WindowParams:
    days: int = 4
    date_from: str = ""
    date_to: str = ""
    hour_from: str = ""
    hour_to: str = ""

    @classmethod
    def from_request(cls, default_days: int = 4) -> "WindowParams":
        raw_days = request.args.get("days") or request.form.get("days") or default_days
        try:
            days = max(1, min(int(raw_days), 90))
        except (TypeError, ValueError):
            days = int(default_days)
        return cls(
            days=days,
            date_from=scrub_text(request.args.get("date_from", "")),
            date_to=scrub_text(request.args.get("date_to", "")),
            hour_from=scrub_text(request.args.get("hour_from", "")),
            hour_to=scrub_text(request.args.get("hour_to", "")),
        )

    def has_custom_dates(self) -> bool:
        return bool(self.date_from or self.date_to)

    def has_hour_brush(self) -> bool:
        return bool(self.hour_from or self.hour_to)

    def date_sql(self, column: str = "event_date") -> str:
        """SQL predicate for a Date/DateTime column (no leading AND)."""
        a = _esc(self.date_from)
        b = _esc(self.date_to)
        if a or b:
            parts: list[str] = []
            if a:
                parts.append(f"toDate({column}) >= toDate(parseDateTimeBestEffort('{a}'))")
            if b:
                parts.append(f"toDate({column}) <= toDate(parseDateTimeBestEffort('{b}'))")
            return " AND ".join(parts)
        days = max(1, min(int(self.days), 90))
        return f"toDate({column}) >= today() - {days}"

    def hour_sql(self, *, datetime_expr: str | None = None) -> str:
        """Optional hour-brush predicate (leading AND …)."""
        a = _esc(self.hour_from)
        b = _esc(self.hour_to)
        if not a and not b:
            return ""
        h = datetime_expr or (
            "toStartOfHour(parseDateTimeBestEffort("
            "concat(toString(event_date),' ',if(time='','00:00:00',time))))"
        )
        parts: list[str] = []
        if a:
            parts.append(f"{h} >= parseDateTimeBestEffort('{a}')")
        if b:
            parts.append(f"{h} < parseDateTimeBestEffort('{b}')")
        return (" AND " + " AND ".join(parts)) if parts else ""

    def event_sql(self, column: str = "event_date") -> str:
        """Full filter for SMF event tables."""
        return self.date_sql(column) + self.hour_sql()

    def hour_column_sql(self, column: str = "hour") -> str:
        """Filter for pre-aggregated hour columns (stats_*)."""
        return self.date_sql(column) + self.hour_sql(datetime_expr=column)

    def query_args(self) -> dict[str, Any]:
        """Args safe to pass into url_for / form hidden fields."""
        out: dict[str, Any] = {"days": self.days}
        if self.date_from:
            out["date_from"] = self.date_from
        if self.date_to:
            out["date_to"] = self.date_to
        if self.hour_from:
            out["hour_from"] = self.hour_from
        if self.hour_to:
            out["hour_to"] = self.hour_to
        return out

    def to_template(self) -> dict[str, Any]:
        def _local(s: str) -> str:
            t = scrub_text(s).replace(" ", "T")
            return t[:16] if t else ""

        return {
            "days": self.days,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "date_from_local": _local(self.date_from),
            "date_to_local": _local(self.date_to),
            "hour_from": self.hour_from,
            "hour_to": self.hour_to,
            "window_args": self.query_args(),
        }


def bind_window(default_days: int = 4) -> WindowParams:
    win = WindowParams.from_request(default_days)
    if has_request_context():
        g.smf_window = win
    return win


def active_window(fallback_days: int = 4) -> WindowParams:
    if has_request_context() and getattr(g, "smf_window", None) is not None:
        return g.smf_window  # type: ignore[return-value]
    return WindowParams(days=fallback_days)


def event_window(days: int = 4) -> str:
    """Back-compat helper used by queries._days."""
    return active_window(days).event_sql()


def ts_expr() -> str:
    return (
        "parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))"
    )


def last_ts_select(alias: str = "last_ts") -> str:
    return f"max({ts_expr()}) AS {alias}"
