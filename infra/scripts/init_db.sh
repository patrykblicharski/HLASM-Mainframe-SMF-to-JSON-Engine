#!/usr/bin/env bash
# Apply infra/clickhouse/init.sql to a running ClickHouse (Docker or remote).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CH_URL="${CH_URL:-http://127.0.0.1:8123}"
CH_USER="${CH_USER:-smf}"
CH_PASSWORD="${CH_PASSWORD:-blacha123}"
SQL="${ROOT}/clickhouse/init.sql"

echo "Waiting for ClickHouse at ${CH_URL} ..."
for i in $(seq 1 60); do
  if curl -fsS "${CH_URL}/ping" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
curl -fsS "${CH_URL}/ping"
echo

echo "Applying ${SQL} ..."
curl -fsS "${CH_URL}/?user=${CH_USER}&password=${CH_PASSWORD}&database=default" \
  --data-binary @"${SQL}"
echo
echo "OK — schema loaded."
