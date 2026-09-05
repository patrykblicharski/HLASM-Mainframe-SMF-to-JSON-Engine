#!/usr/bin/env python3
"""One-off: dump smfexplorer field metadata to JSON for catalog generation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app_core.session import KNOWN_RECORD_MODULES, list_fields


def main() -> None:
    out = {}
    for record_name in KNOWN_RECORD_MODULES:
        try:
            out[record_name] = list_fields(record_name)
        except Exception as exc:  # collect errors instead of aborting the whole run
            out[record_name] = {"error": str(exc)}

    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")

    total_fields = sum(len(v) for v in out.values() if isinstance(v, list))
    errors = [k for k, v in out.items() if isinstance(v, dict) and "error" in v]
    print(
        f"# {len(out)} modules, {total_fields} fields total, {len(errors)} errors: {errors}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
