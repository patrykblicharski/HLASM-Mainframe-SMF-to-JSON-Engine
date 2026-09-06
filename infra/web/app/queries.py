"""Shared query snippets against ClickHouse SMF schema."""

from __future__ import annotations

from typing import Any

from . import db
from .helpers import display_dsname, scrub_text


def _days(days: int) -> str:
    return db.date_filter(days)


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
      (SELECT count() FROM smf.smf_66 WHERE {_days(days)}) AS alt66
    """
    rows = db.query(sql)
    return rows[0] if rows else {}


def records_by_table(days: int) -> list[dict[str, Any]]:
    return db.query(
        f"""
        SELECT table_name, sum(row_count) AS rows
        FROM smf.stats_records_daily
        WHERE {_days(days)}
        GROUP BY table_name
        ORDER BY rows DESC
        LIMIT 40
        """
    )


def hourly_activity(days: int) -> list[dict[str, Any]]:
    return db.query(
        f"""
        SELECT hour, source, sum(cnt) AS rows FROM (
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'INPUT-14' AS source, count() AS cnt
          FROM smf.smf_14 WHERE {_days(days)} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'OUTPUT-15' AS source, count() AS cnt
          FROM smf.smf_15 WHERE {_days(days)} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'RACF-80' AS source, count() AS cnt
          FROM smf.smf_80 WHERE {_days(days)} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'TCP-119-2' AS source, count() AS cnt
          FROM smf.smf_119_2 WHERE {_days(days)} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'JOB-30-5' AS source, count() AS cnt
          FROM smf.smf_30_5 WHERE {_days(days)} GROUP BY hour
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
        SELECT direction, job_name, dsname, volser, sum(rows) AS rows, sum(excp) AS excp FROM (
          SELECT 'INPUT' AS direction, job_name,
                 if(trim(BOTH ' ' FROM dsname) = '' OR match(dsname, '^[\\\\x00-\\\\x1f\\\\x7f-\\\\x9f\\\\x{{fffd}}?]+$'), '', dsname) AS dsname,
                 volser_1 AS volser, count() AS rows, sum(toUInt64OrZero(excp_count)) AS excp
          FROM smf.smf_14 WHERE {_days(days)} GROUP BY job_name, dsname, volser
          UNION ALL
          SELECT 'OUTPUT', job_name,
                 if(trim(BOTH ' ' FROM dsname) = '' OR match(dsname, '^[\\\\x00-\\\\x1f\\\\x7f-\\\\x9f\\\\x{{fffd}}?]+$'), '', dsname) AS dsname,
                 volser_1 AS volser, count(), sum(toUInt64OrZero(excp_count))
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
               volume_serial AS volser, count() AS rows
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
    return db.query(
        f"""
        SELECT hour, direction, sum(cnt) AS rows FROM (
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'INPUT' AS direction, count() AS cnt
          FROM smf.smf_14 WHERE {_days(days)} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'OUTPUT' AS direction, count() AS cnt
          FROM smf.smf_15 WHERE {_days(days)} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'SCRATCH' AS direction, count() AS cnt
          FROM smf.smf_17 WHERE {_days(days)} GROUP BY hour
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


def jobs_top(days: int, limit: int = 50, q: str = "", hour_from: str = "", hour_to: str = "") -> list[dict[str, Any]]:
    filt = ""
    if q:
        qq = scrub_text(q).replace("'", "\\'")
        filt = f"AND positionCaseInsensitive(job_name, '{qq}') > 0"
    hf = _hour_bounds(hour_from, hour_to)
    return db.query(
        f"""
        SELECT e.job_name, e.smf_system_id, e.ends,
               coalesce(p.programs, '') AS programs,
               coalesce(p.steps, '') AS steps,
               coalesce(p.cpu_sum, 0) AS cpu_sum
        FROM (
          SELECT job_name, smf_system_id, count() AS ends
          FROM smf.smf_30_5
          WHERE {_days(days)} AND job_name != '' {filt} {hf}
          GROUP BY job_name, smf_system_id
        ) e
        LEFT JOIN (
          SELECT job_name, smf_system_id,
                 arrayStringConcat(arrayFilter(x -> x != '', topK(3)(program_name)), ', ') AS programs,
                 arrayStringConcat(arrayFilter(x -> x != '', topK(3)(step_name)), ', ') AS steps,
                 sum(toUInt64OrZero(cpu_step_time)) AS cpu_sum
          FROM smf.smf_30_4
          WHERE {_days(days)} AND job_name != '' {filt} {hf}
          GROUP BY job_name, smf_system_id
        ) p USING (job_name, smf_system_id)
        ORDER BY e.ends DESC
        LIMIT {int(limit)}
        """
    )


def _hour_bounds(hour_from: str, hour_to: str) -> str:
    """Optional brush filter: restrict to [hour_from, hour_to) wall-clock hours."""
    a = scrub_text(hour_from).replace("'", "\\'")
    b = scrub_text(hour_to).replace("'", "\\'")
    if not a and not b:
        return ""
    h = (
        "toStartOfHour(parseDateTimeBestEffort("
        "concat(toString(event_date),' ',if(time='','00:00:00',time))))"
    )
    parts = []
    if a:
        parts.append(f"{h} >= parseDateTimeBestEffort('{a}')")
    if b:
        parts.append(f"{h} < parseDateTimeBestEffort('{b}')")
    return (" AND " + " AND ".join(parts)) if parts else ""


def jobs_hourly(days: int) -> list[dict[str, Any]]:
    return db.query(
        f"""
        SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
               count() AS ends
        FROM smf.smf_30_5
        WHERE {_days(days)}
        GROUP BY hour ORDER BY hour
        """
    )


def job_class_mix(days: int, hour_from: str = "", hour_to: str = "") -> list[dict[str, Any]]:
    hf = _hour_bounds(hour_from, hour_to)
    return db.query(
        f"""
        SELECT if(job_class = '', '(blank)', job_class) AS job_class, count() AS rows
        FROM smf.smf_30_4
        WHERE {_days(days)} {hf}
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


def racf_summary(days: int) -> dict[str, Any]:
    codes = db.query(
        f"""
        SELECT event_code, count() AS rows
        FROM smf.smf_80 WHERE {_days(days)}
        GROUP BY event_code ORDER BY rows DESC LIMIT 30
        """
    )
    users = db.query(
        f"""
        SELECT user_id, count() AS rows
        FROM smf.smf_80 WHERE {_days(days)} AND user_id != ''
        GROUP BY user_id ORDER BY rows DESC LIMIT 40
        """
    )
    classes = db.query(
        f"""
        SELECT if(class_name='', '(blank)', class_name) AS class_name, count() AS rows
        FROM smf.smf_80 WHERE {_days(days)}
        GROUP BY class_name ORDER BY rows DESC LIMIT 20
        """
    )
    hourly = db.query(
        f"""
        SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
               count() AS events,
               countIf(event_code = '1') AS failed_logon
        FROM smf.smf_80 WHERE {_days(days)}
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


def tcp_summary(days: int) -> dict[str, Any]:
    hourly = db.query(
        f"""
        SELECT hour AS hour, sum(conn_count) AS conns, sum(in_bytes) AS in_bytes, sum(out_bytes) AS out_bytes
        FROM smf.stats_tcp_hourly
        WHERE toDate(hour) >= today() - {int(days)}
        GROUP BY hour ORDER BY hour
        """
    )
    remotes = db.query(
        f"""
        SELECT remote_ip, count() AS conns,
               sum(toUInt64OrZero(in_bytes)) AS in_bytes,
               sum(toUInt64OrZero(out_bytes)) AS out_bytes
        FROM smf.smf_119_2
        WHERE {_days(days)} AND remote_ip != ''
        GROUP BY remote_ip ORDER BY conns DESC LIMIT 40
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
        SELECT local_port, count() AS conns
        FROM smf.smf_119_1 WHERE {_days(days)} AND local_port != ''
        GROUP BY local_port ORDER BY conns DESC LIMIT 30
        """
    )
    stacks = db.query(
        f"""
        SELECT tcp_stack, count() AS conns,
               sum(toUInt64OrZero(in_bytes)) AS in_bytes,
               sum(toUInt64OrZero(out_bytes)) AS out_bytes
        FROM smf.smf_119_2 WHERE {_days(days)}
        GROUP BY tcp_stack ORDER BY conns DESC LIMIT 20
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
        WHERE {_days(days)}
        GROUP BY direction, local_user
        ORDER BY bytes DESC LIMIT 40
        """
    )
    return {"client": int(c3), "server": int(c70), "fail72": int(c72), "subtypes": subtypes, "users": users}


def lifecycle_summary(days: int) -> dict[str, Any]:
    hourly = db.query(
        f"""
        SELECT hour, action, sum(cnt) AS rows FROM (
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'DEFINE-61' AS action, count() AS cnt FROM smf.smf_61 WHERE {_days(days)} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'DELETE-65' AS action, count() AS cnt FROM smf.smf_65 WHERE {_days(days)} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'ALTER-66' AS action, count() AS cnt FROM smf.smf_66 WHERE {_days(days)} GROUP BY hour
          UNION ALL
          SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,
                 'SCRATCH-17' AS action, count() AS cnt FROM smf.smf_17 WHERE {_days(days)} GROUP BY hour
        ) GROUP BY hour, action ORDER BY hour
        """
    )
    tops = db.query(
        f"""
        SELECT action, entry_name, job_name, count() AS rows FROM (
          SELECT 'DEFINE' AS action, entry_name, job_name FROM smf.smf_61 WHERE {_days(days)}
          UNION ALL
          SELECT 'DELETE', entry_name, job_name FROM smf.smf_65 WHERE {_days(days)}
          UNION ALL
          SELECT 'ALTER', entry_name, job_name FROM smf.smf_66 WHERE {_days(days)}
        )
        WHERE entry_name != ''
        GROUP BY action, entry_name, job_name
        ORDER BY rows DESC LIMIT 50
        """
    )
    catalogs = db.query(
        f"""
        SELECT catalog_name, count() AS rows FROM (
          SELECT catalog_name FROM smf.smf_61 WHERE {_days(days)} AND catalog_name != ''
          UNION ALL
          SELECT catalog_name FROM smf.smf_65 WHERE {_days(days)} AND catalog_name != ''
          UNION ALL
          SELECT catalog_name FROM smf.smf_66 WHERE {_days(days)} AND catalog_name != ''
        )
        GROUP BY catalog_name ORDER BY rows DESC LIMIT 20
        """
    )
    return {"hourly": hourly, "tops": tops, "catalogs": catalogs}


def cross_summary(days: int) -> dict[str, Any]:
    """ANALYTICS.md priority crosses as practical tables."""
    job_security = db.query(
        f"""
        SELECT j.job_name,
               j.ends,
               j.cpu_sum,
               coalesce(r.events, 0) AS racf_events
        FROM (
          SELECT job_name, count() AS ends, sum(toUInt64OrZero(cpu_step_time)) AS cpu_sum
          FROM smf.smf_30_5 WHERE {_days(days)} AND job_name != ''
          GROUP BY job_name
        ) j
        LEFT JOIN (
          SELECT job_name, count() AS events
          FROM smf.smf_80 WHERE {_days(days)} AND job_name != ''
          GROUP BY job_name
        ) r USING (job_name)
        ORDER BY racf_events DESC, ends DESC
        LIMIT 40
        """
    )
    net_work = db.query(
        f"""
        SELECT if(resource_name='', as_name, resource_name) AS workload,
               count() AS conns,
               sum(toUInt64OrZero(in_bytes)) AS in_bytes,
               sum(toUInt64OrZero(out_bytes)) AS out_bytes
        FROM smf.smf_119_2
        WHERE {_days(days)}
        GROUP BY workload
        ORDER BY (in_bytes + out_bytes) DESC
        LIMIT 40
        """
    )
    return {"job_security": job_security, "net_work": net_work}
