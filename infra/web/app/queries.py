"""Shared query snippets against ClickHouse SMF schema."""

from __future__ import annotations

from typing import Any

from . import db
from .helpers import display_dsname, scrub_text
from .window import active_window, last_ts_select, ts_expr


def _days(days: int) -> str:
    """Date (+ optional custom range / hour brush) from the active request window."""
    return active_window(days).event_sql()


def _chart_days(days: int) -> str:
    """Date window only — charts ignore hour brush so bars stay clickable."""
    return active_window(days).date_sql()


def _hour_days(days: int) -> str:
    """Window filter for pre-aggregated `hour` columns (tables/KPIs)."""
    return active_window(days).hour_column_sql("hour")


def _chart_hour_days(days: int) -> str:
    return active_window(days).date_sql("hour")


def overview_kpis(days: int) -> dict[str, Any]:
    sql = f"""
    SELECT
      (SELECT count() FROM smf.smf_14 WHERE {_days(days)}) AS in14,
      (SELECT count() FROM smf.smf_15 WHERE {_days(days)}) AS out15,
      (SELECT count() FROM smf.smf_17 WHERE {_days(days)}) AS scratch17,
      (SELECT count() FROM smf.smf_30_5 WHERE {_days(days)}) AS jobs30,
      (SELECT count() FROM smf.smf_80 WHERE {_days(days)}) AS racf80,
      (SELECT count() FROM smf.smf_119_2 WHERE {_days(days)}) AS tcp119,
      (SELECT count() FROM smf.smf_119_3 WHERE {_days(days)}) AS ftp3,
      (SELECT count() FROM smf.smf_119_70 WHERE {_days(days)}) AS ftp70,
      (SELECT count() FROM smf.smf_61 WHERE {_days(days)}) AS def61,
      (SELECT count() FROM smf.smf_65 WHERE {_days(days)}) AS del65,
      (SELECT count() FROM smf.smf_66 WHERE {_days(days)}) AS alt66,
      (SELECT count() FROM smf.smf_92_11 WHERE {_days(days)}) AS uss_close,
      (SELECT count() FROM smf.smf_92_17 WHERE {_days(days)}) AS uss_access,
      (SELECT count() FROM smf.smf_92_10 WHERE {_days(days)}) AS uss_open
    """
    rows = db.query(sql)
    return rows[0] if rows else {}


def latest_smf_update() -> Any:
    """Newest event datetime across key loaded SMF tables (absolute, not windowed)."""
    tables = (
        "smf_14",
        "smf_15",
        "smf_17",
        "smf_30_4",
        "smf_30_5",
        "smf_61",
        "smf_65",
        "smf_66",
        "smf_80",
        "smf_92_10",
        "smf_92_11",
        "smf_92_14",
        "smf_92_17",
        "smf_119_1",
        "smf_119_2",
        "smf_119_3",
        "smf_119_70",
    )
    ts = ts_expr()
    unions = " UNION ALL ".join(f"SELECT max({ts}) AS ts FROM smf.{t}" for t in tables)
    return db.query_scalar(f"SELECT max(ts) FROM ({unions})")


def records_by_table(days: int) -> list[dict[str, Any]]:
    return db.query(
        f"""
        SELECT table_name, sum(row_count) AS rows
        FROM smf.stats_records_daily
        WHERE {_chart_days(days)}
        GROUP BY table_name
        ORDER BY rows DESC
        LIMIT 40
        """
    )


def hourly_activity(days: int) -> list[dict[str, Any]]:
    w = _chart_days(days)
    return db.query(
        f"""
        SELECT hour, source, sum(cnt) AS rows FROM (
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'INPUT-14' AS source, count() AS cnt
          FROM smf.smf_14 WHERE {w} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'OUTPUT-15' AS source, count() AS cnt
          FROM smf.smf_15 WHERE {w} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'RACF-80' AS source, count() AS cnt
          FROM smf.smf_80 WHERE {w} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'TCP-119-2' AS source, count() AS cnt
          FROM smf.smf_119_2 WHERE {w} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'JOB-30-5' AS source, count() AS cnt
          FROM smf.smf_30_5 WHERE {w} GROUP BY hour
        )
        GROUP BY hour, source
        ORDER BY hour
        """
    )


def top_datasets(days: int, limit: int = 50, q: str = "") -> list[dict[str, Any]]:
    filt = ""
    if q:
        qq = scrub_text(q).replace("'", "\\'")
        filt = f"AND (positionCaseInsensitive(dsname, '{qq}') > 0 OR positionCaseInsensitive(job_name, '{qq}') > 0 OR positionCaseInsensitive(volser, '{qq}') > 0)"
    rows = db.query(
        f"""
        SELECT direction, job_name, dsname, volser, sum(rows) AS rows, sum(excp) AS excp,
               max(last_ts) AS last_ts
        FROM (
          SELECT 'INPUT' AS direction, job_name,
                 if(trim(BOTH ' ' FROM dsname) = '' OR match(dsname, '^[\\\\x00-\\\\x1f\\\\x7f-\\\\x9f\\\\x{{fffd}}?]+$'), '', dsname) AS dsname,
                 volser_1 AS volser, count() AS rows, sum(toUInt64OrZero(excp_count)) AS excp,
                 {last_ts_select()}
          FROM smf.smf_14 WHERE {_days(days)} GROUP BY job_name, dsname, volser
          UNION ALL
          SELECT 'OUTPUT', job_name,
                 if(trim(BOTH ' ' FROM dsname) = '' OR match(dsname, '^[\\\\x00-\\\\x1f\\\\x7f-\\\\x9f\\\\x{{fffd}}?]+$'), '', dsname) AS dsname,
                 volser_1 AS volser, count(), sum(toUInt64OrZero(excp_count)),
                 {last_ts_select()}
          FROM smf.smf_15 WHERE {_days(days)} GROUP BY job_name, dsname, volser
        )
        WHERE 1=1 {filt}
        GROUP BY direction, job_name, dsname, volser
        ORDER BY rows DESC
        LIMIT {int(limit)}
        """
    )
    for r in rows:
        r["dsname_display"] = display_dsname(r.get("dsname"), volser=r.get("volser"))
    return rows


def scratch_top(days: int, limit: int = 40) -> list[dict[str, Any]]:
    rows = db.query(
        f"""
        SELECT job_name,
               if(trim(BOTH ' ' FROM dsname) = '', '', dsname) AS dsname,
               volume_serial AS volser, count() AS rows,
               {last_ts_select()}
        FROM smf.smf_17
        WHERE {_days(days)}
        GROUP BY job_name, dsname, volser
        ORDER BY rows DESC
        LIMIT {int(limit)}
        """
    )
    for r in rows:
        r["dsname_display"] = display_dsname(r.get("dsname"), volser=r.get("volser"))
    return rows


def dataset_hourly(days: int) -> list[dict[str, Any]]:
    w = _chart_days(days)
    return db.query(
        f"""
        SELECT hour, direction, sum(cnt) AS rows FROM (
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'INPUT' AS direction, count() AS cnt
          FROM smf.smf_14 WHERE {w} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'OUTPUT' AS direction, count() AS cnt
          FROM smf.smf_15 WHERE {w} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'SCRATCH' AS direction, count() AS cnt
          FROM smf.smf_17 WHERE {w} GROUP BY hour
        )
        GROUP BY hour, direction ORDER BY hour
        """
    )


def dataset_detail(dsname: str, days: int) -> dict[str, Any]:
    name = scrub_text(dsname).replace("'", "\\'")
    io14 = db.query(
        f"""
        SELECT event_date, time, job_name, ddname, volser_1 AS volser, excp_count, 'INPUT' AS direction
        FROM smf.smf_14
        WHERE {_days(days)} AND dsname = '{name}'
        ORDER BY event_date DESC, time DESC LIMIT 200
        """
    )
    io15 = db.query(
        f"""
        SELECT event_date, time, job_name, ddname, volser_1 AS volser, excp_count, 'OUTPUT' AS direction
        FROM smf.smf_15
        WHERE {_days(days)} AND dsname = '{name}'
        ORDER BY event_date DESC, time DESC LIMIT 200
        """
    )
    scratch = db.query(
        f"""
        SELECT event_date, time, job_name, volume_serial AS volser
        FROM smf.smf_17
        WHERE {_days(days)} AND dsname = '{name}'
        ORDER BY event_date DESC, time DESC LIMIT 100
        """
    )
    catalog = db.query(
        f"""
        SELECT 'DEFINE' AS action, event_date, time, job_name, entry_name, catalog_name FROM smf.smf_61
        WHERE {_days(days)} AND entry_name = '{name}'
        UNION ALL
        SELECT 'DELETE', event_date, time, job_name, entry_name, catalog_name FROM smf.smf_65
        WHERE {_days(days)} AND entry_name = '{name}'
        UNION ALL
        SELECT 'ALTER', event_date, time, job_name, entry_name, catalog_name FROM smf.smf_66
        WHERE {_days(days)} AND (entry_name = '{name}' OR new_entry_name = '{name}')
        ORDER BY event_date DESC, time DESC LIMIT 100
        """
    )
    racf = db.query(
        f"""
        SELECT event_date, time, user_id, job_name, event_code, class_name, old_resource, access_requested, access_allowed
        FROM smf.smf_80
        WHERE {_days(days)} AND (old_resource = '{name}' OR new_dataset_name = '{name}')
        ORDER BY event_date DESC, time DESC LIMIT 100
        """
    )
    return {
        "dsname": name,
        "io": io14 + io15,
        "scratch": scratch,
        "catalog": catalog,
        "racf": racf,
    }


def jobs_top(days: int, limit: int = 50, q: str = "") -> list[dict[str, Any]]:
    filt = ""
    if q:
        qq = scrub_text(q).replace("'", "\\'")
        filt = f"AND positionCaseInsensitive(job_name, '{qq}') > 0"
    return db.query(
        f"""
        SELECT e.job_name, e.smf_system_id, e.ends, e.last_ts,
               coalesce(p.programs, '') AS programs,
               coalesce(p.steps, '') AS steps,
               coalesce(p.cpu_sum, 0) AS cpu_sum
        FROM (
          SELECT job_name, smf_system_id, count() AS ends, {last_ts_select()}
          FROM smf.smf_30_5
          WHERE {_days(days)} AND job_name != '' {filt}
          GROUP BY job_name, smf_system_id
        ) e
        LEFT JOIN (
          SELECT job_name, smf_system_id,
                 arrayStringConcat(arrayFilter(x -> x != '', topK(3)(program_name)), ', ') AS programs,
                 arrayStringConcat(arrayFilter(x -> x != '', topK(3)(step_name)), ', ') AS steps,
                 sum(toUInt64OrZero(cpu_step_time)) AS cpu_sum
          FROM smf.smf_30_4
          WHERE {_days(days)} AND job_name != '' {filt}
          GROUP BY job_name, smf_system_id
        ) p USING (job_name, smf_system_id)
        ORDER BY e.ends DESC
        LIMIT {int(limit)}
        """
    )


def jobs_hourly(days: int) -> list[dict[str, Any]]:
    # Hourly chart stays on the full day window (ignore hour brush) so bars remain clickable.
    w = _chart_days(days)
    return db.query(
        f"""
        SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
               count() AS ends
        FROM smf.smf_30_5
        WHERE {w}
        GROUP BY hour ORDER BY hour
        """
    )


def job_class_mix(days: int) -> list[dict[str, Any]]:
    return db.query(
        f"""
        SELECT if(job_class = '', '(blank)', job_class) AS job_class, count() AS rows
        FROM smf.smf_30_4
        WHERE {_days(days)}
        GROUP BY job_class ORDER BY rows DESC LIMIT 20
        """
    )


def job_detail(job: str, days: int) -> dict[str, Any]:
    name = scrub_text(job).replace("'", "\\'")
    # Step/program live on 30-4 in this dump; 30-5 is job-end summary
    steps = db.query(
        f"""
        SELECT event_date, time, smf_system_id, step_name, program_name, job_class, racf_user,
               cpu_step_time, srb_time, step_comp_code
        FROM smf.smf_30_4
        WHERE {_days(days)} AND job_name = '{name}'
        ORDER BY event_date DESC, time DESC LIMIT 200
        """
    )
    ends = db.query(
        f"""
        SELECT event_date, time, smf_system_id, step_name, program_name, job_class, racf_user,
               cpu_step_time, srb_time, step_comp_code
        FROM smf.smf_30_5
        WHERE {_days(days)} AND job_name = '{name}'
        ORDER BY event_date DESC, time DESC LIMIT 100
        """
    )
    starts = db.query(
        f"""
        SELECT event_date, time, smf_system_id, step_name, program_name, job_class, racf_user
        FROM smf.smf_30_1
        WHERE {_days(days)} AND job_name = '{name}'
        ORDER BY event_date DESC, time DESC LIMIT 100
        """
    )
    ds = db.query(
        f"""
        SELECT 'INPUT' AS direction, event_date, time, ddname, dsname, volser_1 AS volser, excp_count
        FROM smf.smf_14 WHERE {_days(days)} AND job_name = '{name}'
        UNION ALL
        SELECT 'OUTPUT', event_date, time, ddname, dsname, volser_1, excp_count
        FROM smf.smf_15 WHERE {_days(days)} AND job_name = '{name}'
        ORDER BY event_date DESC, time DESC LIMIT 200
        """
    )
    for r in ds:
        r["dsname_display"] = display_dsname(r.get("dsname"), volser=r.get("volser"))
    racf = db.query(
        f"""
        SELECT event_date, time, user_id, event_code, class_name,
               nullIf(old_resource,'') AS old_resource,
               nullIf(access_requested,'') AS access_requested,
               nullIf(access_allowed,'') AS access_allowed
        FROM smf.smf_80
        WHERE {_days(days)} AND job_name = '{name}'
        ORDER BY event_date DESC, time DESC LIMIT 150
        """
    )
    tcp = db.query(
        f"""
        SELECT event_date, time, resource_name, remote_ip, local_ip, remote_port, local_port,
               in_bytes, out_bytes, term_code, connection_id
        FROM smf.smf_119_2
        WHERE {_days(days)} AND (resource_name = '{name}' OR as_name = '{name}')
        ORDER BY event_date DESC, time DESC LIMIT 100
        """
    )
    return {
        "job": name,
        "steps": steps,
        "ends": ends,
        "starts": starts,
        "datasets": ds,
        "racf": racf,
        "tcp": tcp,
    }


def racf_summary(
    days: int,
    *,
    users_limit: int = 40,
    classes_limit: int = 20,
) -> dict[str, Any]:
    codes = db.query(
        f"""
        SELECT event_code, count() AS rows
        FROM smf.smf_80 WHERE {_days(days)}
        GROUP BY event_code ORDER BY rows DESC LIMIT 30
        """
    )
    users = db.query(
        f"""
        SELECT user_id, count() AS rows, {last_ts_select()}
        FROM smf.smf_80 WHERE {_days(days)} AND user_id != ''
        GROUP BY user_id ORDER BY rows DESC LIMIT {int(users_limit)}
        """
    )
    classes = db.query(
        f"""
        SELECT if(class_name='', '(blank)', class_name) AS class_name, count() AS rows, {last_ts_select()}
        FROM smf.smf_80 WHERE {_days(days)}
        GROUP BY class_name ORDER BY rows DESC LIMIT {int(classes_limit)}
        """
    )
    w = _chart_days(days)
    hourly = db.query(
        f"""
        SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
               count() AS events,
               countIf(event_code = '1') AS failed_logon
        FROM smf.smf_80 WHERE {w}
        GROUP BY hour ORDER BY hour
        """
    )
    return {"codes": codes, "users": users, "classes": classes, "hourly": hourly}


def racf_events(days: int, q: str = "", limit: int = 100) -> list[dict[str, Any]]:
    filt = ""
    if q:
        qq = scrub_text(q).replace("'", "\\'")
        filt = f"AND (positionCaseInsensitive(user_id,'{qq}')>0 OR positionCaseInsensitive(job_name,'{qq}')>0 OR positionCaseInsensitive(old_resource,'{qq}')>0 OR positionCaseInsensitive(class_name,'{qq}')>0)"
    return db.query(
        f"""
        SELECT event_date, time, smf_system_id, user_id, job_name, event_code, event_qualifier,
               class_name, old_resource, access_requested, access_allowed, volser
        FROM smf.smf_80
        WHERE {_days(days)} {filt}
        ORDER BY event_date DESC, time DESC
        LIMIT {int(limit)}
        """
    )


def user_detail(user: str, days: int) -> dict[str, Any]:
    name = scrub_text(user).replace("'", "\\'")
    events = db.query(
        f"""
        SELECT event_date, time, job_name, event_code, class_name, old_resource, access_requested, access_allowed
        FROM smf.smf_80 WHERE {_days(days)} AND user_id = '{name}'
        ORDER BY event_date DESC, time DESC LIMIT 200
        """
    )
    jobs = db.query(
        f"""
        SELECT job_name, count() AS ends, sum(toUInt64OrZero(cpu_step_time)) AS cpu_sum
        FROM smf.smf_30_5
        WHERE {_days(days)} AND (racf_user = '{name}' OR user_id_field = '{name}')
        GROUP BY job_name ORDER BY ends DESC LIMIT 50
        """
    )
    return {"user": name, "events": events, "jobs": jobs}


def tcp_summary(
    days: int,
    *,
    remotes_limit: int = 40,
    ports_limit: int = 30,
    stacks_limit: int = 20,
) -> dict[str, Any]:
    hourly = db.query(
        f"""
        SELECT hour AS hour, sum(conn_count) AS conns, sum(in_bytes) AS in_bytes, sum(out_bytes) AS out_bytes
        FROM smf.stats_tcp_hourly
        WHERE {_chart_hour_days(days)}
        GROUP BY hour ORDER BY hour
        """
    )
    remotes = db.query(
        f"""
        SELECT remote_ip, count() AS conns,
               sum(toUInt64OrZero(in_bytes)) AS in_bytes,
               sum(toUInt64OrZero(out_bytes)) AS out_bytes,
               {last_ts_select()}
        FROM smf.smf_119_2
        WHERE {_days(days)} AND remote_ip != ''
        GROUP BY remote_ip ORDER BY conns DESC LIMIT {int(remotes_limit)}
        """
    )
    terms = db.query(
        f"""
        SELECT if(term_code='','(blank)',term_code) AS term_code, count() AS conns
        FROM smf.smf_119_2 WHERE {_days(days)}
        GROUP BY term_code ORDER BY conns DESC LIMIT 20
        """
    )
    ports = db.query(
        f"""
        SELECT local_port, count() AS conns, {last_ts_select()}
        FROM smf.smf_119_1 WHERE {_days(days)} AND local_port != ''
        GROUP BY local_port ORDER BY conns DESC LIMIT {int(ports_limit)}
        """
    )
    stacks = db.query(
        f"""
        SELECT tcp_stack, count() AS conns,
               sum(toUInt64OrZero(in_bytes)) AS in_bytes,
               sum(toUInt64OrZero(out_bytes)) AS out_bytes,
               {last_ts_select()}
        FROM smf.smf_119_2 WHERE {_days(days)}
        GROUP BY tcp_stack ORDER BY conns DESC LIMIT {int(stacks_limit)}
        """
    )
    return {"hourly": hourly, "remotes": remotes, "terms": terms, "ports": ports, "stacks": stacks}


def ip_detail(ip: str, days: int) -> dict[str, Any]:
    addr = scrub_text(ip).replace("'", "\\'")
    sessions = db.query(
        f"""
        SELECT event_date, time, connection_id, resource_name, as_name, tcp_stack,
               local_ip, local_port, remote_ip, remote_port, in_bytes, out_bytes, term_code
        FROM smf.smf_119_2
        WHERE {_days(days)} AND (remote_ip = '{addr}' OR local_ip = '{addr}')
        ORDER BY event_date DESC, time DESC LIMIT 200
        """
    )
    inits = db.query(
        f"""
        SELECT event_date, time, connection_id, resource_name, local_ip, local_port, remote_ip, remote_port
        FROM smf.smf_119_1
        WHERE {_days(days)} AND (remote_ip = '{addr}' OR local_ip = '{addr}')
        ORDER BY event_date DESC, time DESC LIMIT 100
        """
    )
    return {"ip": addr, "sessions": sessions, "inits": inits}


def ftp_summary(days: int) -> dict[str, Any]:
    c3 = db.query_scalar(f"SELECT count() FROM smf.smf_119_3 WHERE {_days(days)}") or 0
    c70 = db.query_scalar(f"SELECT count() FROM smf.smf_119_70 WHERE {_days(days)}") or 0
    c72 = db.query_scalar(f"SELECT count() FROM smf.smf_119_72 WHERE {_days(days)}") or 0
    subtypes = db.query(
        f"""
        SELECT table, smf_subtype, rows FROM (
          SELECT '119-1' AS table, smf_subtype, count() AS rows
          FROM smf.smf_119_1 WHERE {_days(days)} GROUP BY smf_subtype
          UNION ALL
          SELECT '119-2', smf_subtype, count()
          FROM smf.smf_119_2 WHERE {_days(days)} GROUP BY smf_subtype
          UNION ALL
          SELECT '119-5', smf_subtype, count()
          FROM smf.smf_119_5 WHERE {_days(days)} GROUP BY smf_subtype
          UNION ALL
          SELECT '119-6', smf_subtype, count()
          FROM smf.smf_119_6 WHERE {_days(days)} GROUP BY smf_subtype
          UNION ALL
          SELECT '119-10', smf_subtype, count()
          FROM smf.smf_119_10 WHERE {_days(days)} GROUP BY smf_subtype
        )
        ORDER BY rows DESC
        """
    )
    users = db.query(
        f"""
        SELECT direction, local_user, sum(bytes_sum) AS bytes, sum(xfer_count) AS transfers
        FROM smf.stats_ftp_daily
        WHERE {_chart_days(days)}
        GROUP BY direction, local_user
        ORDER BY bytes DESC LIMIT 40
        """
    )
    return {"client": int(c3), "server": int(c70), "fail72": int(c72), "subtypes": subtypes, "users": users}


def lifecycle_summary(
    days: int,
    *,
    tops_limit: int = 50,
    catalogs_limit: int = 20,
) -> dict[str, Any]:
    w = _chart_days(days)
    hourly = db.query(
        f"""
        SELECT hour, action, sum(cnt) AS rows FROM (
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'DEFINE-61' AS action, count() AS cnt FROM smf.smf_61 WHERE {w} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'DELETE-65' AS action, count() AS cnt FROM smf.smf_65 WHERE {w} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'ALTER-66' AS action, count() AS cnt FROM smf.smf_66 WHERE {w} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'SCRATCH-17' AS action, count() AS cnt FROM smf.smf_17 WHERE {w} GROUP BY hour
        ) GROUP BY hour, action ORDER BY hour
        """
    )
    tops = db.query(
        f"""
        SELECT action, entry_name, job_name, count() AS rows, max(ts) AS last_ts FROM (
          SELECT 'DEFINE' AS action, entry_name, job_name,
                 parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time))) AS ts
          FROM smf.smf_61 WHERE {_days(days)}
          UNION ALL
          SELECT 'DELETE', entry_name, job_name,
                 parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))
          FROM smf.smf_65 WHERE {_days(days)}
          UNION ALL
          SELECT 'ALTER', entry_name, job_name,
                 parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))
          FROM smf.smf_66 WHERE {_days(days)}
        )
        WHERE entry_name != ''
        GROUP BY action, entry_name, job_name
        ORDER BY rows DESC LIMIT {int(tops_limit)}
        """
    )
    catalogs = db.query(
        f"""
        SELECT catalog_name, count() AS rows, max(ts) AS last_ts FROM (
          SELECT catalog_name,
                 parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time))) AS ts
          FROM smf.smf_61 WHERE {_days(days)} AND catalog_name != ''
          UNION ALL
          SELECT catalog_name,
                 parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))
          FROM smf.smf_65 WHERE {_days(days)} AND catalog_name != ''
          UNION ALL
          SELECT catalog_name,
                 parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))
          FROM smf.smf_66 WHERE {_days(days)} AND catalog_name != ''
        )
        GROUP BY catalog_name ORDER BY rows DESC LIMIT {int(catalogs_limit)}
        """
    )
    return {"hourly": hourly, "tops": tops, "catalogs": catalogs}


def uss_summary(
    days: int,
    *,
    paths_limit: int = 50,
    jobs_limit: int = 40,
    deletes_limit: int = 40,
    mounts_limit: int = 20,
) -> dict[str, Any]:
    """SMF 92 OMVS/HFS/zFS activity — hot subtypes 10/11/17/14 plus mount KPIs."""
    w = _chart_days(days)
    d = _days(days)
    hourly = db.query(
        f"""
        SELECT hour, action, sum(cnt) AS rows FROM (
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'OPEN-10' AS action, count() AS cnt FROM smf.smf_92_10 WHERE {w} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'CLOSE-11' AS action, count() AS cnt FROM smf.smf_92_11 WHERE {w} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'ACCESS-17' AS action, count() AS cnt FROM smf.smf_92_17 WHERE {w} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'DELETE-14' AS action, count() AS cnt FROM smf.smf_92_14 WHERE {w} GROUP BY hour
        ) GROUP BY hour, action ORDER BY hour
        """
    )
    kpis_rows = db.query(
        f"""
        SELECT
          (SELECT count() FROM smf.smf_92_10 WHERE {d}) AS opens,
          (SELECT count() FROM smf.smf_92_11 WHERE {d}) AS closes,
          (SELECT count() FROM smf.smf_92_17 WHERE {d}) AS accesses,
          (SELECT count() FROM smf.smf_92_14 WHERE {d}) AS deletes,
          (SELECT count() FROM smf.smf_92_1 WHERE {d}) AS mounts,
          (SELECT count() FROM smf.smf_92_5 WHERE {d}) AS unmounts,
          (SELECT sum(toUInt64OrZero(bytes_read)) FROM smf.smf_92_11 WHERE {d}) AS bytes_read,
          (SELECT sum(toUInt64OrZero(bytes_written)) FROM smf.smf_92_11 WHERE {d}) AS bytes_written
        """
    )
    kpis = kpis_rows[0] if kpis_rows else {}
    opens = int(kpis.get("opens") or 0)
    closes = int(kpis.get("closes") or 0)
    deletes = int(kpis.get("deletes") or 0)
    open_close_ratio = round(opens / closes, 3) if closes else (float(opens) if opens else 0.0)

    # Delete spike vs prior 14d baseline (simple count ratio; empty-safe).
    delete_baseline_rows = db.query(
        f"""
        SELECT
          (SELECT count() FROM smf.smf_92_14 WHERE {d}) AS window_cnt,
          (SELECT count() FROM smf.smf_92_14
           WHERE event_date >= today() - 14 AND event_date < today() - {int(days)}
          ) AS baseline_cnt
        """
    )
    db_row = delete_baseline_rows[0] if delete_baseline_rows else {}
    baseline_cnt = int(db_row.get("baseline_cnt") or 0)
    # Normalize baseline to same-length window when possible.
    baseline_days = max(14 - int(days), 1)
    baseline_daily = baseline_cnt / baseline_days if baseline_cnt else 0.0
    expected = baseline_daily * max(int(days), 1)
    delete_spike_ratio = round(deletes / expected, 2) if expected > 0 else (0.0 if deletes == 0 else None)

    paths = db.query(
        f"""
        SELECT pathname, count() AS closes,
               sum(toUInt64OrZero(bytes_read)) AS bytes_read,
               sum(toUInt64OrZero(bytes_written)) AS bytes_written,
               {last_ts_select()}
        FROM smf.smf_92_11
        WHERE {d} AND pathname != ''
        GROUP BY pathname
        ORDER BY (bytes_read + bytes_written) DESC, closes DESC
        LIMIT {int(paths_limit)}
        """
    )
    paths_source = "close"
    if not paths:
        paths_source = "access"
        paths = db.query(
            f"""
            SELECT pathname, sum(toUInt64OrZero(access_count)) AS access_count,
                   count() AS rows, {last_ts_select()}
            FROM smf.smf_92_17
            WHERE {d} AND pathname != ''
            GROUP BY pathname
            ORDER BY access_count DESC, rows DESC
            LIMIT {int(paths_limit)}
            """
        )

    jobs = db.query(
        f"""
        SELECT job_name, saf_user,
               sum(opens) AS opens, sum(closes) AS closes,
               sum(bytes_read) AS bytes_read, sum(bytes_written) AS bytes_written,
               max(last_ts) AS last_ts
        FROM (
          SELECT job_name, saf_user, count() AS opens, toUInt64(0) AS closes,
                 toUInt64(0) AS bytes_read, toUInt64(0) AS bytes_written,
                 {last_ts_select()}
          FROM smf.smf_92_10 WHERE {d} AND job_name != ''
          GROUP BY job_name, saf_user
          UNION ALL
          SELECT job_name, saf_user, toUInt64(0), count(),
                 sum(toUInt64OrZero(bytes_read)), sum(toUInt64OrZero(bytes_written)),
                 {last_ts_select()}
          FROM smf.smf_92_11 WHERE {d} AND job_name != ''
          GROUP BY job_name, saf_user
        )
        GROUP BY job_name, saf_user
        ORDER BY (bytes_read + bytes_written) DESC, (opens + closes) DESC
        LIMIT {int(jobs_limit)}
        """
    )

    delete_rows = db.query(
        f"""
        SELECT file_name, new_file_name, job_name, saf_user, fs_name,
               count() AS rows, {last_ts_select()}
        FROM smf.smf_92_14
        WHERE {d}
        GROUP BY file_name, new_file_name, job_name, saf_user, fs_name
        ORDER BY rows DESC
        LIMIT {int(deletes_limit)}
        """
    )

    mounts = db.query(
        f"""
        SELECT fs_name, fs_type_name, job_name, saf_user,
               anyLast(fs_space_total) AS fs_space_total,
               anyLast(fs_space_used) AS fs_space_used,
               count() AS rows, {last_ts_select()}
        FROM smf.smf_92_1
        WHERE {d} AND fs_name != ''
        GROUP BY fs_name, fs_type_name, job_name, saf_user
        ORDER BY rows DESC
        LIMIT {int(mounts_limit)}
        """
    )

    unmount_io = db.query(
        f"""
        SELECT fs_name, job_name,
               sum(toUInt64OrZero(bytes_read)) AS bytes_read,
               sum(toUInt64OrZero(bytes_written)) AS bytes_written,
               count() AS rows, {last_ts_select()}
        FROM smf.smf_92_5
        WHERE {d} AND fs_name != ''
        GROUP BY fs_name, job_name
        ORDER BY (bytes_read + bytes_written) DESC
        LIMIT {int(mounts_limit)}
        """
    )

    return {
        "hourly": hourly,
        "kpis": {
            **kpis,
            "open_close_ratio": open_close_ratio,
            "delete_spike_ratio": delete_spike_ratio,
        },
        "paths": paths,
        "paths_source": paths_source,
        "jobs": jobs,
        "deletes": delete_rows,
        "mounts": mounts,
        "unmount_io": unmount_io,
    }


def cross_summary(
    days: int,
    *,
    job_limit: int = 40,
    net_limit: int = 40,
    uss_limit: int = 40,
    racf_uss_limit: int = 40,
) -> dict[str, Any]:
    """ANALYTICS.md priority crosses as practical tables."""
    job_security = db.query(
        f"""
        SELECT j.job_name,
               j.ends,
               j.cpu_sum,
               j.last_ts,
               coalesce(r.events, 0) AS racf_events
        FROM (
          SELECT job_name, count() AS ends, sum(toUInt64OrZero(cpu_step_time)) AS cpu_sum, {last_ts_select()}
          FROM smf.smf_30_5 WHERE {_days(days)} AND job_name != ''
          GROUP BY job_name
        ) j
        LEFT JOIN (
          SELECT job_name, count() AS events
          FROM smf.smf_80 WHERE {_days(days)} AND job_name != ''
          GROUP BY job_name
        ) r USING (job_name)
        ORDER BY racf_events DESC, ends DESC
        LIMIT {int(job_limit)}
        """
    )
    net_work = db.query(
        f"""
        SELECT if(resource_name='', as_name, resource_name) AS workload,
               count() AS conns,
               sum(toUInt64OrZero(in_bytes)) AS in_bytes,
               sum(toUInt64OrZero(out_bytes)) AS out_bytes,
               {last_ts_select()}
        FROM smf.smf_119_2
        WHERE {_days(days)}
        GROUP BY workload
        ORDER BY (in_bytes + out_bytes) DESC
        LIMIT {int(net_limit)}
        """
    )
    job_uss = db.query(
        f"""
        SELECT j.job_name,
               j.ends,
               j.cpu_sum,
               j.last_ts,
               coalesce(u.closes, 0) AS uss_closes,
               coalesce(u.bytes_read, 0) AS uss_bytes_read,
               coalesce(u.bytes_written, 0) AS uss_bytes_written
        FROM (
          SELECT job_name, count() AS ends, sum(toUInt64OrZero(cpu_step_time)) AS cpu_sum, {last_ts_select()}
          FROM smf.smf_30_5 WHERE {_days(days)} AND job_name != ''
          GROUP BY job_name
        ) j
        INNER JOIN (
          SELECT job_name,
                 count() AS closes,
                 sum(toUInt64OrZero(bytes_read)) AS bytes_read,
                 sum(toUInt64OrZero(bytes_written)) AS bytes_written
          FROM smf.smf_92_11 WHERE {_days(days)} AND job_name != ''
          GROUP BY job_name
        ) u USING (job_name)
        ORDER BY (uss_bytes_read + uss_bytes_written) DESC, uss_closes DESC
        LIMIT {int(uss_limit)}
        """
    )
    racf_uss = db.query(
        f"""
        SELECT u.saf_user AS user_id,
               u.deletes AS uss_deletes,
               coalesce(r.events, 0) AS racf_events,
               u.last_ts
        FROM (
          SELECT saf_user, count() AS deletes, {last_ts_select()}
          FROM smf.smf_92_14
          WHERE {_days(days)} AND saf_user != ''
          GROUP BY saf_user
        ) u
        LEFT JOIN (
          SELECT user_id, count() AS events
          FROM smf.smf_80
          WHERE {_days(days)} AND user_id != ''
          GROUP BY user_id
        ) r ON r.user_id = u.saf_user
        ORDER BY uss_deletes DESC, racf_events DESC
        LIMIT {int(racf_uss_limit)}
        """
    )
    return {
        "job_security": job_security,
        "net_work": net_work,
        "job_uss": job_uss,
        "racf_uss": racf_uss,
    }
