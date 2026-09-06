#!/usr/bin/env bash
# Apply infra/clickhouse/init.sql to a running ClickHouse (Docker or remote).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CH_URL="${CH_URL:-http://127.0.0.1:8123}"
CH_USER="${CH_USER:-smf}"
CH_PASSWORD="${CH_PASSWORD:-blacha123}"
CH_CONTAINER="${CH_CONTAINER:-smf-clickhouse}"
SQL="${ROOT}/clickhouse/init.sql"

echo "Waiting for ClickHouse at ${CH_URL} ..."
for _ in $(seq 1 60); do
  if curl -fsS "${CH_URL}/ping" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
curl -fsS "${CH_URL}/ping"
echo

echo "Applying ${SQL} ..."

apply_via_docker() {
  docker exec -i "${CH_CONTAINER}" \
    clickhouse-client --user "${CH_USER}" --password "${CH_PASSWORD}" --multiquery \
    < "${SQL}"
}

apply_via_curl() {
  # Basic auth + multiquery (query-string password often returns bare 403).
  local tmp
  tmp="$(mktemp)"
  local code
  code="$(
    curl -sS -o "${tmp}" -w "%{http_code}" \
      -u "${CH_USER}:${CH_PASSWORD}" \
      "${CH_URL}/?database=default&multiquery=1" \
      --data-binary @"${SQL}"
  )"
  if [[ "${code}" != "200" ]]; then
    echo "ClickHouse HTTP ${code}:" >&2
    cat "${tmp}" >&2
    echo >&2
    rm -f "${tmp}"
    return 1
  fi
  cat "${tmp}"
  rm -f "${tmp}"
}

if command -v docker >/dev/null 2>&1 && docker ps --format '{{.Names}}' | grep -qx "${CH_CONTAINER}"; then
  echo "(via docker exec ${CH_CONTAINER})"
  apply_via_docker
else
  echo "(via HTTP ${CH_URL})"
  apply_via_curl
fi

echo
echo "OK — schema loaded."
