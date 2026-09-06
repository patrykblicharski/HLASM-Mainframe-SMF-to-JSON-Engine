#!/usr/bin/env python3
import json, urllib.request, base64

CH = "http://192.168.0.141:8123/?database=smf"
auth = base64.b64encode(b"smf:blacha123").decode()


def ch(sql: str):
    body = (sql.strip().rstrip(";") + " FORMAT JSON").encode()
    req = urllib.request.Request(CH, data=body, method="POST")
    req.add_header("Authorization", "Basic " + auth)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return True, json.loads(r.read().decode())
    except Exception as e:
        err = getattr(e, "read", lambda: b"")()
        return False, (err.decode(errors="replace")[:500] if err else str(e))


h = (
    "toStartOfHour(parseDateTimeBestEffort("
    "concat(toString(event_date),' ',if(time='','00:00:00',time))))"
)
tf = "event_date >= today()-4"
q = f"""
SELECT hour AS time, series, sum(cnt) AS value FROM (
  SELECT {h} AS hour, 'INPUT-14' AS series, count() AS cnt FROM smf.smf_14 WHERE {tf} GROUP BY hour
  UNION ALL SELECT {h} AS hour, 'OUTPUT-15' AS series, count() AS cnt FROM smf.smf_15 WHERE {tf} GROUP BY hour
  UNION ALL SELECT {h} AS hour, 'RACF-80' AS series, count() AS cnt FROM smf.smf_80 WHERE {tf} GROUP BY hour
) GROUP BY time, series ORDER BY time LIMIT 5
"""
ok, data = ch(q)
print("HOURLY", ok, data.get("data", data)[:3] if ok else data)

q2 = f"""
SELECT e.job_name, e.ends, coalesce(p.with_program,0) AS with_program, coalesce(p.cpu_timer_sum,0) AS cpu_timer_sum
FROM (SELECT job_name, count() AS ends FROM smf.smf_30_5 WHERE {tf} AND job_name!='' GROUP BY job_name) e
LEFT JOIN (
  SELECT job_name, countIf(program_name!='') AS with_program,
         sum(toUInt64OrZero(cpu_step_time)) AS cpu_timer_sum
  FROM smf.smf_30_4 WHERE {tf} AND job_name!='' GROUP BY job_name
) p USING (job_name)
ORDER BY e.ends DESC LIMIT 3
"""
ok2, data2 = ch(q2)
print("JOBS", ok2, data2.get("data", data2) if ok2 else data2)

# Confirm overview JSON no longer has broken UNION without AS hour
from pathlib import Path
overview = Path(__file__).resolve().parents[1] / "grafana" / "dashboards" / "smf-overview.json"
raw = overview.read_text(encoding="utf-8")
bad = "GROUP BY hour\\n  UNION ALL SELECT toStartOfHour" in raw or "', count() FROM" in raw
print("OVERVIEW_HAS_BAD_UNION_PATTERN", bad)
# All UNION branches should contain AS hour
print("AS_hour_count", raw.count("AS hour"))
