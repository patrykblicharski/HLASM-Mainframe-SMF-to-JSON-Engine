#!/usr/bin/env bash
# Load every smf_*.csv from a directory into matching ClickHouse tables.
# Usage: ./load_all.sh [csv_dir]
#
# Prefers docker exec + clickhouse-client (avoids HTTP 30s body-read timeout).
#   CH_TIMEOUT=1200 ./scripts/load_all.sh ./data/csv
#   LOAD_MODE=docker|http|auto  (default auto)
set -euo pipefail

CSV_DIR="${1:-$(cd "$(dirname "$0")/.." && pwd)/data/csv}"
CH_URL="${CH_URL:-http://127.0.0.1:8123}"
CH_USER="${CH_USER:-smf}"
CH_PASSWORD="${CH_PASSWORD:-blacha123}"
CH_DB="${CH_DB:-smf}"
CH_CONTAINER="${CH_CONTAINER:-smf-clickhouse}"
CH_TIMEOUT="${CH_TIMEOUT:-600}"
LOAD_MODE="${LOAD_MODE:-auto}"   # auto | docker | http

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

resolve_container() {
  if ! command -v docker >/dev/null 2>&1; then
    return 1
  fi
  if docker inspect -f '{{.State.Running}}' "${CH_CONTAINER}" 2>/dev/null | grep -qx true; then
    echo "${CH_CONTAINER}"
    return 0
  fi
  local found
  found="$(docker ps --format '{{.Names}}' | grep -E 'clickhouse' | grep -v init | head -n1 || true)"
  if [[ -n "${found}" ]]; then
    echo "${found}"
    return 0
  fi
  return 1
}

CONTAINER_ID=""
MODE="http"
if [[ "${LOAD_MODE}" == "http" ]]; then
  MODE="http"
elif [[ "${LOAD_MODE}" == "docker" ]]; then
  CONTAINER_ID="$(resolve_container)" || {
    echo "LOAD_MODE=docker but no running ClickHouse container found" >&2
    exit 1
  }
  MODE="docker"
else
  if CONTAINER_ID="$(resolve_container)"; then
    MODE="docker"
  else
    MODE="http"
  fi
fi

echo "load_all.sh mode=${MODE} timeout=${CH_TIMEOUT}s files=${#files[@]}"
if [[ "${MODE}" == "docker" ]]; then
  echo "container=${CONTAINER_ID}"
else
  echo "url=${CH_URL}"
  echo "WARN: HTTP mode can hit server 30s timeouts on large CSVs (smf_92_*)." >&2
fi

load_one_docker() {
  local table="$1" file="$2"
  docker exec -i \
    "${CONTAINER_ID}" \
    clickhouse-client \
      --user "${CH_USER}" \
      --password="${CH_PASSWORD}" \
      --receive_timeout "${CH_TIMEOUT}" \
      --send_timeout "${CH_TIMEOUT}" \
      --database "${CH_DB}" \
      --input_format_parallel_parsing 0 \
      --input_format_skip_unknown_fields 1 \
      --max_execution_time "${CH_TIMEOUT}" \
      --query "INSERT INTO ${table} FORMAT CSVWithNames" \
    < "${file}"
}

load_one_http() {
  local table="$1" file="$2"
  local tmp code enc query
  tmp="$(mktemp)"
  query="INSERT INTO ${table} SETTINGS input_format_parallel_parsing=0, input_format_skip_unknown_fields=1, max_execution_time=${CH_TIMEOUT}, http_receive_timeout=${CH_TIMEOUT}, receive_timeout=${CH_TIMEOUT}, send_timeout=${CH_TIMEOUT} FORMAT CSVWithNames"
  enc="$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "${query}")"
  code="$(
    curl -sS -o "${tmp}" -w "%{http_code}" \
      --max-time "$((CH_TIMEOUT + 30))" \
      -u "${CH_USER}:${CH_PASSWORD}" \
      "${CH_URL}/?database=${CH_DB}&query=${enc}" \
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
  if [[ "${MODE}" == "docker" ]]; then
    if ! load_one_docker "${base}" "${f}"; then
      echo "ERROR: docker load failed for ${base}" >&2
      failed=$((failed + 1))
      continue
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
