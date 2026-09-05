"""CLI and GUI entrypoint: python -m smf2json"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, IO, List, Optional, TextIO

from .engine import convert_record, ordered_columns
from .progress import CONVERT_BATCH, CliProgress, format_timing
from .reader import iter_dump


def _cli_log(args: argparse.Namespace, msg: str) -> None:
    if msg.startswith("DEBUG") and not args.debug:
        return
    if msg.startswith("INFO") and not (args.debug or args.verbose):
        if not msg.startswith("INFO: loaded"):
            return
    print(msg, file=sys.stderr)


def _write_json_object(fh: IO[str], obj: Dict[str, Any], first: bool) -> None:
    if not first:
        fh.write(",\n")
    dumped = json.dumps(obj, indent=2, ensure_ascii=False)
    for line in dumped.splitlines():
        fh.write("  ")
        fh.write(line)
        fh.write("\n")


def run_cli(args: argparse.Namespace) -> int:
    out = Path(args.output) if args.output else None
    show_bar = not args.no_progress and not args.debug
    bar = CliProgress(enabled=show_bar, label=Path(args.input).name)

    def reader_log(msg: str) -> None:
        _cli_log(args, msg)

    convert_log = reader_log if args.debug else None
    last_pos = 0
    total = 0
    seen = 0
    mapped = 0
    t_start = time.perf_counter()
    t_records_start: Optional[float] = None

    def on_progress(pos: int, n: int) -> None:
        nonlocal last_pos, total
        last_pos = pos
        total = n
        bar.update(pos, n, seen, mapped)

    json_fh: Optional[TextIO] = None
    csv_fh: Optional[TextIO] = None
    csv_writer: Optional[csv.DictWriter] = None
    csv_pending: List[Dict[str, Any]] = []
    json_first = True
    close_json = False
    close_csv = False

    def open_json() -> None:
        nonlocal json_fh, close_json
        if json_fh is not None:
            return
        if out:
            json_fh = out.open("w", encoding="utf-8")
            close_json = True
        else:
            json_fh = sys.stdout
        json_fh.write("[\n")

    def flush_csv_pending() -> None:
        nonlocal csv_fh, csv_writer, close_csv
        if not csv_pending:
            return
        if csv_writer is None:
            if out:
                csv_fh = out.open("w", encoding="utf-8", newline="")
                close_csv = True
            else:
                csv_fh = sys.stdout
            cols = ordered_columns(csv_pending)
            csv_writer = csv.DictWriter(csv_fh, fieldnames=cols, extrasaction="ignore")
            csv_writer.writeheader()
        assert csv_fh is not None
        for row in csv_pending:
            csv_writer.writerow({c: row.get(c, "") for c in csv_writer.fieldnames})
        csv_pending.clear()
        csv_fh.flush()

    try:
        for rec in iter_dump(args.input, log=reader_log, progress=on_progress):
            if t_records_start is None:
                t_records_start = time.perf_counter()
            seen += 1
            obj = convert_record(rec, log=convert_log)
            if obj is None:
                continue
            mapped += 1
            if args.format == "json":
                open_json()
                assert json_fh is not None
                _write_json_object(json_fh, obj, json_first)
                json_first = False
                if mapped % CONVERT_BATCH == 0:
                    json_fh.flush()
            else:
                csv_pending.append(obj)
                if len(csv_pending) >= CONVERT_BATCH:
                    flush_csv_pending()
            if mapped % CONVERT_BATCH == 0:
                bar.update(last_pos, total, seen, mapped, force=True)

        if args.format == "csv":
            flush_csv_pending()

        if json_fh is not None:
            json_fh.write("]\n")
            if close_json:
                json_fh.close()
                close_json = False

        t_end = time.perf_counter()
        records_s = (t_end - t_records_start) if t_records_start is not None else 0.0
        dump_s = t_end - t_start

        bar.update(total or last_pos, total or last_pos, seen, mapped, force=True)
        bar.close()
        print(f"INFO: timing  {format_timing(records_s, dump_s)}", file=sys.stderr)

        if mapped == 0:
            print("No mapped records found.", file=sys.stderr)
            return 2

        if out is not None and args.format == "json":
            print(f"Wrote {out} ({mapped:,} objects)", file=sys.stderr)
        elif close_csv and out is not None:
            print(f"Wrote {out} ({mapped:,} rows)", file=sys.stderr)

        if args.verbose or args.debug:
            print(f"INFO: converted {mapped:,} mapped records from {seen:,} SMF records", file=sys.stderr)
        return 0
    finally:
        if close_json and json_fh is not None:
            json_fh.close()
        if close_csv and csv_fh is not None:
            csv_fh.close()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="smf2json",
        description="Convert binary SMF dumps (types 30/80/89/119-1) to JSON or CSV",
    )
    p.add_argument("input", nargs="?", help="SMF dump path (omit to launch GUI)")
    p.add_argument("-o", "--output", help="Output file (json/csv)")
    p.add_argument("-f", "--format", choices=("json", "csv"), default="json")
    p.add_argument("--gui", action="store_true", help="Force GUI even if input given")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--debug", action="store_true", help="Print field-level debug lines")
    p.add_argument(
        "--no-progress",
        action="store_true",
        help="Do not draw the stderr progress bar (also off when --debug)",
    )
    p.add_argument("--make-sample", metavar="PATH", help="Write a synthetic sample dump and exit")
    args = p.parse_args(argv)

    if args.make_sample:
        from .sample_dump import build_smf30, build_smf80, build_smf119_st01

        path = Path(args.make_sample)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(build_smf30() + build_smf80() + build_smf119_st01())
        print(f"Wrote sample dump {path}")
        return 0

    if args.gui or not args.input:
        from .gui import run_app

        run_app(initial_file=args.input)
        return 0

    return run_cli(args)


if __name__ == "__main__":
    raise SystemExit(main())
