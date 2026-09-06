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

echo "Auth check (${CH_USER}@${CH_URL}) ..."
auth_tmp="$(mktemp)"
auth_code="$(
  curl -sS -o "${auth_tmp}" -w "%{http_code}" \
    -u "${CH_USER}:${CH_PASSWORD}" \
    "${CH_URL}/" \
    --data-binary "SELECT 1"
)"
if [[ "${auth_code}" != "200" ]] || [[ "$(tr -d '[:space:]' < "${auth_tmp}")" != "1" ]]; then
  echo "HTTP auth failed (${auth_code}):" >&2
  cat "${auth_tmp}" >&2
  echo >&2
  echo "Try: curl -s -u '${CH_USER}:${CH_PASSWORD}' '${CH_URL}/' --data-binary 'SELECT 1'" >&2
  echo "If that fails: docker compose down -v && docker compose up -d" >&2
  rm -f "${auth_tmp}"
  exit 1
fi
rm -f "${auth_tmp}"
echo "Auth OK"

echo "Applying ${SQL} ..."

apply_via_curl() {
  # Basic auth + multiquery (do NOT put password in the URL — bare 403).
  local tmp code
  tmp="$(mktemp)"
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

apply_via_docker() {
  # Prefer --password=... so the value is never eaten as a separate token.
  docker exec -i \
    -e "CLICKHOUSE_USER=${CH_USER}" \
    -e "CLICKHOUSE_PASSWORD=${CH_PASSWORD}" \
    "${CH_CONTAINER}" \
    clickhouse-client \
      --user "${CH_USER}" \
      --password="${CH_PASSWORD}" \
      --multiquery \
    < "${SQL}"
}

# HTTP Basic auth is what works from the host; docker exec is fallback.
if apply_via_curl; then
  echo
  echo "OK — schema loaded (HTTP)."
  exit 0
fi

echo "HTTP apply failed; trying docker exec ${CH_CONTAINER} ..." >&2
if command -v docker >/dev/null 2>&1 && docker ps --format '{{.Names}}' | grep -qx "${CH_CONTAINER}"; then
  apply_via_docker
  echo
  echo "OK — schema loaded (docker exec)."
  exit 0
fi

echo "Could not apply init.sql via HTTP or docker exec." >&2
exit 1
