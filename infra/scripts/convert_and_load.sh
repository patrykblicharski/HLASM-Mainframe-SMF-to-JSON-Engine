#!/usr/bin/env bash
# End-to-end: SMF dump → per-type CSV → ClickHouse → stats refresh.
# Usage: ./convert_and_load.sh /path/to/dump.smf [csv_out_dir]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "${ROOT}/.." && pwd)"
DUMP="${1:?Usage: $0 /path/to/dump.smf [csv_dir]}"
CSV_DIR="${2:-${ROOT}/data/csv}"

mkdir -p "${CSV_DIR}"
echo "== export CSV by type =="
python "${ROOT}/scripts/export_csv_by_type.py" "${DUMP}" -o "${CSV_DIR}" -v

echo "== load into ClickHouse =="
"${ROOT}/scripts/load_all.sh" "${CSV_DIR}"

echo "== refresh Grafana stats =="
"${ROOT}/scripts/refresh_stats.sh"

echo "Done."
