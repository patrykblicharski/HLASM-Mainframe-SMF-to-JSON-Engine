"""Display helpers — encoding-safe labels, empty states, DSN scrubbing."""

from __future__ import annotations

import re
from typing import Any, Optional

from markupsafe import Markup, escape


_CTRL = re.compile(r"[\x00-\x1f\x7f-\x9f\ufffd]")
_DSN_OK = re.compile(r"^[A-Z0-9.@$#+\-][A-Z0-9.@$#+\- ]{0,43}$", re.I)


def scrub_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    text = _CTRL.sub("", text).strip()
    # Collapse leftover question-mark-only garbage from older loads
    if text and set(text) <= {"?"}:
        return ""
    if text.count("?") >= 8 and text.count("?") >= len(text) * 0.5:
        return ""
    return text


def display_dsname(dsname: Any, *, volser: Any = "", fallback: str = "(no dataset name)") -> str:
    name = scrub_text(dsname)
    if name and _DSN_OK.match(name):
        return name
    if name and all(32 <= ord(c) <= 126 for c in name):
        return name
    vol = scrub_text(volser)
    if vol:
        return f"{fallback} · vol {vol}"
    return fallback


def display_cell(value: Any, empty: str = "—") -> Markup:
    text = scrub_text(value)
    if text:
        return Markup(escape(text))
    return Markup(f'<span class="cell-empty">{escape(empty)}</span>')


def intish(value: Any) -> int:
    try:
        return int(str(value).strip() or "0")
    except ValueError:
        return 0


def fmt_bytes(n: Any) -> str:
    v = float(intish(n))
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(v) < 1024 or unit == "TB":
            return f"{v:,.0f} {unit}" if unit == "B" else f"{v:,.1f} {unit}"
        v /= 1024.0
    return f"{v:.1f} TB"


def fmt_int(n: Any) -> str:
    return f"{intish(n):,}"


def fmt_cpu_timer(n: Any) -> str:
    """Format SMF cpu_step_time sum as raw timer units (not wall seconds)."""
    return f"{intish(n):,} timer"


NAV = [
    {"endpoint": "overview", "label": "Overview", "icon": "grid"},
    {"endpoint": "datasets", "label": "Datasets", "icon": "disk"},
    {"endpoint": "lifecycle", "label": "Lifecycle", "icon": "cycle"},
    {"endpoint": "jobs", "label": "Jobs", "icon": "cpu"},
    {"endpoint": "racf", "label": "RACF", "icon": "shield"},
    {"endpoint": "tcp", "label": "TCP", "icon": "net"},
    {"endpoint": "ftp", "label": "FTP", "icon": "transfer"},
    {"endpoint": "cross", "label": "Cross", "icon": "link"},
]
