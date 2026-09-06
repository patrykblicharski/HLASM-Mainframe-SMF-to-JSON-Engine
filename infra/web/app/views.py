"""Flask views — full SMF analytics UI."""

from __future__ import annotations

import json
from typing import Any

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from markupsafe import Markup

from . import db, details, queries
from .helpers import NAV, display_cell, display_dsname, fmt_bytes, fmt_cpu_timer, fmt_int, scrub_text

bp = Blueprint("smf", __name__)


def _days() -> int:
    raw = request.args.get("days") or request.form.get("days") or current_app.config["DEFAULT_DAYS"]
    try:
        return max(1, min(int(raw), 90))
    except ValueError:
        return int(current_app.config["DEFAULT_DAYS"])


def _ctx(**extra: Any) -> dict[str, Any]:
    days = _days()
    ctx = {
        "nav": NAV,
        "days": days,
        "fmt_int": fmt_int,
        "fmt_bytes": fmt_bytes,
        "fmt_cpu_timer": fmt_cpu_timer,
        "display_cell": display_cell,
        "display_dsname": display_dsname,
        "scrub_text": scrub_text,
        "q": scrub_text(request.args.get("q", "")),
        "error": None,
    }
    ctx.update(extra)
    return ctx


def _safe(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs), None
    except db.ClickHouseError as exc:
        return None, str(exc)


@bp.app_template_filter("tojson_chart")
def tojson_chart(value: Any) -> Markup:
    """Serialize for inline <script> — must be Markup or Jinja escapes quotes to &#34;."""
    return Markup(json.dumps(value, default=str, ensure_ascii=False))


@bp.route("/")
def overview():
    days = _days()
    kpis, err = _safe(queries.overview_kpis, days)
    tables, _ = _safe(queries.records_by_table, days)
    hourly, _ = _safe(queries.hourly_activity, days)
    return render_template(
        "overview.html",
        **_ctx(
            active="overview",
            title="Overview",
            kpis=kpis or {},
            tables=tables or [],
            hourly=hourly or [],
            error=err,
        ),
    )


@bp.route("/datasets")
def datasets():
    days = _days()
    q = scrub_text(request.args.get("q", ""))
    top, err = _safe(queries.top_datasets, days, 80, q)
    scratch, _ = _safe(queries.scratch_top, days, 40)
    hourly, _ = _safe(queries.dataset_hourly, days)
    return render_template(
        "datasets.html",
        **_ctx(
            active="datasets",
            title="Datasets",
            top=top or [],
            scratch=scratch or [],
            hourly=hourly or [],
            error=err,
        ),
    )


@bp.route("/datasets/<path:dsname>")
def dataset_detail(dsname: str):
    days = _days()
    data, err = _safe(queries.dataset_detail, dsname, days)
    return render_template(
        "dataset_detail.html",
        **_ctx(
            active="datasets",
            title=f"Dataset · {scrub_text(dsname) or '(blank)'}",
            data=data or {"dsname": dsname, "io": [], "scratch": [], "catalog": [], "racf": []},
            error=err,
        ),
    )


@bp.route("/jobs")
def jobs():
    days = _days()
    q = scrub_text(request.args.get("q", ""))
    hour_from = scrub_text(request.args.get("hour_from", ""))
    hour_to = scrub_text(request.args.get("hour_to", ""))
    top, err = _safe(queries.jobs_top, days, 80, q, hour_from, hour_to)
    hourly, _ = _safe(queries.jobs_hourly, days)
    classes, _ = _safe(queries.job_class_mix, days, hour_from, hour_to)
    return render_template(
        "jobs.html",
        **_ctx(
            active="jobs",
            title="Jobs / SMF 30",
            top=top or [],
            hourly=hourly or [],
            classes=classes or [],
            hour_from=hour_from,
            hour_to=hour_to,
            error=err,
        ),
    )


@bp.route("/jobs/<path:job>")
def job_detail(job: str):
    days = _days()
    data, err = _safe(queries.job_detail, job, days)
    return render_template(
        "job_detail.html",
        **_ctx(
            active="jobs",
            title=f"Job · {scrub_text(job)}",
            data=data
            or {
                "job": job,
                "steps": [],
                "ends": [],
                "starts": [],
                "datasets": [],
                "racf": [],
                "tcp": [],
            },
            error=err,
        ),
    )


@bp.route("/racf")
def racf():
    days = _days()
    q = scrub_text(request.args.get("q", ""))
    summary, err = _safe(queries.racf_summary, days)
    events, _ = _safe(queries.racf_events, days, q, 120)
    return render_template(
        "racf.html",
        **_ctx(
            active="racf",
            title="RACF / SMF 80",
            summary=summary or {"codes": [], "users": [], "classes": [], "hourly": []},
            events=events or [],
            error=err,
        ),
    )


@bp.route("/users/<path:user>")
def user_detail(user: str):
    days = _days()
    data, err = _safe(queries.user_detail, user, days)
    return render_template(
        "user_detail.html",
        **_ctx(
            active="racf",
            title=f"User · {scrub_text(user)}",
            data=data or {"user": user, "events": [], "jobs": []},
            error=err,
        ),
    )


@bp.route("/tcp")
def tcp():
    days = _days()
    summary, err = _safe(queries.tcp_summary, days)
    return render_template(
        "tcp.html",
        **_ctx(
            active="tcp",
            title="TCP / SMF 119",
            summary=summary or {"hourly": [], "remotes": [], "terms": [], "ports": [], "stacks": []},
            error=err,
        ),
    )


@bp.route("/tcp/ip/<path:ip>")
def ip_detail(ip: str):
    days = _days()
    data, err = _safe(queries.ip_detail, ip, days)
    return render_template(
        "ip_detail.html",
        **_ctx(
            active="tcp",
            title=f"IP · {scrub_text(ip)}",
            data=data or {"ip": ip, "sessions": [], "inits": []},
            error=err,
        ),
    )


@bp.route("/ftp")
def ftp():
    days = _days()
    summary, err = _safe(queries.ftp_summary, days)
    return render_template(
        "ftp.html",
        **_ctx(
            active="ftp",
            title="FTP / SMF 119-3/70",
            summary=summary or {"client": 0, "server": 0, "fail72": 0, "subtypes": [], "users": []},
            error=err,
        ),
    )


@bp.route("/lifecycle")
def lifecycle():
    days = _days()
    summary, err = _safe(queries.lifecycle_summary, days)
    return render_template(
        "lifecycle.html",
        **_ctx(
            active="lifecycle",
            title="Dataset Lifecycle",
            summary=summary or {"hourly": [], "tops": [], "catalogs": []},
            error=err,
        ),
    )


@bp.route("/cross")
def cross():
    days = _days()
    summary, err = _safe(queries.cross_summary, days)
    return render_template(
        "cross.html",
        **_ctx(
            active="cross",
            title="Cross Analysis",
            summary=summary or {"job_security": [], "net_work": []},
            error=err,
        ),
    )


@bp.route("/api/details")
def api_details():
    """JSON: full SMF column dump for modal Details buttons."""
    days = _days()
    raw_tables = request.args.get("tables") or request.args.get("table") or ""
    tables = [t.strip() for t in raw_tables.split(",") if t.strip()]
    try:
        limit = int(request.args.get("limit") or 8)
    except ValueError:
        limit = 8
    filters = {k: v for k, v in request.args.items() if k not in {"tables", "table", "days", "limit"}}
    try:
        payload = details.fetch_full_details(tables, filters, days, limit=limit)
    except ValueError as exc:
        return Response(
            json.dumps({"error": str(exc)}),
            status=400,
            mimetype="application/json",
        )
    except db.ClickHouseError as exc:
        return Response(
            json.dumps({"error": str(exc)}),
            status=502,
            mimetype="application/json",
        )
    return Response(
        json.dumps(payload, default=str, ensure_ascii=False),
        mimetype="application/json",
    )


@bp.route("/export/<kind>.csv")
def export_csv(kind: str):
    days = _days()
    q = scrub_text(request.args.get("q", ""))
    rows: list[dict[str, Any]] = []
    fields: list[str] = []
    if kind == "datasets":
        rows = queries.top_datasets(days, 500, q)
        fields = ["direction", "job_name", "dsname", "volser", "rows", "excp", "dsname_display"]
    elif kind == "jobs":
        rows = queries.jobs_top(days, 500, q)
        fields = ["job_name", "smf_system_id", "ends", "programs", "steps", "cpu_sum"]
    elif kind == "racf":
        rows = queries.racf_events(days, q, 1000)
        fields = [
            "event_date",
            "time",
            "user_id",
            "job_name",
            "event_code",
            "class_name",
            "old_resource",
            "access_requested",
            "access_allowed",
        ]
    else:
        return redirect(url_for("smf.overview", days=days))
    body = db.csv_export(rows, fields)
    return Response(
        body,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=smf_{kind}_{days}d.csv"},
    )


@bp.route("/health")
def health():
    try:
        n = db.query_scalar("SELECT 1")
        return {"ok": True, "clickhouse": n == 1}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}, 503
