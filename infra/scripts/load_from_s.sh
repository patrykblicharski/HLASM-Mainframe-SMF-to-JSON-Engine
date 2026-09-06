#!/usr/bin/env bash
# Convert every ~/s/t*.raw.dump → CSV → ClickHouse → refresh stats.
# Usage: ./load_from_s.sh [dump_dir] [csv_dir]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DUMP_DIR="${1:-$HOME/s}"
CSV_DIR="${2:-${ROOT}/data/csv}"

if [[ ! -d "${DUMP_DIR}" ]]; then
  echo "Dump directory not found: ${DUMP_DIR}" >&2
  exit 1
fi

mkdir -p "${CSV_DIR}"
chmod +x "${ROOT}/scripts/"*.sh 2>/dev/null || true

shopt -s nullglob
dumps=("${DUMP_DIR}"/t*.raw.dump)
if [[ ${#dumps[@]} -eq 0 ]]; then
  echo "No t*.raw.dump files in ${DUMP_DIR}" >&2
  exit 1
fi

for dump in "${dumps[@]}"; do
  echo "== $(basename "${dump}") =="
  python "${ROOT}/scripts/export_csv_by_type.py" "${dump}" -o "${CSV_DIR}"
done

echo "== load CSV into ClickHouse =="
"${ROOT}/scripts/load_all.sh" "${CSV_DIR}"

echo "== refresh Grafana stats =="
"${ROOT}/scripts/refresh_stats.sh"

echo "Done — loaded dumps from ${DUMP_DIR}"
