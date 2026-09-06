#!/usr/bin/env python3
"""Split one SMF dump into per-type / per-subtype CSV files for ClickHouse.

Uses the stdlib-only smf2json package (no pip installs).

Usage (from repo root):
  python infra/scripts/export_csv_by_type.py path/to/dump.smf -o infra/data/csv
  python infra/scripts/export_csv_by_type.py path/to/dump.smf -o infra/data/csv --types 14,30,119
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from smf2json.engine import convert_record, ordered_columns  # noqa: E402
from smf2json.reader import iter_dump  # noqa: E402


Key = Tuple[int, Optional[int]]


def table_name(rty: int, sty: Optional[int], subtype_maps: Set[int]) -> str:
    if rty in subtype_maps and sty is not None:
        return f"smf_{rty}_{sty}"
    return f"smf_{rty}"


def parse_types(raw: Optional[str]) -> Optional[Set[int]]:
    if not raw:
        return None
    return {int(x.strip()) for x in raw.split(",") if x.strip()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", help="Binary SMF dump (RECFM=VB/VBS)")
    ap.add_argument("-o", "--output-dir", required=True, help="Directory for CSV files")
    ap.add_argument(
        "--types",
        help="Comma-separated SMF types to export (default: all mapped)",
    )
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    from smf2json.maps import MAPS_BY_SUBTYPE

    subtype_types = {rty for rty, _sty in MAPS_BY_SUBTYPE}
    want = parse_types(args.types)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    buckets: Dict[str, List[dict]] = defaultdict(list)
    seen = mapped = 0

    for rec in iter_dump(args.input):
        seen += 1
        if want is not None and rec.record_type not in want:
            continue
        obj = convert_record(rec)
        if obj is None:
            continue
        mapped += 1
        sty = None
        if "smf_subtype" in obj and str(obj["smf_subtype"]).strip() != "":
            try:
                sty = int(str(obj["smf_subtype"]).strip())
            except ValueError:
                sty = rec.subtype
        elif rec.record_type in subtype_types:
            sty = rec.subtype
        name = table_name(rec.record_type, sty, subtype_types)
        buckets[name].append(obj)

    written = 0
    for name, rows in sorted(buckets.items()):
        path = out_dir / f"{name}.csv"
        cols = ordered_columns(rows)
        with path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for row in rows:
                w.writerow({c: row.get(c, "") for c in cols})
        written += 1
        print(f"Wrote {path} ({len(rows):,} rows, {len(cols)} cols)")

    print(
        f"Done: {written} CSV file(s), {mapped:,} mapped / {seen:,} records → {out_dir}",
        file=sys.stderr,
    )
    return 0 if written else 2


if __name__ == "__main__":
    raise SystemExit(main())
