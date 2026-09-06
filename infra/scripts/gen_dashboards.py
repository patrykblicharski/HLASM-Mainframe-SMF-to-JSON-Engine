#!/usr/bin/env python3
"""Generate polished Grafana SMF dashboards (default range now-4d).

Fixes vs prior revision:
- Every UNION branch aliases columns (AS hour / AS source / AS cnt) — CH 24.8 rejects GROUP BY hour otherwise
- All panels use Grafana $__timeFilter so zoom/time picker updates tables
- Job program/step/class/CPU come from smf_30_4 (step end) where dumps leave 30-5 blank
- Stat panels show value only (no redundant count() label)
- Mix panels use named metrics (events/share) + bar gauges where a donut misleads
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "grafana" / "dashboards"
DS = {"type": "grafana-clickhouse-datasource", "uid": "clickhouse_smf"}

# Grafana ClickHouse macros — follow dashboard time picker / brush zoom
TF = "$__timeFilter(event_date)"
TF_DAY = "$__timeFilter(event_date)"
TF_HOUR = "$__timeFilter(hour)"


def hour_expr() -> str:
    return (
        "toStartOfHour(parseDateTimeBestEffort("
        "concat(toString(event_date),' ',if(time='','00:00:00',time))))"
    )


def union_hourly(parts: list[tuple[str, str]]) -> str:
    """parts: list of (table, label). Each branch fully aliased for CH 24.8."""
    h = hour_expr()
    branches = []
    for table, label in parts:
        branches.append(
            f"SELECT {h} AS hour, '{label}' AS series, count() AS cnt "
            f"FROM smf.{table} WHERE {TF} GROUP BY hour"
        )
    inner = "\n  UNION ALL\n  ".join(branches)
    return (
        f"SELECT hour AS time, series, sum(cnt) AS value FROM (\n  {inner}\n) "
        f"GROUP BY time, series ORDER BY time"
    )


def panel_base(title, ptype, x, y, w, h, sql, **extra):
    p = {
        "title": title,
        "type": ptype,
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "datasource": DS,
        "targets": [
            {
                "refId": "A",
                "format": 1,
                "queryType": "sql",
                "rawSql": sql,
            }
        ],
        "fieldConfig": {"defaults": {}, "overrides": []},
        "options": {},
    }
    p.update(extra)
    return p


def timeseries(title, x, y, w, h, sql, *, bars=False, unit=None, desc="", stacking=None):
    custom = {
        "drawStyle": "bars" if bars else "line",
        "fillOpacity": 45 if bars else 18,
        "spanNulls": True,
        "lineWidth": 2,
    }
    if stacking:
        custom["stacking"] = {"mode": stacking}
    defaults = {"custom": custom}
    if unit:
        defaults["unit"] = unit
    return panel_base(
        title,
        "timeseries",
        x,
        y,
        w,
        h,
        sql,
        description=desc,
        fieldConfig={"defaults": defaults, "overrides": []},
        options={"legend": {"displayMode": "list", "placement": "bottom"}},
    )


def stat(title, x, y, w, h, sql, color="blue"):
    # Alias scalar so Grafana does not paint "count()" as the field name
    if " AS " not in sql.upper().split("SELECT", 1)[-1].split("FROM", 1)[0]:
        sql = sql.replace("SELECT ", "SELECT (", 1)
        # crude: wrap whole select expression — prefer callers pass alias
        pass
    return panel_base(
        title,
        "stat",
        x,
        y,
        w,
        h,
        sql,
        options={
            "colorMode": "background",
            "graphMode": "none",
            "textMode": "value",
            "reduceOptions": {"calcs": ["lastNotNull"]},
        },
        fieldConfig={
            "defaults": {
                "displayName": title,
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "semi-dark-blue", "value": None},
                        {"color": color, "value": 0},
                    ],
                },
            },
            "overrides": [],
        },
    )


def table(title, x, y, w, h, sql, links=None, desc=""):
    fc = {"defaults": {}, "overrides": []}
    if links:
        fc["defaults"]["links"] = links
    return panel_base(
        title,
        "table",
        x,
        y,
        w,
        h,
        sql,
        description=desc,
        fieldConfig=fc,
        options={"showHeader": True, "cellHeight": "sm"},
    )


def bargauge(title, x, y, w, h, sql, unit=None, desc=""):
    defaults = {
        "color": {"mode": "palette-classic"},
        "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]},
    }
    if unit:
        defaults["unit"] = unit
    return panel_base(
        title,
        "bargauge",
        x,
        y,
        w,
        h,
        sql,
        description=desc,
        options={"orientation": "horizontal", "displayMode": "gradient", "showUnfilled": True},
        fieldConfig={"defaults": defaults, "overrides": []},
    )


def pie(title, x, y, w, h, sql, desc=""):
    return panel_base(
        title,
        "piechart",
        x,
        y,
        w,
        h,
        sql,
        description=desc,
        options={
            "legend": {"displayMode": "table", "placement": "right", "values": ["value", "percent"]},
            "pieType": "donut",
            "displayLabels": ["percent"],
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": ""},
        },
        fieldConfig={"defaults": {"color": {"mode": "palette-classic"}}, "overrides": []},
    )


def dash(uid, title, tags, panels, templating=None, links=None):
    return {
        "annotations": {"list": []},
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 1,
        "id": None,
        "links": links
        or [
            {"title": "Overview", "type": "link", "url": "/d/smf-overview"},
            {"title": "Datasets", "type": "link", "url": "/d/smf-datasets"},
            {"title": "Jobs", "type": "link", "url": "/d/smf-jobs"},
            {"title": "RACF", "type": "link", "url": "/d/smf-racf"},
            {"title": "TCP", "type": "link", "url": "/d/smf-tcp"},
            {"title": "Lifecycle", "type": "link", "url": "/d/smf-lifecycle"},
            {"title": "Cross", "type": "link", "url": "/d/smf-cross"},
            {"title": "Web App :8080", "type": "link", "url": "http://${__hostname}:8080"},
        ],
        "panels": panels,
        "schemaVersion": 39,
        "tags": tags,
        "templating": {"list": templating or []},
        "time": {"from": "now-4d", "to": "now"},
        "timezone": "browser",
        "title": title,
        "uid": uid,
        "version": 4,
        "refresh": "5m",
    }


JOB_LINK = [
    {
        "title": "Job detail",
        "url": "/d/smf-job-detail?var-job=${__data.fields.job_name}&from=${__from}&to=${__to}",
    }
]
USER_LINK = [
    {
        "title": "User detail",
        "url": "/d/smf-user-detail?var-user=${__data.fields.user_id}&from=${__from}&to=${__to}",
    }
]
DSN_LINK = [
    {
        "title": "Dataset detail",
        "url": "/d/smf-dataset-detail?var-dsname=${__data.fields.dsname}&from=${__from}&to=${__to}",
    }
]
IP_LINK = [
    {
        "title": "IP detail",
        "url": "/d/smf-ip-detail?var-ip=${__data.fields.remote_ip}&from=${__from}&to=${__to}",
    }
]


def build_all() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    h = hour_expr()

    overview = dash(
        "smf-overview",
        "SMF Overview",
        ["smf", "overview"],
        [
            stat(
                "Total rows",
                0,
                0,
                4,
                4,
                f"SELECT sum(row_count) AS value FROM smf.stats_records_daily WHERE {TF_DAY}",
                "teal",
            ),
            stat(
                "Distinct days",
                4,
                0,
                4,
                4,
                f"SELECT countDistinct(event_date) AS value FROM smf.stats_records_daily WHERE {TF_DAY}",
                "purple",
            ),
            stat(
                "INPUT 14",
                8,
                0,
                4,
                4,
                f"SELECT count() AS value FROM smf.smf_14 WHERE {TF}",
                "green",
            ),
            stat(
                "RACF 80",
                12,
                0,
                4,
                4,
                f"SELECT count() AS value FROM smf.smf_80 WHERE {TF}",
                "red",
            ),
            stat(
                "TCP 119-2",
                16,
                0,
                4,
                4,
                f"SELECT count() AS value FROM smf.smf_119_2 WHERE {TF}",
                "blue",
            ),
            stat(
                "Jobs 30-5",
                20,
                0,
                4,
                4,
                f"SELECT count() AS value FROM smf.smf_30_5 WHERE {TF}",
                "orange",
            ),
            timeseries(
                "Hourly pulse (multi-type)",
                0,
                4,
                16,
                9,
                union_hourly(
                    [
                        ("smf_14", "INPUT-14"),
                        ("smf_15", "OUTPUT-15"),
                        ("smf_80", "RACF-80"),
                        ("smf_119_2", "TCP-119-2"),
                        ("smf_30_5", "JOB-30-5"),
                    ]
                ),
                bars=True,
                stacking="normal",
                desc="Uses dashboard time range. Aliased UNION branches for ClickHouse 24.8.",
            ),
            bargauge(
                "Rows by table (top 12)",
                16,
                4,
                8,
                9,
                f"SELECT table_name, sum(row_count) AS rows FROM smf.stats_records_daily WHERE {TF_DAY} GROUP BY table_name ORDER BY rows DESC LIMIT 12",
                desc="Bar gauge instead of donut — clearer share of loaded tables.",
            ),
            bargauge(
                "Top systems",
                0,
                13,
                12,
                8,
                f"SELECT smf_system_id, sum(row_count) AS rows FROM smf.stats_records_daily WHERE {TF_DAY} GROUP BY smf_system_id ORDER BY rows DESC",
            ),
            table(
                "Daily / table / system",
                12,
                13,
                12,
                8,
                f"SELECT event_date, table_name, smf_system_id, sum(row_count) AS rows FROM smf.stats_records_daily WHERE {TF_DAY} GROUP BY event_date, table_name, smf_system_id ORDER BY rows DESC LIMIT 200",
            ),
        ],
    )

    datasets = dash(
        "smf-datasets",
        "SMF Datasets (14/15/17)",
        ["smf", "dataset"],
        [
            timeseries(
                "I/O + scratch by hour",
                0,
                0,
                16,
                8,
                union_hourly(
                    [
                        ("smf_14", "INPUT"),
                        ("smf_15", "OUTPUT"),
                        ("smf_17", "SCRATCH"),
                    ]
                ),
                bars=True,
                stacking="normal",
            ),
            bargauge(
                "INPUT vs OUTPUT vs SCRATCH",
                16,
                0,
                8,
                8,
                f"""SELECT direction, sum(c) AS events FROM (
  SELECT 'INPUT' AS direction, count() AS c FROM smf.smf_14 WHERE {TF}
  UNION ALL SELECT 'OUTPUT' AS direction, count() AS c FROM smf.smf_15 WHERE {TF}
  UNION ALL SELECT 'SCRATCH' AS direction, count() AS c FROM smf.smf_17 WHERE {TF}
) GROUP BY direction ORDER BY events DESC""",
                desc="Event counts by SMF type (not a misleading single-slice pie).",
            ),
            table(
                "Top datasets (blank JFCB shown safely)",
                0,
                8,
                24,
                10,
                f"""SELECT direction, job_name,
  if(dsname = '' OR match(dsname, '^[\\\\x00-\\\\x1f\\\\x7f-\\\\x9f\\\\x{{fffd}}?]+$'), concat('(no dsname) ', volser), dsname) AS dsname_display,
  if(dsname = '' OR match(dsname, '^[\\\\x00-\\\\x1f\\\\x7f-\\\\x9f\\\\x{{fffd}}?]+$'), '', dsname) AS dsname,
  volser, sum(rows) AS rows, sum(excp) AS excp
FROM (
  SELECT 'INPUT' AS direction, job_name, trim(BOTH ' ' FROM dsname) AS dsname, volser_1 AS volser, count() AS rows, sum(toUInt64OrZero(excp_count)) AS excp
  FROM smf.smf_14 WHERE {TF} GROUP BY job_name, dsname, volser
  UNION ALL
  SELECT 'OUTPUT' AS direction, job_name, trim(BOTH ' ' FROM dsname) AS dsname, volser_1 AS volser, count() AS rows, sum(toUInt64OrZero(excp_count)) AS excp
  FROM smf.smf_15 WHERE {TF} GROUP BY job_name, dsname, volser
)
GROUP BY direction, job_name, dsname_display, dsname, volser
ORDER BY rows DESC LIMIT 60""",
                links=DSN_LINK + JOB_LINK,
            ),
            table(
                "Top scratches",
                0,
                18,
                24,
                8,
                f"""SELECT job_name,
  if(trim(BOTH ' ' FROM dsname)='','(no dsname)', dsname) AS dsname_display,
  if(trim(BOTH ' ' FROM dsname)='','', dsname) AS dsname,
  volume_serial AS volser, count() AS rows
FROM smf.smf_17 WHERE {TF}
GROUP BY job_name, dsname_display, dsname, volser ORDER BY rows DESC LIMIT 50""",
                links=DSN_LINK + JOB_LINK,
            ),
        ],
    )

    jobs = dash(
        "smf-jobs",
        "SMF Jobs (30)",
        ["smf", "jobs", "30"],
        [
            timeseries(
                "Job ends by hour (30-5)",
                0,
                0,
                12,
                8,
                f"SELECT {h} AS time, count() AS ends FROM smf.smf_30_5 WHERE {TF} GROUP BY time ORDER BY time",
                bars=True,
            ),
            bargauge(
                "Job class mix (30-4 step end)",
                12,
                0,
                12,
                8,
                f"""SELECT if(job_class='','(blank)',job_class) AS job_class, count() AS steps
FROM smf.smf_30_4 WHERE {TF} GROUP BY job_class ORDER BY steps DESC LIMIT 15""",
                desc="Class comes from SMF 30-4 — subtype 5 often leaves job_class/program blank in dumps.",
            ),
            table(
                "Top jobs (30-5 ends + 30-4 programs)",
                0,
                8,
                12,
                10,
                f"""SELECT e.job_name, e.ends, coalesce(p.with_program, 0) AS with_program,
  coalesce(p.with_step, 0) AS with_step, coalesce(p.cpu_timer_sum, 0) AS cpu_timer_sum
FROM (
  SELECT job_name, count() AS ends FROM smf.smf_30_5 WHERE {TF} AND job_name!='' GROUP BY job_name
) e
LEFT JOIN (
  SELECT job_name,
         countIf(program_name!='') AS with_program,
         countIf(step_name!='') AS with_step,
         sum(toUInt64OrZero(cpu_step_time)) AS cpu_timer_sum
  FROM smf.smf_30_4 WHERE {TF} AND job_name!='' GROUP BY job_name
) p USING (job_name)
ORDER BY e.ends DESC LIMIT 40""",
                links=JOB_LINK,
                desc="cpu_timer_sum = sum(SMF cpu_step_time) from 30-4, raw timer units from the record.",
            ),
            table(
                "Programs / steps (from 30-4)",
                12,
                8,
                12,
                10,
                f"""SELECT nullIf(program_name,'') AS program_name, nullIf(step_name,'') AS step_name, count() AS steps
FROM smf.smf_30_4 WHERE {TF} AND (program_name!='' OR step_name!='')
GROUP BY program_name, step_name ORDER BY steps DESC LIMIT 40""",
                desc="Step-end records (30-4) carry program/step; 30-5 job-end often does not in this dump.",
            ),
            bargauge(
                "CPU timer sum by job (30-4, top 15)",
                0,
                18,
                24,
                8,
                f"""SELECT job_name, sum(toUInt64OrZero(cpu_step_time)) AS cpu_timer_sum
FROM smf.smf_30_4 WHERE {TF} AND job_name!=''
GROUP BY job_name ORDER BY cpu_timer_sum DESC LIMIT 15""",
                desc="Raw SMF cpu_step_time units (not wall-clock seconds).",
            ),
        ],
    )

    racf = dash(
        "smf-racf",
        "SMF RACF (80)",
        ["smf", "racf", "security"],
        [
            timeseries(
                "RACF events & failed logons (EVT 1)",
                0,
                0,
                16,
                8,
                f"""SELECT {h} AS time,
  count() AS events, countIf(event_code='1') AS failed_logon
FROM smf.smf_80 WHERE {TF} GROUP BY time ORDER BY time""",
            ),
            bargauge(
                "Event codes",
                16,
                0,
                8,
                8,
                f"SELECT concat('EVT ', event_code) AS event_code, count() AS events FROM smf.smf_80 WHERE {TF} GROUP BY event_code ORDER BY events DESC LIMIT 12",
            ),
            table(
                "Top users",
                0,
                8,
                8,
                9,
                f"SELECT user_id, count() AS events FROM smf.smf_80 WHERE {TF} AND user_id!='' GROUP BY user_id ORDER BY events DESC LIMIT 40",
                links=USER_LINK,
            ),
            table(
                "Top jobs",
                8,
                8,
                8,
                9,
                f"SELECT job_name, count() AS events FROM smf.smf_80 WHERE {TF} AND job_name!='' GROUP BY job_name ORDER BY events DESC LIMIT 40",
                links=JOB_LINK,
            ),
            bargauge(
                "Class mix",
                16,
                8,
                8,
                9,
                f"SELECT if(class_name='','(blank)',class_name) AS class_name, count() AS events FROM smf.smf_80 WHERE {TF} GROUP BY class_name ORDER BY events DESC LIMIT 12",
            ),
            table(
                "Recent events",
                0,
                17,
                24,
                9,
                f"""SELECT
  concat(toString(event_date),' ',if(time='','00:00:00',time)) AS event_ts,
  date AS smf_date, time AS smf_time,
  user_id, job_name, event_code, class_name,
  nullIf(old_resource,'') AS old_resource,
  nullIf(access_requested,'') AS access_requested,
  nullIf(access_allowed,'') AS access_allowed
FROM smf.smf_80 WHERE {TF}
ORDER BY event_date DESC, time DESC LIMIT 100""",
                links=USER_LINK + JOB_LINK,
                desc="old_resource / access_* are sparse in many dumps; event_ts always from date+time.",
            ),
        ],
    )

    tcp = dash(
        "smf-tcp",
        "SMF TCP (119-1/2)",
        ["smf", "tcp", "119"],
        [
            timeseries(
                "Terminations / hour",
                0,
                0,
                12,
                8,
                f"SELECT hour AS time, sum(conn_count) AS connections FROM smf.stats_tcp_hourly WHERE {TF_HOUR} GROUP BY hour ORDER BY time",
            ),
            timeseries(
                "Bytes in/out / hour",
                12,
                0,
                12,
                8,
                f"SELECT hour AS time, sum(in_bytes) AS in_bytes, sum(out_bytes) AS out_bytes FROM smf.stats_tcp_hourly WHERE {TF_HOUR} GROUP BY hour ORDER BY time",
                unit="decbytes",
            ),
            table(
                "Top remote IPs",
                0,
                8,
                12,
                10,
                f"""SELECT remote_ip, count() AS conns, sum(toUInt64OrZero(in_bytes)) AS in_bytes, sum(toUInt64OrZero(out_bytes)) AS out_bytes
FROM smf.smf_119_2 WHERE {TF} AND remote_ip!=''
GROUP BY remote_ip ORDER BY conns DESC LIMIT 40""",
                links=IP_LINK,
            ),
            bargauge(
                "Termination codes",
                12,
                8,
                12,
                10,
                f"SELECT if(term_code='','(blank)',term_code) AS term_code, count() AS conns FROM smf.smf_119_2 WHERE {TF} GROUP BY term_code ORDER BY conns DESC LIMIT 15",
            ),
            table(
                "Local ports (119-1)",
                0,
                18,
                12,
                8,
                f"SELECT local_port, count() AS conns FROM smf.smf_119_1 WHERE {TF} AND local_port!='' GROUP BY local_port ORDER BY conns DESC LIMIT 40",
            ),
            table(
                "Top workloads (resource/AS)",
                12,
                18,
                12,
                8,
                f"""SELECT if(resource_name='',as_name,resource_name) AS job_name, count() AS conns,
  sum(toUInt64OrZero(in_bytes)+toUInt64OrZero(out_bytes)) AS bytes
FROM smf.smf_119_2 WHERE {TF}
GROUP BY job_name ORDER BY bytes DESC LIMIT 40""",
                links=JOB_LINK,
            ),
        ],
    )

    ftp = dash(
        "smf-ftp",
        "SMF FTP (119-3/70)",
        ["smf", "ftp"],
        [
            stat(
                "Client 119-3",
                0,
                0,
                6,
                4,
                f"SELECT count() AS value FROM smf.smf_119_3 WHERE {TF}",
                "teal",
            ),
            stat(
                "Server 119-70",
                6,
                0,
                6,
                4,
                f"SELECT count() AS value FROM smf.smf_119_70 WHERE {TF}",
                "blue",
            ),
            stat(
                "Fail 119-72",
                12,
                0,
                6,
                4,
                f"SELECT count() AS value FROM smf.smf_119_72 WHERE {TF}",
                "red",
            ),
            stat(
                "FTP present",
                18,
                0,
                6,
                4,
                f"SELECT if((SELECT count() FROM smf.smf_119_3 WHERE {TF})+(SELECT count() FROM smf.smf_119_70 WHERE {TF})=0, 0, 1) AS value",
                "orange",
            ),
            timeseries(
                "FTP bytes / day",
                0,
                4,
                12,
                8,
                f"SELECT toDateTime(event_date) AS time, direction, sum(bytes_sum) AS bytes FROM smf.stats_ftp_daily WHERE {TF_DAY} GROUP BY time, direction ORDER BY time",
                bars=True,
                unit="decbytes",
                desc="Empty when dump has no subtype 3/70.",
            ),
            table(
                "Available 119 subtypes",
                12,
                4,
                12,
                8,
                f"""SELECT '119-1' AS subtype, count() AS rows FROM smf.smf_119_1 WHERE {TF}
UNION ALL SELECT '119-2', count() FROM smf.smf_119_2 WHERE {TF}
UNION ALL SELECT '119-5', count() FROM smf.smf_119_5 WHERE {TF}
UNION ALL SELECT '119-6', count() FROM smf.smf_119_6 WHERE {TF}
UNION ALL SELECT '119-10', count() FROM smf.smf_119_10 WHERE {TF}
UNION ALL SELECT '119-3', count() FROM smf.smf_119_3 WHERE {TF}
UNION ALL SELECT '119-70', count() FROM smf.smf_119_70 WHERE {TF}""",
            ),
            table(
                "Top FTP users",
                0,
                12,
                24,
                9,
                f"SELECT direction, local_user, sum(bytes_sum) AS bytes, sum(xfer_count) AS transfers FROM smf.stats_ftp_daily WHERE {TF_DAY} GROUP BY direction, local_user ORDER BY bytes DESC LIMIT 50",
            ),
        ],
    )

    lifecycle = dash(
        "smf-lifecycle",
        "SMF Lifecycle (61/65/66/17)",
        ["smf", "lifecycle", "catalog"],
        [
            timeseries(
                "Catalog + scratch by hour",
                0,
                0,
                16,
                9,
                union_hourly(
                    [
                        ("smf_61", "DEFINE-61"),
                        ("smf_65", "DELETE-65"),
                        ("smf_66", "ALTER-66"),
                        ("smf_17", "SCRATCH-17"),
                    ]
                ),
                bars=True,
                stacking="normal",
            ),
            bargauge(
                "Action mix",
                16,
                0,
                8,
                9,
                f"""SELECT action, sum(c) AS events FROM (
  SELECT 'DEFINE' AS action, count() AS c FROM smf.smf_61 WHERE {TF}
  UNION ALL SELECT 'DELETE' AS action, count() AS c FROM smf.smf_65 WHERE {TF}
  UNION ALL SELECT 'ALTER' AS action, count() AS c FROM smf.smf_66 WHERE {TF}
  UNION ALL SELECT 'SCRATCH' AS action, count() AS c FROM smf.smf_17 WHERE {TF}
) GROUP BY action ORDER BY events DESC""",
            ),
            table(
                "Top catalog entries",
                0,
                9,
                24,
                10,
                f"""SELECT action, entry_name AS dsname, job_name, count() AS rows FROM (
  SELECT 'DEFINE' AS action, entry_name, job_name FROM smf.smf_61 WHERE {TF}
  UNION ALL SELECT 'DELETE' AS action, entry_name, job_name FROM smf.smf_65 WHERE {TF}
  UNION ALL SELECT 'ALTER' AS action, entry_name, job_name FROM smf.smf_66 WHERE {TF}
) WHERE entry_name!='' GROUP BY action, dsname, job_name ORDER BY rows DESC LIMIT 60""",
                links=DSN_LINK + JOB_LINK,
            ),
        ],
    )

    cross = dash(
        "smf-cross",
        "SMF Cross Analysis",
        ["smf", "cross", "analytics"],
        [
            table(
                "30 × 80 — job ends vs RACF events",
                0,
                0,
                12,
                12,
                f"""SELECT j.job_name, j.ends, coalesce(p.cpu_timer_sum,0) AS cpu_timer_sum, coalesce(r.events,0) AS racf_events
FROM (
  SELECT job_name, count() AS ends FROM smf.smf_30_5 WHERE {TF} AND job_name!='' GROUP BY job_name
) j
LEFT JOIN (
  SELECT job_name, sum(toUInt64OrZero(cpu_step_time)) AS cpu_timer_sum
  FROM smf.smf_30_4 WHERE {TF} AND job_name!='' GROUP BY job_name
) p USING (job_name)
LEFT JOIN (
  SELECT job_name, count() AS events FROM smf.smf_80 WHERE {TF} AND job_name!='' GROUP BY job_name
) r USING (job_name)
ORDER BY racf_events DESC, ends DESC LIMIT 50""",
                links=JOB_LINK,
            ),
            table(
                "119 × workload — network bytes",
                12,
                0,
                12,
                12,
                f"""SELECT if(resource_name='',as_name,resource_name) AS job_name, count() AS conns,
  sum(toUInt64OrZero(in_bytes)) AS in_bytes, sum(toUInt64OrZero(out_bytes)) AS out_bytes
FROM smf.smf_119_2 WHERE {TF}
GROUP BY job_name ORDER BY (in_bytes+out_bytes) DESC LIMIT 50""",
                links=JOB_LINK,
            ),
        ],
    )

    def var(name, label, query=None, regex=None):
        v = {
            "name": name,
            "label": label,
            "type": "textbox" if query is None else "query",
            "current": {"text": "", "value": ""},
            "options": [],
            "query": query or "",
            "datasource": DS,
            "refresh": 1,
            "hide": 0,
        }
        if regex:
            v["regex"] = regex
        return v

    job_detail = dash(
        "smf-job-detail",
        "SMF Job Detail",
        ["smf", "jobs", "detail"],
        [
            table(
                "Step ends (30-4) — program / step / class / CPU",
                0,
                0,
                24,
                10,
                f"""SELECT
  concat(toString(event_date),' ',if(time='','00:00:00',time)) AS event_ts,
  step_name, program_name, job_class, racf_user,
  cpu_step_time AS cpu_timer, step_comp_code
FROM smf.smf_30_4 WHERE {TF} AND job_name = '$job'
ORDER BY event_date DESC, time DESC LIMIT 200""",
                desc="Primary step/program source. Subtype 5 often blanks these fields.",
            ),
            table(
                "Job ends (30-5)",
                0,
                10,
                12,
                8,
                f"""SELECT
  concat(toString(event_date),' ',if(time='','00:00:00',time)) AS event_ts,
  racf_user, step_comp_code, cpu_step_time AS cpu_timer
FROM smf.smf_30_5 WHERE {TF} AND job_name = '$job'
ORDER BY event_date DESC, time DESC LIMIT 100""",
            ),
            table(
                "Dataset I/O for $job",
                12,
                10,
                12,
                8,
                f"""SELECT 'INPUT' AS direction,
  concat(toString(event_date),' ',if(time='','00:00:00',time)) AS event_ts,
  ddname, if(trim(BOTH ' ' FROM dsname)='','(no dsname)',dsname) AS dsname, volser_1, excp_count
FROM smf.smf_14 WHERE {TF} AND job_name='$job'
UNION ALL
SELECT 'OUTPUT' AS direction,
  concat(toString(event_date),' ',if(time='','00:00:00',time)) AS event_ts,
  ddname, if(trim(BOTH ' ' FROM dsname)='','(no dsname)',dsname) AS dsname, volser_1, excp_count
FROM smf.smf_15 WHERE {TF} AND job_name='$job'
ORDER BY event_ts DESC LIMIT 200""",
            ),
            table(
                "RACF for $job",
                0,
                18,
                24,
                8,
                f"""SELECT
  concat(toString(event_date),' ',if(time='','00:00:00',time)) AS event_ts,
  user_id, event_code, class_name,
  nullIf(old_resource,'') AS old_resource,
  nullIf(access_requested,'') AS access_requested,
  nullIf(access_allowed,'') AS access_allowed
FROM smf.smf_80 WHERE {TF} AND job_name='$job'
ORDER BY event_date DESC, time DESC LIMIT 200""",
                links=USER_LINK,
            ),
        ],
        templating=[var("job", "Job name")],
    )

    dataset_detail = dash(
        "smf-dataset-detail",
        "SMF Dataset Detail",
        ["smf", "dataset", "detail"],
        [
            table(
                "I/O for $dsname",
                0,
                0,
                24,
                10,
                f"""SELECT 'INPUT' AS direction,
  concat(toString(event_date),' ',if(time='','00:00:00',time)) AS event_ts,
  job_name, ddname, volser_1, excp_count
FROM smf.smf_14 WHERE {TF} AND dsname='$dsname'
UNION ALL
SELECT 'OUTPUT' AS direction,
  concat(toString(event_date),' ',if(time='','00:00:00',time)) AS event_ts,
  job_name, ddname, volser_1, excp_count
FROM smf.smf_15 WHERE {TF} AND dsname='$dsname'
ORDER BY event_ts DESC LIMIT 200""",
                links=JOB_LINK,
            ),
            table(
                "Scratches / catalog / RACF",
                0,
                10,
                24,
                10,
                f"""SELECT 'SCRATCH' AS kind,
  concat(toString(event_date),' ',if(time='','00:00:00',time)) AS event_ts,
  job_name, volume_serial AS detail FROM smf.smf_17 WHERE {TF} AND dsname='$dsname'
UNION ALL SELECT 'DEFINE',
  concat(toString(event_date),' ',if(time='','00:00:00',time)),
  job_name, catalog_name FROM smf.smf_61 WHERE {TF} AND entry_name='$dsname'
UNION ALL SELECT 'DELETE',
  concat(toString(event_date),' ',if(time='','00:00:00',time)),
  job_name, catalog_name FROM smf.smf_65 WHERE {TF} AND entry_name='$dsname'
UNION ALL SELECT 'RACF',
  concat(toString(event_date),' ',if(time='','00:00:00',time)),
  job_name, concat(user_id,' EVT',event_code) FROM smf.smf_80 WHERE {TF} AND old_resource='$dsname'
ORDER BY event_ts DESC LIMIT 200""",
                links=JOB_LINK,
            ),
        ],
        templating=[var("dsname", "Dataset name")],
    )

    user_detail = dash(
        "smf-user-detail",
        "SMF User Detail",
        ["smf", "racf", "detail"],
        [
            table(
                "RACF events for $user",
                0,
                0,
                24,
                12,
                f"""SELECT
  concat(toString(event_date),' ',if(time='','00:00:00',time)) AS event_ts,
  date AS smf_date, time AS smf_time,
  job_name, event_code, class_name,
  nullIf(old_resource,'') AS old_resource,
  nullIf(access_requested,'') AS access_requested,
  nullIf(access_allowed,'') AS access_allowed
FROM smf.smf_80 WHERE {TF} AND user_id='$user'
ORDER BY event_date DESC, time DESC LIMIT 300""",
                links=JOB_LINK,
            ),
            table(
                "Jobs for RACF user $user",
                0,
                12,
                24,
                8,
                f"""SELECT job_name, count() AS step_ends, sum(toUInt64OrZero(cpu_step_time)) AS cpu_timer_sum
FROM smf.smf_30_4 WHERE {TF} AND (racf_user='$user' OR user_id_field='$user')
GROUP BY job_name ORDER BY step_ends DESC LIMIT 50""",
                links=JOB_LINK,
            ),
        ],
        templating=[var("user", "RACF user")],
    )

    ip_detail = dash(
        "smf-ip-detail",
        "SMF IP Detail",
        ["smf", "tcp", "detail"],
        [
            table(
                "TCP terminations for $ip",
                0,
                0,
                24,
                14,
                f"""SELECT
  concat(toString(event_date),' ',if(time='','00:00:00',time)) AS event_ts,
  resource_name, as_name, local_ip, local_port, remote_ip, remote_port,
  in_bytes, out_bytes, term_code, connection_id
FROM smf.smf_119_2 WHERE {TF} AND (remote_ip='$ip' OR local_ip='$ip')
ORDER BY event_date DESC, time DESC LIMIT 300""",
                links=JOB_LINK,
            ),
        ],
        templating=[var("ip", "IP address")],
    )

    for obj in (
        overview,
        datasets,
        jobs,
        racf,
        tcp,
        ftp,
        lifecycle,
        cross,
        job_detail,
        dataset_detail,
        user_detail,
        ip_detail,
    ):
        path = OUT / f"{obj['uid']}.json"
        path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
        print("wrote", path.name)


if __name__ == "__main__":
    build_all()
