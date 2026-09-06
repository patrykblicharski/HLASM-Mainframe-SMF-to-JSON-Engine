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

apply_via_docker() {
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

# HTTP has no 'multiquery' URL setting in CH 24.8 — run one statement at a time.
apply_via_curl() {
  local tmp code n stmt
  tmp="$(mktemp)"
  n=0
  while IFS= read -r -d '' stmt; do
    n=$((n + 1))
    code="$(
      curl -sS -o "${tmp}" -w "%{http_code}" \
        -u "${CH_USER}:${CH_PASSWORD}" \
        "${CH_URL}/?database=default" \
        --data-binary "${stmt}"
    )"
    if [[ "${code}" != "200" ]]; then
      echo "ClickHouse HTTP ${code} on statement #${n}:" >&2
      echo "---- statement (head) ----" >&2
      printf '%s\n' "${stmt}" | head -n 25 >&2
      echo "---- response ----" >&2
      cat "${tmp}" >&2
      echo >&2
      rm -f "${tmp}"
      return 1
    fi
  done < <(
    python3 - "${SQL}" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
buf: list[str] = []
for line in text.splitlines(keepends=True):
    stripped = line.lstrip()
    if stripped.startswith("--") and not buf:
        continue
    buf.append(line)
    if line.rstrip().endswith(";"):
        stmt = "".join(buf).strip()
        buf = []
        if stmt:
            sys.stdout.buffer.write(stmt.encode("utf-8") + b"\0")
tail = "".join(buf).strip()
if tail:
    sys.stdout.buffer.write(tail.encode("utf-8") + b"\0")
PY
  )
  rm -f "${tmp}"
  echo "(HTTP applied ${n} statements)"
}

if command -v docker >/dev/null 2>&1 && docker ps --format '{{.Names}}' | grep -qx "${CH_CONTAINER}"; then
  echo "(via docker exec ${CH_CONTAINER})"
  if apply_via_docker; then
    echo
    echo "OK — schema loaded (docker exec)."
    exit 0
  fi
  echo "docker exec failed; trying HTTP statement-by-statement ..." >&2
fi

if apply_via_curl; then
  echo
  echo "OK — schema loaded (HTTP)."
  exit 0
fi

echo "Could not apply init.sql." >&2
exit 1
