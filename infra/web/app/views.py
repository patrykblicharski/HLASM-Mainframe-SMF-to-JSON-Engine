"""Flask views — full SMF analytics UI."""

from __future__ import annotations

import json
from typing import Any, Optional

from flask import (
    Blueprint,
    Response,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)
from markupsafe import Markup

from . import db, details, queries
from .field_meta import field_description, field_meta_json
from .helpers import (
    NAV,
    display_cell,
    display_dsname,
    fmt_bytes,
    fmt_cpu_timer,
    fmt_int,
    fmt_ts,
    scrub_text,
)
from .window import bind_window

bp = Blueprint("smf", __name__)


def _days() -> int:
    return bind_window(current_app.config["DEFAULT_DAYS"]).days


def _limit(name: str, default: int) -> int:
    raw = request.args.get(f"limit_{name}")
    try:
        n = int(raw) if raw is not None else default
    except ValueError:
        n = default
    # Match Full table Load-more sizes (50 … 100000).
    return max(10, min(n, 100_000))


def _slice(rows: Optional[list], limit: int) -> tuple[list, bool]:
    rows = list(rows or [])
    return rows[:limit], len(rows) > limit


def _ctx(**extra: Any) -> dict[str, Any]:
    win = bind_window(current_app.config["DEFAULT_DAYS"])
    q = scrub_text(request.args.get("q", ""))
    ctx = {
        "nav": NAV,
        "fmt_int": fmt_int,
        "fmt_bytes": fmt_bytes,
        "fmt_cpu_timer": fmt_cpu_timer,
        "fmt_ts": fmt_ts,
        "display_cell": display_cell,
        "display_dsname": display_dsname,
        "scrub_text": scrub_text,
        "field_tip": field_description,
        "field_meta": field_meta_json(),
        "q": q,
        "error": None,
        "show_search": False,
        "export_kind": None,
        **win.to_template(),
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


@bp.app_template_global()
def field_tip(name: Any, default: str = "") -> str:
    return field_description(name, default)

@bp.app_template_global()
def more_url(name: str, limit: int, step: int = 50) -> str:
    """Build current-page URL with a bumped limit_* for Load more."""
    args = request.args.to_dict(flat=True)
    args[f"limit_{name}"] = str(int(limit) + int(step))
    return url_for(request.endpoint, **{**(request.view_args or {}), **args})


@bp.app_template_global()
def clear_hour_url() -> str:
    args = request.args.to_dict(flat=True)
    args.pop("hour_from", None)
    args.pop("hour_to", None)
    return url_for(request.endpoint, **{**(request.view_args or {}), **args})


@bp.route("/")
def overview():
    days = _days()
    kpis, err = _safe(queries.overview_kpis, days)
    tables, _ = _safe(queries.records_by_table, days)
    hourly, _ = _safe(queries.hourly_activity, days)
    last_update, _ = _safe(queries.latest_smf_update)
    return render_template(
        "overview.html",
        **_ctx(
            active="overview",
            title="Overview",
            kpis=kpis or {},
            tables=tables or [],
            hourly=hourly or [],
            last_data_update=last_update,
            error=err,
        ),
    )


@bp.route("/datasets")
def datasets():
    days = _days()
    q = scrub_text(request.args.get("q", ""))
    lim_ds = _limit("datasets", 80)
    lim_sc = _limit("scratch", 40)
    top_raw, err = _safe(queries.top_datasets, days, lim_ds + 1, q)
    scratch_raw, _ = _safe(queries.scratch_top, days, lim_sc + 1)
    top, has_more_datasets = _slice(top_raw, lim_ds)
    scratch, has_more_scratch = _slice(scratch_raw, lim_sc)
    hourly, _ = _safe(queries.dataset_hourly, days)
    return render_template(
        "datasets.html",
        **_ctx(
            active="datasets",
            title="Datasets",
            top=top,
            scratch=scratch,
            hourly=hourly or [],
            limit_datasets=lim_ds,
            limit_scratch=lim_sc,
            has_more_datasets=has_more_datasets,
            has_more_scratch=has_more_scratch,
            show_search=True,
            export_kind="datasets",
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
    lim = _limit("jobs", 80)
    top_raw, err = _safe(queries.jobs_top, days, lim + 1, q)
    top, has_more_jobs = _slice(top_raw, lim)
    hourly, _ = _safe(queries.jobs_hourly, days)
    classes, _ = _safe(queries.job_class_mix, days)
    return render_template(
        "jobs.html",
        **_ctx(
            active="jobs",
            title="Jobs / SMF 30",
            top=top,
            hourly=hourly or [],
            classes=classes or [],
            limit_jobs=lim,
            has_more_jobs=has_more_jobs,
            show_search=True,
            export_kind="jobs",
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
    lim_users = _limit("users", 40)
    lim_classes = _limit("classes", 20)
    lim_events = _limit("events", 120)
    summary, err = _safe(
        queries.racf_summary,
        days,
        users_limit=lim_users + 1,
        classes_limit=lim_classes + 1,
    )
    summary = summary or {"codes": [], "users": [], "classes": [], "hourly": []}
    users, has_more_users = _slice(summary.get("users"), lim_users)
    classes, has_more_classes = _slice(summary.get("classes"), lim_classes)
    summary["users"] = users
    summary["classes"] = classes
    events_raw, _ = _safe(queries.racf_events, days, q, lim_events + 1)
    events, has_more_events = _slice(events_raw, lim_events)
    return render_template(
        "racf.html",
        **_ctx(
            active="racf",
            title="RACF / SMF 80",
            summary=summary,
            events=events,
            limit_users=lim_users,
            limit_classes=lim_classes,
            limit_events=lim_events,
            has_more_users=has_more_users,
            has_more_classes=has_more_classes,
            has_more_events=has_more_events,
            show_search=True,
            export_kind="racf",
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
    lim_remotes = _limit("remotes", 40)
    lim_ports = _limit("ports", 30)
    lim_stacks = _limit("stacks", 20)
    summary, err = _safe(
        queries.tcp_summary,
        days,
        remotes_limit=lim_remotes + 1,
        ports_limit=lim_ports + 1,
        stacks_limit=lim_stacks + 1,
    )
    summary = summary or {"hourly": [], "remotes": [], "terms": [], "ports": [], "stacks": []}
    remotes, has_more_remotes = _slice(summary.get("remotes"), lim_remotes)
    ports, has_more_ports = _slice(summary.get("ports"), lim_ports)
    stacks, has_more_stacks = _slice(summary.get("stacks"), lim_stacks)
    summary["remotes"] = remotes
    summary["ports"] = ports
    summary["stacks"] = stacks
    return render_template(
        "tcp.html",
        **_ctx(
            active="tcp",
            title="TCP / SMF 119",
            summary=summary,
            limit_remotes=lim_remotes,
            limit_ports=lim_ports,
            limit_stacks=lim_stacks,
            has_more_remotes=has_more_remotes,
            has_more_ports=has_more_ports,
            has_more_stacks=has_more_stacks,
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
    lim_tops = _limit("tops", 50)
    lim_catalogs = _limit("catalogs", 20)
    summary, err = _safe(
        queries.lifecycle_summary,
        days,
        tops_limit=lim_tops + 1,
        catalogs_limit=lim_catalogs + 1,
    )
    summary = summary or {"hourly": [], "tops": [], "catalogs": []}
    tops, has_more_tops = _slice(summary.get("tops"), lim_tops)
    catalogs, has_more_catalogs = _slice(summary.get("catalogs"), lim_catalogs)
    summary["tops"] = tops
    summary["catalogs"] = catalogs
    return render_template(
        "lifecycle.html",
        **_ctx(
            active="lifecycle",
            title="Dataset Lifecycle",
            summary=summary,
            limit_tops=lim_tops,
            limit_catalogs=lim_catalogs,
            has_more_tops=has_more_tops,
            has_more_catalogs=has_more_catalogs,
            error=err,
        ),
    )


@bp.route("/cross")
def cross():
    days = _days()
    lim_job = _limit("jobsec", 40)
    lim_net = _limit("network", 40)
    summary, err = _safe(
        queries.cross_summary,
        days,
        job_limit=lim_job + 1,
        net_limit=lim_net + 1,
    )
    summary = summary or {"job_security": [], "net_work": []}
    job_security, has_more_jobsec = _slice(summary.get("job_security"), lim_job)
    net_work, has_more_network = _slice(summary.get("net_work"), lim_net)
    summary["job_security"] = job_security
    summary["net_work"] = net_work
    return render_template(
        "cross.html",
        **_ctx(
            active="cross",
            title="Cross Analysis",
            summary=summary,
            limit_jobsec=lim_job,
            limit_network=lim_net,
            has_more_jobsec=has_more_jobsec,
            has_more_network=has_more_network,
            error=err,
        ),
    )


def _api_table_payload(*, default_limit: int, max_limit: int = 200) -> Response:
    """Shared JSON handler for Details / Full table modals."""
    days = _days()
    raw_tables = request.args.get("tables") or request.args.get("table") or ""
    tables = [t.strip() for t in raw_tables.split(",") if t.strip()]
    try:
        limit = int(request.args.get("limit") or default_limit)
    except ValueError:
        limit = default_limit
    try:
        offset = int(request.args.get("offset") or 0)
    except ValueError:
        offset = 0
    filters = {
        k: v
        for k, v in request.args.items()
        if k
        not in {
            "tables",
            "table",
            "days",
            "limit",
            "offset",
            "date_from",
            "date_to",
            "hour_from",
            "hour_to",
        }
    }
    try:
        payload = details.fetch_full_details(
            tables, filters, days, limit=limit, offset=offset, max_limit=max_limit
        )
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


@bp.route("/api/details")
def api_details():
    """JSON: full SMF column dump for modal Details buttons."""
    return _api_table_payload(default_limit=100, max_limit=200)


@bp.route("/api/full-table")
def api_full_table():
    """JSON: paginated SELECT * for Full table panel modal (all columns)."""
    return _api_table_payload(default_limit=50, max_limit=100_000)


@bp.route("/export/<kind>.csv")
def export_csv(kind: str):
    days = _days()
    q = scrub_text(request.args.get("q", ""))
    rows: list[dict[str, Any]] = []
    fields: list[str] = []
    if kind == "datasets":
        rows = queries.top_datasets(days, 500, q)
        fields = ["last_ts", "direction", "job_name", "dsname", "volser", "rows", "excp", "dsname_display"]
    elif kind == "jobs":
        rows = queries.jobs_top(days, 500, q)
        fields = ["last_ts", "job_name", "smf_system_id", "ends", "programs", "steps", "cpu_sum"]
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
