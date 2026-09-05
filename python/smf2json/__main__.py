"""CLI and GUI entrypoint: python -m smf2json"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .engine import convert_dump, ordered_columns
from .reader import read_dump


def run_cli(args: argparse.Namespace) -> int:
    def log(msg: str) -> None:
        if args.debug or args.verbose or msg.startswith(("ERROR", "WARN", "INFO")):
            if args.debug or not msg.startswith("DEBUG"):
                print(msg, file=sys.stderr)
            elif args.debug:
                print(msg, file=sys.stderr)

    records = read_dump(args.input, log=log)
    rows = convert_dump(records, log=log)
    if not rows:
        print("No mapped records found.", file=sys.stderr)
        return 2

    out = Path(args.output) if args.output else None
    if args.format == "json":
        text = json.dumps(rows, indent=2, ensure_ascii=False)
        if out:
            out.write_text(text, encoding="utf-8")
            print(f"Wrote {out}")
        else:
            print(text)
    else:
        cols = ordered_columns(rows)
        fh = out.open("w", encoding="utf-8", newline="") if out else sys.stdout
        close = out is not None
        try:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for row in rows:
                w.writerow({c: row.get(c, "") for c in cols})
        finally:
            if close:
                fh.close()
                print(f"Wrote {out}")
    return 0


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
