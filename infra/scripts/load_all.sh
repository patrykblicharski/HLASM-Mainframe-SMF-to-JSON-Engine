#!/usr/bin/env bash
# Load every smf_*.csv from a directory into matching ClickHouse tables.
# Usage: ./load_all.sh [csv_dir]
set -euo pipefail

CSV_DIR="${1:-$(cd "$(dirname "$0")/.." && pwd)/data/csv}"
CH_URL="${CH_URL:-http://127.0.0.1:8123}"
CH_USER="${CH_USER:-smf}"
CH_PASSWORD="${CH_PASSWORD:-smf_change_me}"
CH_DB="${CH_DB:-smf}"

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

loaded=0
for f in "${files[@]}"; do
  base="$(basename "${f}" .csv)"
  echo "Loading ${f} → ${CH_DB}.${base}"
  curl -fsS \
    "${CH_URL}/?user=${CH_USER}&password=${CH_PASSWORD}&database=${CH_DB}&input_format_skip_unknown_fields=1&query=INSERT%20INTO%20${base}%20FORMAT%20CSVWithNames" \
    --data-binary @"${f}"
  echo
  loaded=$((loaded + 1))
done

echo "Loaded ${loaded} file(s) from ${CSV_DIR}"
