#!/usr/bin/env bash
# Refresh small Grafana rollup tables from raw SMF tables (last 10 days).
set -euo pipefail

CH_URL="${CH_URL:-http://127.0.0.1:8123}"
CH_USER="${CH_USER:-smf}"
CH_PASSWORD="${CH_PASSWORD:-blacha123}"

q() {
  local tmp code
  tmp="$(mktemp)"
  code="$(
    curl -sS -o "${tmp}" -w "%{http_code}" \
      -u "${CH_USER}:${CH_PASSWORD}" \
      "${CH_URL}/?database=smf" \
      --data-binary "$1"
  )"
  if [[ "${code}" != "200" ]]; then
    echo "ClickHouse HTTP ${code}:" >&2
    cat "${tmp}" >&2
    echo >&2
    rm -f "${tmp}"
    exit 1
  fi
  cat "${tmp}"
  rm -f "${tmp}"
  echo
}

echo "Refreshing stats_* ..."

q "TRUNCATE TABLE IF EXISTS smf.stats_records_daily"
q "
INSERT INTO smf.stats_records_daily
SELECT event_date, 'smf_14', smf_system_id, count() FROM smf.smf_14 WHERE event_date >= today() - 10 GROUP BY event_date, smf_system_id
UNION ALL
SELECT event_date, 'smf_15', smf_system_id, count() FROM smf.smf_15 WHERE event_date >= today() - 10 GROUP BY event_date, smf_system_id
UNION ALL
SELECT event_date, 'smf_17', smf_system_id, count() FROM smf.smf_17 WHERE event_date >= today() - 10 GROUP BY event_date, smf_system_id
UNION ALL
SELECT event_date, 'smf_80', smf_system_id, count() FROM smf.smf_80 WHERE event_date >= today() - 10 GROUP BY event_date, smf_system_id
UNION ALL
SELECT event_date, 'smf_119_1', smf_system_id, count() FROM smf.smf_119_1 WHERE event_date >= today() - 10 GROUP BY event_date, smf_system_id
UNION ALL
SELECT event_date, 'smf_119_2', smf_system_id, count() FROM smf.smf_119_2 WHERE event_date >= today() - 10 GROUP BY event_date, smf_system_id
UNION ALL
SELECT event_date, 'smf_119_3', smf_system_id, count() FROM smf.smf_119_3 WHERE event_date >= today() - 10 GROUP BY event_date, smf_system_id
UNION ALL
SELECT event_date, 'smf_119_70', smf_system_id, count() FROM smf.smf_119_70 WHERE event_date >= today() - 10 GROUP BY event_date, smf_system_id
UNION ALL
SELECT event_date, 'smf_30_4', smf_system_id, count() FROM smf.smf_30_4 WHERE event_date >= today() - 10 GROUP BY event_date, smf_system_id
UNION ALL
SELECT event_date, 'smf_30_5', smf_system_id, count() FROM smf.smf_30_5 WHERE event_date >= today() - 10 GROUP BY event_date, smf_system_id
UNION ALL
SELECT event_date, 'smf_92_10', smf_system_id, count() FROM smf.smf_92_10 WHERE event_date >= today() - 10 GROUP BY event_date, smf_system_id
UNION ALL
SELECT event_date, 'smf_92_11', smf_system_id, count() FROM smf.smf_92_11 WHERE event_date >= today() - 10 GROUP BY event_date, smf_system_id
UNION ALL
SELECT event_date, 'smf_92_14', smf_system_id, count() FROM smf.smf_92_14 WHERE event_date >= today() - 10 GROUP BY event_date, smf_system_id
UNION ALL
SELECT event_date, 'smf_92_17', smf_system_id, count() FROM smf.smf_92_17 WHERE event_date >= today() - 10 GROUP BY event_date, smf_system_id
"

q "TRUNCATE TABLE IF EXISTS smf.stats_tcp_hourly"
q "
INSERT INTO smf.stats_tcp_hourly
SELECT
  toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date), ' ', nullIf(time, '')))) AS hour,
  smf_system_id,
  tcp_stack,
  count() AS conn_count,
  sum(toUInt64OrZero(in_bytes)) AS in_bytes,
  sum(toUInt64OrZero(out_bytes)) AS out_bytes
FROM smf.smf_119_2
WHERE event_date >= today() - 10
GROUP BY hour, smf_system_id, tcp_stack
"

q "TRUNCATE TABLE IF EXISTS smf.stats_dataset_daily"
q "
INSERT INTO smf.stats_dataset_daily
SELECT event_date, smf_system_id, 'INPUT', job_name, dsname, count(), sum(toUInt64OrZero(excp_count))
FROM smf.smf_14 WHERE event_date >= today() - 10
GROUP BY event_date, smf_system_id, job_name, dsname
UNION ALL
SELECT event_date, smf_system_id, 'OUTPUT', job_name, dsname, count(), sum(toUInt64OrZero(excp_count))
FROM smf.smf_15 WHERE event_date >= today() - 10
GROUP BY event_date, smf_system_id, job_name, dsname
"

q "TRUNCATE TABLE IF EXISTS smf.stats_racf_daily"
q "
INSERT INTO smf.stats_racf_daily
SELECT event_date, smf_system_id, event_code, user_id, job_name, count()
FROM smf.smf_80
WHERE event_date >= today() - 10
GROUP BY event_date, smf_system_id, event_code, user_id, job_name
"

q "TRUNCATE TABLE IF EXISTS smf.stats_ftp_daily"
q "
INSERT INTO smf.stats_ftp_daily
SELECT event_date, smf_system_id, 'CLIENT', local_user, sum(toUInt64OrZero(bytes_transferred)), count()
FROM smf.smf_119_3 WHERE event_date >= today() - 10
GROUP BY event_date, smf_system_id, local_user
UNION ALL
SELECT event_date, smf_system_id, 'SERVER', server_user, sum(toUInt64OrZero(bytes_transferred)), count()
FROM smf.smf_119_70 WHERE event_date >= today() - 10
GROUP BY event_date, smf_system_id, server_user
"

q "TRUNCATE TABLE IF EXISTS smf.stats_jobs_daily"
q "
INSERT INTO smf.stats_jobs_daily
SELECT event_date, smf_system_id, smf_subtype, job_name, count()
FROM smf.smf_30_5
WHERE event_date >= today() - 10
GROUP BY event_date, smf_system_id, smf_subtype, job_name
"

q "TRUNCATE TABLE IF EXISTS smf.stats_uss_hourly"
q "
INSERT INTO smf.stats_uss_hourly
SELECT hour, smf_system_id, action, sum(cnt) FROM (
  SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date), ' ', nullIf(time, '')))) AS hour,
         smf_system_id, 'OPEN-10' AS action, count() AS cnt
  FROM smf.smf_92_10 WHERE event_date >= today() - 10 GROUP BY hour, smf_system_id
  UNION ALL
  SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date), ' ', nullIf(time, '')))) AS hour,
         smf_system_id, 'CLOSE-11' AS action, count() AS cnt
  FROM smf.smf_92_11 WHERE event_date >= today() - 10 GROUP BY hour, smf_system_id
  UNION ALL
  SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date), ' ', nullIf(time, '')))) AS hour,
         smf_system_id, 'ACCESS-17' AS action, count() AS cnt
  FROM smf.smf_92_17 WHERE event_date >= today() - 10 GROUP BY hour, smf_system_id
  UNION ALL
  SELECT toStartOfHour(parseDateTimeBestEffort(concat(toString(event_date), ' ', nullIf(time, '')))) AS hour,
         smf_system_id, 'DELETE-14' AS action, count() AS cnt
  FROM smf.smf_92_14 WHERE event_date >= today() - 10 GROUP BY hour, smf_system_id
) GROUP BY hour, smf_system_id, action
"

q "TRUNCATE TABLE IF EXISTS smf.stats_uss_path_daily"
q "
INSERT INTO smf.stats_uss_path_daily
SELECT event_date, smf_system_id, pathname, job_name,
       count() AS close_count,
       sum(toUInt64OrZero(bytes_read)) AS bytes_read,
       sum(toUInt64OrZero(bytes_written)) AS bytes_written
FROM smf.smf_92_11
WHERE event_date >= today() - 10 AND pathname != ''
GROUP BY event_date, smf_system_id, pathname, job_name
"

echo "stats refresh done."
