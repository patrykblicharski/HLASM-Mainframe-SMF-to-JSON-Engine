#!/usr/bin/env python3
"""Parse PACSYS SMF119 HTML layout pages into JSON section specs."""
from __future__ import annotations

import json
import re
from pathlib import Path

SEC_MARK = re.compile(
    r"\(Offset from beginning of record:\s*(SMF119[A-Za-z0-9_]+)\)",
    re.I,
)


def parse_page(html: str) -> dict:
    html = re.sub(r"<\s*br\s*/?\s*>", "", html, flags=re.I)
    html = SEC_MARK.sub(lambda m: f"\nSEC|{m.group(1)}|\n", html)
    html = re.sub(r"<tr[^>]*>", "\nTR|", html, flags=re.I)
    html = re.sub(r"<td[^>]*>", "|", html, flags=re.I)
    html = re.sub(r"<[^>]+>", "", html)
    html = html.replace("&nbsp;", " ").replace("&amp;", "&")

    sections: list[dict] = []
    current: dict = {"triplet": "HEADER", "fields": []}
    sections.append(current)

    for raw in html.splitlines():
        line = raw.strip()
        if line.startswith("SEC|"):
            trip = line.split("|")[1]
            current = {"triplet": trip, "fields": []}
            sections.append(current)
            continue
        if not line.startswith("TR|"):
            continue
        parts = [p for p in (x.strip() for x in line.split("|")) if p != ""]
        # TR, off, hex, name, len, fmt, desc...
        if len(parts) < 6:
            continue
        try:
            off = int(parts[1])
        except ValueError:
            continue
        name = parts[3]
        if not (name.startswith("SMF119") or name == "--"):
            continue
        length = parts[4]
        fmt = parts[5]
        desc = parts[6] if len(parts) > 6 else ""
        reserved = name == "--"
        if reserved:
            name = f"_rsv_{off}"
        current["fields"].append(
            {
                "offset": off,
                "name": name,
                "length": length,
                "format": fmt,
                "description": re.sub(r"\s+", " ", desc).strip()[:240],
                "reserved": reserved,
            }
        )

    return {"sections": [s for s in sections if s["fields"]]}


def main() -> None:
    src = Path("/tmp/pacsys")
    out_dir = Path("/workspace/smf119-app/tools/pacsys_json")
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {}
    for path in sorted(src.glob("st*.htm")):
        data = parse_page(path.read_text(encoding="utf-8", errors="ignore"))
        subtype = int(path.stem[2:])
        payload = {"subtype": subtype, **data}
        (out_dir / f"st{subtype:02d}.json").write_text(json.dumps(payload, indent=2))
        nfields = sum(len(s["fields"]) for s in data["sections"])
        summary[subtype] = {
            "sections": [s["triplet"] for s in data["sections"]],
            "fields": nfields,
        }
        print(f"st{subtype:02d}: {len(data['sections'])} sections, {nfields} fields")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
