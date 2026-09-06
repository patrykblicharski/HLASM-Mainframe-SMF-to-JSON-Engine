#!/usr/bin/env python3
"""Generate polished Grafana SMF dashboards (default range now-4d)."""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "grafana" / "dashboards"
DS = {"type": "grafana-clickhouse-datasource", "uid": "clickhouse_smf"}


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
    return panel_base(
        title,
        "stat",
        x,
        y,
        w,
        h,
        sql,
        options={"colorMode": "background", "graphMode": "area", "textMode": "value_and_name"},
        fieldConfig={
            "defaults": {
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "semi-dark-blue", "value": None},
                        {"color": color, "value": 0},
                    ],
                }
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


def bargauge(title, x, y, w, h, sql):
    return panel_base(
        title,
        "bargauge",
        x,
        y,
        w,
        h,
        sql,
        options={"orientation": "horizontal", "displayMode": "gradient", "showUnfilled": True},
        fieldConfig={
            "defaults": {
                "color": {"mode": "palette-classic"},
                "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]},
            },
            "overrides": [],
        },
    )


def pie(title, x, y, w, h, sql):
    return panel_base(
        title,
        "piechart",
        x,
        y,
        w,
        h,
        sql,
        options={
            "legend": {"displayMode": "table", "placement": "right", "values": ["value", "percent"]},
            "pieType": "donut",
            "reduceOptions": {"calcs": ["lastNotNull"]},
        },
        fieldConfig={"defaults": {"color": {"mode": "palette-classic"}}, "overrides": []},
    )


def dash(uid, title, tags, panels, templating=None, links=None):
    return {
        "annotations": {"list": []},
        "editable": true if False else True,
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
        "version": 3,
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

    overview = dash(
        "smf-overview",
        "SMF Overview",
        ["smf", "overview"],
        [
            stat("Total rows (stats)", 0, 0, 4, 4, "SELECT sum(row_count) FROM smf.stats_records_daily WHERE event_date >= today()-4", "teal"),
            stat("Distinct days", 4, 0, 4, 4, "SELECT countDistinct(event_date) FROM smf.stats_records_daily", "purple"),
            stat("INPUT 14", 8, 0, 4, 4, "SELECT count() FROM smf.smf_14 WHERE event_date >= today()-4", "green"),
            stat("RACF 80", 12, 0, 4, 4, "SELECT count() FROM smf.smf_80 WHERE event_date >= today()-4", "red"),
            stat("TCP 119-2", 16, 0, 4, 4, "SELECT count() FROM smf.smf_119_2 WHERE event_date >= today()-4", "blue"),
            stat("Jobs 30-5", 20, 0, 4, 4, "SELECT count() FROM smf.smf_30_5 WHERE event_date >= today()-4", "orange"),
            timeseries(
                "Hourly pulse (multi-type)",
                0,
                4,
                16,
                9,
                """SELECT hour AS time, source, sum(cnt) AS rows FROM (
  SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,'INPUT-14' AS source,count() AS cnt FROM smf.smf_14 WHERE event_date>=today()-4 GROUP BY hour
  UNION ALL SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))), 'OUTPUT-15', count() FROM smf.smf_15 WHERE event_date>=today()-4 GROUP BY hour
  UNION ALL SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))), 'RACF-80', count() FROM smf.smf_80 WHERE event_date>=today()-4 GROUP BY hour
  UNION ALL SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))), 'TCP-119-2', count() FROM smf.smf_119_2 WHERE event_date>=today()-4 GROUP BY hour
  UNION ALL SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))), 'JOB-30-5', count() FROM smf.smf_30_5 WHERE event_date>=today()-4 GROUP BY hour
) GROUP BY time, source ORDER BY time""",
                bars=True,
                stacking="normal",
                desc="Works well when the dump is concentrated on one calendar day.",
            ),
            pie(
                "Rows by table",
                16,
                4,
                8,
                9,
                "SELECT table_name, sum(row_count) AS rows FROM smf.stats_records_daily WHERE event_date>=today()-4 GROUP BY table_name ORDER BY rows DESC LIMIT 12",
            ),
            bargauge(
                "Top systems",
                0,
                13,
                12,
                8,
                "SELECT smf_system_id, sum(row_count) AS rows FROM smf.stats_records_daily WHERE event_date>=today()-4 GROUP BY smf_system_id ORDER BY rows DESC",
            ),
            table(
                "Daily / table / system",
                12,
                13,
                12,
                8,
                "SELECT event_date, table_name, smf_system_id, sum(row_count) AS rows FROM smf.stats_records_daily WHERE event_date>=today()-4 GROUP BY event_date, table_name, smf_system_id ORDER BY rows DESC LIMIT 200",
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
                """SELECT hour AS time, direction, sum(cnt) AS rows FROM (
  SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,'INPUT' AS direction,count() AS cnt FROM smf.smf_14 WHERE event_date>=today()-4 GROUP BY hour
  UNION ALL SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))),'OUTPUT',count() FROM smf.smf_15 WHERE event_date>=today()-4 GROUP BY hour
  UNION ALL SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))),'SCRATCH',count() FROM smf.smf_17 WHERE event_date>=today()-4 GROUP BY hour
) GROUP BY time, direction ORDER BY time""",
                bars=True,
                stacking="normal",
            ),
            pie(
                "INPUT vs OUTPUT vs SCRATCH",
                16,
                0,
                8,
                8,
                """SELECT direction, sum(c) AS rows FROM (
  SELECT 'INPUT' AS direction, count() AS c FROM smf.smf_14 WHERE event_date>=today()-4
  UNION ALL SELECT 'OUTPUT', count() FROM smf.smf_15 WHERE event_date>=today()-4
  UNION ALL SELECT 'SCRATCH', count() FROM smf.smf_17 WHERE event_date>=today()-4
) GROUP BY direction""",
            ),
            table(
                "Top datasets (blank JFCB shown as empty — not ???????)",
                0,
                8,
                24,
                10,
                """SELECT direction, job_name,
  if(dsname = '' OR match(dsname, '^[\\\\x00-\\\\x1f\\\\x7f-\\\\x9f\\\\x{fffd}?]+$'), concat('(no dsname) ', volser), dsname) AS dsname_display,
  if(dsname = '' OR match(dsname, '^[\\\\x00-\\\\x1f\\\\x7f-\\\\x9f\\\\x{fffd}?]+$'), '', dsname) AS dsname,
  volser, sum(rows) AS rows, sum(excp) AS excp
FROM (
  SELECT 'INPUT' AS direction, job_name, trim(BOTH ' ' FROM dsname) AS dsname, volser_1 AS volser, count() AS rows, sum(toUInt64OrZero(excp_count)) AS excp
  FROM smf.smf_14 WHERE event_date>=today()-4 GROUP BY job_name, dsname, volser
  UNION ALL
  SELECT 'OUTPUT', job_name, trim(BOTH ' ' FROM dsname), volser_1, count(), sum(toUInt64OrZero(excp_count))
  FROM smf.smf_15 WHERE event_date>=today()-4 GROUP BY job_name, dsname, volser
)
GROUP BY direction, job_name, dsname_display, dsname, volser
ORDER BY rows DESC LIMIT 60""",
                links=DSN_LINK + JOB_LINK,
                desc="Control-byte JFCB fills (EBCDIC x'04') are blanked at export; Grafana no longer maps them to ???.",
            ),
            table(
                "Top scratches",
                0,
                18,
                24,
                8,
                """SELECT job_name,
  if(trim(BOTH ' ' FROM dsname)='','(no dsname)', dsname) AS dsname_display,
  if(trim(BOTH ' ' FROM dsname)='','', dsname) AS dsname,
  volume_serial AS volser, count() AS rows
FROM smf.smf_17 WHERE event_date>=today()-4
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
                """SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS time, count() AS ends
FROM smf.smf_30_5 WHERE event_date>=today()-4 GROUP BY time ORDER BY time""",
                bars=True,
            ),
            pie(
                "Job class mix",
                12,
                0,
                12,
                8,
                """SELECT if(job_class='','(blank)',job_class) AS job_class, count() AS rows
FROM smf.smf_30_5 WHERE event_date>=today()-4 GROUP BY job_class ORDER BY rows DESC LIMIT 15""",
            ),
            table(
                "Top jobs",
                0,
                8,
                12,
                10,
                """SELECT job_name, count() AS ends, countIf(program_name!='') AS with_program,
  sum(toUInt64OrZero(cpu_step_time)) AS cpu_sum
FROM smf.smf_30_5 WHERE event_date>=today()-4 AND job_name!=''
GROUP BY job_name ORDER BY ends DESC LIMIT 40""",
                links=JOB_LINK,
            ),
            table(
                "Programs / steps (non-empty only)",
                12,
                8,
                12,
                10,
                """SELECT nullIf(program_name,'') AS program_name, nullIf(step_name,'') AS step_name, count() AS rows
FROM smf.smf_30_5 WHERE event_date>=today()-4 AND (program_name!='' OR step_name!='')
GROUP BY program_name, step_name ORDER BY rows DESC LIMIT 40""",
                desc="Many dumps leave step/program blank — do not invent values.",
            ),
            bargauge(
                "CPU sum by job (top 15)",
                0,
                18,
                24,
                8,
                """SELECT job_name, sum(toUInt64OrZero(cpu_step_time)) AS cpu_sum
FROM smf.smf_30_5 WHERE event_date>=today()-4 AND job_name!=''
GROUP BY job_name ORDER BY cpu_sum DESC LIMIT 15""",
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
                """SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS time,
  count() AS events, countIf(event_code='1') AS failed_logon
FROM smf.smf_80 WHERE event_date>=today()-4 GROUP BY time ORDER BY time""",
                bars=False,
            ),
            pie(
                "Event codes",
                16,
                0,
                8,
                8,
                "SELECT event_code, count() AS events FROM smf.smf_80 WHERE event_date>=today()-4 GROUP BY event_code ORDER BY events DESC LIMIT 12",
            ),
            table(
                "Top users",
                0,
                8,
                8,
                9,
                "SELECT user_id, count() AS events FROM smf.smf_80 WHERE event_date>=today()-4 AND user_id!='' GROUP BY user_id ORDER BY events DESC LIMIT 40",
                links=USER_LINK,
            ),
            table(
                "Top jobs",
                8,
                8,
                8,
                9,
                "SELECT job_name, count() AS events FROM smf.smf_80 WHERE event_date>=today()-4 AND job_name!='' GROUP BY job_name ORDER BY events DESC LIMIT 40",
                links=JOB_LINK,
            ),
            pie(
                "Class mix",
                16,
                8,
                8,
                9,
                "SELECT if(class_name='','(blank)',class_name) AS class_name, count() AS events FROM smf.smf_80 WHERE event_date>=today()-4 GROUP BY class_name ORDER BY events DESC LIMIT 12",
            ),
            table(
                "Recent events",
                0,
                17,
                24,
                9,
                """SELECT event_date, time, user_id, job_name, event_code, class_name, old_resource, access_requested, access_allowed
FROM smf.smf_80 WHERE event_date>=today()-4
ORDER BY event_date DESC, time DESC LIMIT 100""",
                links=USER_LINK + JOB_LINK,
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
                "SELECT hour AS time, sum(conn_count) AS connections FROM smf.stats_tcp_hourly WHERE toDate(hour)>=today()-4 GROUP BY hour ORDER BY time",
            ),
            timeseries(
                "Bytes in/out / hour",
                12,
                0,
                12,
                8,
                "SELECT hour AS time, sum(in_bytes) AS in_bytes, sum(out_bytes) AS out_bytes FROM smf.stats_tcp_hourly WHERE toDate(hour)>=today()-4 GROUP BY hour ORDER BY time",
                unit="decbytes",
            ),
            table(
                "Top remote IPs",
                0,
                8,
                12,
                10,
                """SELECT remote_ip, count() AS conns, sum(toUInt64OrZero(in_bytes)) AS in_bytes, sum(toUInt64OrZero(out_bytes)) AS out_bytes
FROM smf.smf_119_2 WHERE event_date>=today()-4 AND remote_ip!=''
GROUP BY remote_ip ORDER BY conns DESC LIMIT 40""",
                links=IP_LINK,
            ),
            pie(
                "Termination codes",
                12,
                8,
                12,
                10,
                "SELECT if(term_code='','(blank)',term_code) AS term_code, count() AS conns FROM smf.smf_119_2 WHERE event_date>=today()-4 GROUP BY term_code ORDER BY conns DESC LIMIT 15",
            ),
            table(
                "Local ports (119-1)",
                0,
                18,
                12,
                8,
                "SELECT local_port, count() AS conns FROM smf.smf_119_1 WHERE event_date>=today()-4 AND local_port!='' GROUP BY local_port ORDER BY conns DESC LIMIT 40",
            ),
            table(
                "Top workloads (resource/AS)",
                12,
                18,
                12,
                8,
                """SELECT if(resource_name='',as_name,resource_name) AS job_name, count() AS conns,
  sum(toUInt64OrZero(in_bytes)+toUInt64OrZero(out_bytes)) AS bytes
FROM smf.smf_119_2 WHERE event_date>=today()-4
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
            stat("Client 119-3", 0, 0, 6, 4, "SELECT count() FROM smf.smf_119_3 WHERE event_date>=today()-4", "teal"),
            stat("Server 119-70", 6, 0, 6, 4, "SELECT count() FROM smf.smf_119_70 WHERE event_date>=today()-4", "blue"),
            stat("Fail 119-72", 12, 0, 6, 4, "SELECT count() FROM smf.smf_119_72 WHERE event_date>=today()-4", "red"),
            stat(
                "FTP status",
                18,
                0,
                6,
                4,
                "SELECT if((SELECT count() FROM smf.smf_119_3)+(SELECT count() FROM smf.smf_119_70)=0, 0, 1)",
                "orange",
            ),
            timeseries(
                "FTP bytes / day",
                0,
                4,
                12,
                8,
                "SELECT toDateTime(event_date) AS time, direction, sum(bytes_sum) AS bytes FROM smf.stats_ftp_daily WHERE event_date>=today()-4 GROUP BY time, direction ORDER BY time",
                bars=True,
                unit="decbytes",
                desc="Empty when dump has no subtype 3/70.",
            ),
            table(
                "Available 119 subtypes (context when FTP empty)",
                12,
                4,
                12,
                8,
                """SELECT '119-1' AS table, count() AS rows FROM smf.smf_119_1
UNION ALL SELECT '119-2', count() FROM smf.smf_119_2
UNION ALL SELECT '119-5', count() FROM smf.smf_119_5
UNION ALL SELECT '119-6', count() FROM smf.smf_119_6
UNION ALL SELECT '119-10', count() FROM smf.smf_119_10
UNION ALL SELECT '119-3', count() FROM smf.smf_119_3
UNION ALL SELECT '119-70', count() FROM smf.smf_119_70""",
            ),
            table(
                "Top FTP users",
                0,
                12,
                24,
                9,
                "SELECT direction, local_user, sum(bytes_sum) AS bytes, sum(xfer_count) AS transfers FROM smf.stats_ftp_daily WHERE event_date>=today()-4 GROUP BY direction, local_user ORDER BY bytes DESC LIMIT 50",
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
                """SELECT hour AS time, action, sum(cnt) AS rows FROM (
  SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))) AS hour,'DEFINE-61' AS action,count() AS cnt FROM smf.smf_61 WHERE event_date>=today()-4 GROUP BY hour
  UNION ALL SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))),'DELETE-65',count() FROM smf.smf_65 WHERE event_date>=today()-4 GROUP BY hour
  UNION ALL SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))),'ALTER-66',count() FROM smf.smf_66 WHERE event_date>=today()-4 GROUP BY hour
  UNION ALL SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date),' ',if(time='','00:00:00',time)))),'SCRATCH-17',count() FROM smf.smf_17 WHERE event_date>=today()-4 GROUP BY hour
) GROUP BY time, action ORDER BY time""",
                bars=True,
                stacking="normal",
            ),
            pie(
                "Action mix",
                16,
                0,
                8,
                9,
                """SELECT action, sum(c) AS rows FROM (
  SELECT 'DEFINE' AS action, count() AS c FROM smf.smf_61 WHERE event_date>=today()-4
  UNION ALL SELECT 'DELETE', count() FROM smf.smf_65 WHERE event_date>=today()-4
  UNION ALL SELECT 'ALTER', count() FROM smf.smf_66 WHERE event_date>=today()-4
  UNION ALL SELECT 'SCRATCH', count() FROM smf.smf_17 WHERE event_date>=today()-4
) GROUP BY action""",
            ),
            table(
                "Top catalog entries",
                0,
                9,
                24,
                10,
                """SELECT action, entry_name AS dsname, job_name, count() AS rows FROM (
  SELECT 'DEFINE' AS action, entry_name, job_name FROM smf.smf_61 WHERE event_date>=today()-4
  UNION ALL SELECT 'DELETE', entry_name, job_name FROM smf.smf_65 WHERE event_date>=today()-4
  UNION ALL SELECT 'ALTER', entry_name, job_name FROM smf.smf_66 WHERE event_date>=today()-4
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
                """SELECT j.job_name, j.ends, j.cpu_sum, coalesce(r.events,0) AS racf_events
FROM (
  SELECT job_name, count() AS ends, sum(toUInt64OrZero(cpu_step_time)) AS cpu_sum
  FROM smf.smf_30_5 WHERE event_date>=today()-4 AND job_name!='' GROUP BY job_name
) j
LEFT JOIN (
  SELECT job_name, count() AS events FROM smf.smf_80 WHERE event_date>=today()-4 AND job_name!='' GROUP BY job_name
) r USING (job_name)
ORDER BY racf_events DESC, ends DESC LIMIT 50""",
                links=JOB_LINK,
                desc="ANALYTICS.md priority cross #1",
            ),
            table(
                "119 × workload — network bytes",
                12,
                0,
                12,
                12,
                """SELECT if(resource_name='',as_name,resource_name) AS job_name, count() AS conns,
  sum(toUInt64OrZero(in_bytes)) AS in_bytes, sum(toUInt64OrZero(out_bytes)) AS out_bytes
FROM smf.smf_119_2 WHERE event_date>=today()-4
GROUP BY job_name ORDER BY (in_bytes+out_bytes) DESC LIMIT 50""",
                links=JOB_LINK,
                desc="ANALYTICS.md priority cross #2",
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
                "30-5 ends for $job",
                0,
                0,
                24,
                10,
                """SELECT event_date, time, step_name, program_name, job_class, racf_user, cpu_step_time, step_comp_code
FROM smf.smf_30_5 WHERE event_date>=today()-4 AND job_name = '$job'
ORDER BY event_date DESC, time DESC LIMIT 200""",
            ),
            table(
                "Dataset I/O for $job",
                0,
                10,
                12,
                10,
                """SELECT 'INPUT' AS direction, event_date, time, ddname,
  if(trim(BOTH ' ' FROM dsname)='','(no dsname)',dsname) AS dsname, volser_1, excp_count
FROM smf.smf_14 WHERE event_date>=today()-4 AND job_name='$job'
UNION ALL
SELECT 'OUTPUT', event_date, time, ddname, if(trim(BOTH ' ' FROM dsname)='','(no dsname)',dsname), volser_1, excp_count
FROM smf.smf_15 WHERE event_date>=today()-4 AND job_name='$job'
ORDER BY event_date DESC, time DESC LIMIT 200""",
            ),
            table(
                "RACF for $job",
                12,
                10,
                12,
                10,
                """SELECT event_date, time, user_id, event_code, class_name, old_resource, access_requested, access_allowed
FROM smf.smf_80 WHERE event_date>=today()-4 AND job_name='$job'
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
                """SELECT 'INPUT' AS direction, event_date, time, job_name, ddname, volser_1, excp_count
FROM smf.smf_14 WHERE event_date>=today()-4 AND dsname='$dsname'
UNION ALL
SELECT 'OUTPUT', event_date, time, job_name, ddname, volser_1, excp_count
FROM smf.smf_15 WHERE event_date>=today()-4 AND dsname='$dsname'
ORDER BY event_date DESC, time DESC LIMIT 200""",
                links=JOB_LINK,
            ),
            table(
                "Scratches / catalog / RACF",
                0,
                10,
                24,
                10,
                """SELECT 'SCRATCH' AS kind, event_date, time, job_name, volume_serial AS detail FROM smf.smf_17 WHERE event_date>=today()-4 AND dsname='$dsname'
UNION ALL SELECT 'DEFINE', event_date, time, job_name, catalog_name FROM smf.smf_61 WHERE event_date>=today()-4 AND entry_name='$dsname'
UNION ALL SELECT 'DELETE', event_date, time, job_name, catalog_name FROM smf.smf_65 WHERE event_date>=today()-4 AND entry_name='$dsname'
UNION ALL SELECT 'RACF', event_date, time, job_name, concat(user_id,' EVT',event_code) FROM smf.smf_80 WHERE event_date>=today()-4 AND old_resource='$dsname'
ORDER BY event_date DESC, time DESC LIMIT 200""",
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
                """SELECT event_date, time, job_name, event_code, class_name, old_resource, access_requested, access_allowed
FROM smf.smf_80 WHERE event_date>=today()-4 AND user_id='$user'
ORDER BY event_date DESC, time DESC LIMIT 300""",
                links=JOB_LINK,
            ),
            table(
                "Jobs for RACF user $user (30)",
                0,
                12,
                24,
                8,
                """SELECT job_name, count() AS ends, sum(toUInt64OrZero(cpu_step_time)) AS cpu_sum
FROM smf.smf_30_5 WHERE event_date>=today()-4 AND (racf_user='$user' OR user_id_field='$user')
GROUP BY job_name ORDER BY ends DESC LIMIT 50""",
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
                """SELECT event_date, time, resource_name, as_name, local_ip, local_port, remote_ip, remote_port,
  in_bytes, out_bytes, term_code, connection_id
FROM smf.smf_119_2 WHERE event_date>=today()-4 AND (remote_ip='$ip' OR local_ip='$ip')
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
