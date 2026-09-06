#!/usr/bin/env bash
# Load every smf_*.csv from a directory into matching ClickHouse tables.
# Usage: ./load_all.sh [csv_dir]
set -euo pipefail

CSV_DIR="${1:-$(cd "$(dirname "$0")/.." && pwd)/data/csv}"
CH_URL="${CH_URL:-http://127.0.0.1:8123}"
CH_USER="${CH_USER:-smf}"
CH_PASSWORD="${CH_PASSWORD:-blacha123}"
CH_DB="${CH_DB:-smf}"
CH_CONTAINER="${CH_CONTAINER:-smf-clickhouse}"
# Seconds — large CSVs (e.g. smf_92_*) need more than the 30s HTTP default.
CH_TIMEOUT="${CH_TIMEOUT:-600}"

if [[ ! -d "${CSV_DIR}" ]]; then
  echo "CSV directory not found: ${CSV_DIR}" >&2
  exit 1
fi

shopt -s nullglob
files=("${CSV_DIR}"/smf_*.csv)
if [[ ${#files[@]} -eq 0 ]]; then
  echo "No smf_*.csv files in ${CSV_DIR}" >&2
  exit 1
fi

USE_DOCKER=0
if command -v docker >/dev/null 2>&1 && docker ps --format '{{.Names}}' | grep -qx "${CH_CONTAINER}"; then
  USE_DOCKER=1
  echo "Load mode: docker exec ${CH_CONTAINER} (timeout ${CH_TIMEOUT}s)"
else
  echo "Load mode: HTTP ${CH_URL} (timeout ${CH_TIMEOUT}s)"
fi

load_one_docker() {
  local table="$1" file="$2"
  docker exec -i \
    -e "CLICKHOUSE_USER=${CH_USER}" \
    -e "CLICKHOUSE_PASSWORD=${CH_PASSWORD}" \
    "${CH_CONTAINER}" \
    clickhouse-client \
      --user "${CH_USER}" \
      --password="${CH_PASSWORD}" \
      --receive_timeout "${CH_TIMEOUT}" \
      --send_timeout "${CH_TIMEOUT}" \
      --database "${CH_DB}" \
      --query "INSERT INTO ${table} FORMAT CSVWithNames SETTINGS input_format_parallel_parsing=0, max_execution_time=${CH_TIMEOUT}, input_format_skip_unknown_fields=1" \
    < "${file}"
}

load_one_http() {
  local table="$1" file="$2"
  local tmp code
  tmp="$(mktemp)"
  code="$(
    curl -sS -o "${tmp}" -w "%{http_code}" \
      --max-time "${CH_TIMEOUT}" \
      -u "${CH_USER}:${CH_PASSWORD}" \
      "${CH_URL}/?database=${CH_DB}&input_format_skip_unknown_fields=1&input_format_parallel_parsing=0&receive_timeout=${CH_TIMEOUT}&send_timeout=${CH_TIMEOUT}&http_receive_timeout=${CH_TIMEOUT}&max_execution_time=${CH_TIMEOUT}&query=INSERT%20INTO%20${table}%20FORMAT%20CSVWithNames" \
      --data-binary @"${file}"
  )"
  if [[ "${code}" != "200" ]]; then
    echo "ClickHouse HTTP ${code} loading ${table}:" >&2
    cat "${tmp}" >&2
    echo >&2
    rm -f "${tmp}"
    return 1
  fi
  rm -f "${tmp}"
}

loaded=0
failed=0
for f in "${files[@]}"; do
  base="$(basename "${f}" .csv)"
  bytes="$(wc -c < "${f}" | tr -d ' ')"
  echo "Loading ${f} → ${CH_DB}.${base} (${bytes} bytes)"
  if [[ "${USE_DOCKER}" -eq 1 ]]; then
    if ! load_one_docker "${base}" "${f}"; then
      echo "WARN: docker load failed for ${base}, trying HTTP ..." >&2
      if ! load_one_http "${base}" "${f}"; then
        failed=$((failed + 1))
        continue
      fi
    fi
  else
    if ! load_one_http "${base}" "${f}"; then
      failed=$((failed + 1))
      continue
    fi
  fi
  loaded=$((loaded + 1))
done

echo "Loaded ${loaded} file(s) from ${CSV_DIR}"
if [[ "${failed}" -gt 0 ]]; then
  echo "Failed: ${failed} file(s)" >&2
  exit 1
fi
