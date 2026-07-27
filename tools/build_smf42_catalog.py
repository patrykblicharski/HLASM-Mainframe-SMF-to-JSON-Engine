#!/usr/bin/env python3
"""Build catalog/smf42/*.json from IBM Docs scrape (catalog/smf42/raw/all_pages.json)."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "catalog" / "smf42" / "raw" / "all_pages.json"
OUT = ROOT / "catalog" / "smf42"

SUBTYPE_TITLES = {
    1: "BMF cache summary / storage-class buffer manager hits",
    2: "Cache control units with SMS-managed devices",
    3: "SMS configuration changed",
    4: "System Data Mover session statistics",
    5: "Storage class VTOC and VVDS I/O statistics",
    6: "Data set level I/O statistics",
    9: "B37/D37/E37 abend information",
    10: "Volume selection failure",
    11: "Extended remote copy session statistics",
    14: "ADSM session resource usage",
    15: "VSAM RLS CF storage class response time",
    16: "VSAM RLS CF data set response time",
    17: "VSAM RLS CF lock structure usage",
    18: "VSAM RLS CF cache partition usage",
    19: "VSAM RLS buffer manager LRU activity",
    20: "STOW initialize",
    21: "Member delete",
    22: "DFSMSrmm audit records",
    23: "DFSMSrmm security records",
    24: "Member add/replace",
    25: "Member rename",
    27: "VTOC DSCB audit record",
}


def hlasm_type(fmt: str, length: str, description: str = "") -> str | None:
    f = (fmt or "").lower()
    desc = (description or "").lower()
    try:
        ln = int(re.sub(r"[^0-9]", "", str(length)) or "0")
    except ValueError:
        ln = 0
    if "ebcdic" in f or f == "character":
        return {1: "T_CHR1", 2: "T_CHR2", 4: "T_CHR4", 8: "T_CHR8", 20: "T_CHR20"}.get(ln)
    if "packed" in f and ln == 4:
        if "time" in desc and "date" not in desc:
            return None
        return "T_DTE"
    if "binary" in f or f == "integer":
        if ln == 4 and "hundredths of a second" in desc:
            return "T_TME"
        return {1: "T_DEC1", 2: "T_DEC2", 4: "T_DEC4"}.get(ln)
    return None


def status_for(field: dict, ht: str | None) -> str:
    desc = (field.get("description") or "").upper()
    # Triplet / section locator meta only (not "number of I/Os", etc.)
    if re.search(r"OFFSET TO .+", desc) and "SECTION" in desc:
        return "skip_meta"
    if re.search(r"LENGTH OF .+ SECTION", desc):
        return "skip_meta"
    if re.search(r"NUMBER OF .+ SECTIONS?\b", desc):
        return "skip_meta"
    if "NUMBER OF TRIPLETS" in desc:
        return "skip_meta"
    if not ht:
        return "needs_engine"
    return "todo"


def json_key(name: str, used: set[str]) -> str:
    tail = re.sub(r"^(SMF42|S42|SMF)", "", name, flags=re.I)
    tail = re.sub(r"[^A-Za-z0-9]", "", tail) or name
    key = tail.lower()[:16]
    if not re.match(r"^[a-z]", key):
        key = ("f" + key)[:16]
    base = key
    n = 2
    while key in used:
        suf = str(n)
        key = (base[: 16 - len(suf)] + suf)[:16]
        n += 1
    used.add(key)
    return key


def collect_descendants(by_file: dict, root_file: str) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    q = [root_file]
    while q:
        f = q.pop(0)
        if f in seen or f not in by_file:
            continue
        seen.add(f)
        p = by_file[f]
        out.append(p)
        for c in p.get("children") or []:
            cf = c.get("file")
            if cf and cf not in seen:
                q.append(cf)
    return out


def main() -> int:
    raw = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    by_file = {p["file"]: p for p in raw}
    header_page = next((p for p in raw if p["title"].startswith("Header/Self-defining")), None)

    subtype_roots: dict[int, dict] = {}
    for p in raw:
        m = re.match(r"Subtype\s+(\d+)\b", p["title"])
        if m:
            subtype_roots[int(m.group(1))] = p

    summary_subtypes: dict[str, dict] = {}
    all_unique: dict[str, dict] = {}

    for sub, root in sorted(subtype_roots.items()):
        pages = collect_descendants(by_file, root["file"])
        if header_page and header_page["file"] not in {p["file"] for p in pages}:
            pages = [header_page] + pages

        fields: list[dict] = []
        used_keys: set[str] = set()
        status_counts: Counter[str] = Counter()
        sections: list[dict] = []

        for p in pages:
            for table in p.get("field_tables") or []:
                section_name = table.get("caption") or p["title"]
                sections.append(
                    {
                        "section": section_name,
                        "source_file": p["file"],
                        "source_title": p["title"],
                        "source_url": p.get("url"),
                        "field_count": len(table["fields"]),
                    }
                )
                for f in table["fields"]:
                    ht = hlasm_type(f.get("format"), f.get("length"), f.get("description") or "")
                    st = status_for(f, ht)
                    rec = {
                        "ibm_name": f["name"],
                        "section": section_name,
                        "source_page": p["title"],
                        "source_file": p["file"],
                        "offset_dec": f.get("offset_dec"),
                        "offset_hex": f.get("offset_hex"),
                        "length": f.get("length"),
                        "format": f.get("format"),
                        "description": f.get("description"),
                        "hlasm_type": ht,
                        "json_key": json_key(f["name"], used_keys) if ht and st == "todo" else None,
                        "status": st,
                    }
                    fields.append(rec)
                    status_counts[st] += 1
                    all_unique[f["name"]] = rec

        subtype_doc = {
            "smf_type": 42,
            "subtype": sub,
            "title": SUBTYPE_TITLES.get(sub, root["title"]),
            "source": {
                "ibm_docs_root": "https://www.ibm.com/docs/en/SSLTBW_3.2.0/com.ibm.zos.v3r2.ieag200/rec42.htm",
                "subtype_page": root.get("url"),
                "manual": "SA38-0667 z/OS MVS System Management Facilities (SMF)",
                "scraped_via": "tools/ibm_docs/crawl_smf42.mjs",
            },
            "field_count": len(fields),
            "status_counts": dict(status_counts),
            "sections": sections,
            "fields": fields,
        }
        (OUT / f"subtype_{sub}.json").write_text(
            json.dumps(subtype_doc, indent=2) + "\n", encoding="utf-8"
        )
        summary_subtypes[str(sub)] = {
            "title": subtype_doc["title"],
            "field_count": len(fields),
            "status_counts": dict(status_counts),
            "sections": len(sections),
            "file": f"subtype_{sub}.json",
        }

    priority: list[dict] = []
    for name in ["SMF42RTY", "SMF42SID", "SMF42SSI", "SMF42STY", "SMF42TME", "SMF42DTE"]:
        if name in all_unique:
            priority.append({**all_unique[name], "reason": "header identity"})

    s6_path = OUT / "subtype_6.json"
    if s6_path.exists():
        doc = json.loads(s6_path.read_text(encoding="utf-8"))
        n = 0
        for f in doc["fields"]:
            if f["status"] != "todo":
                continue
            if f["section"] not in {
                "Data set I/O statistics section",
                "Data set header section",
                "Job header section (data set statistics)",
            }:
                continue
            priority.append({**f, "reason": "subtype6 analytics"})
            n += 1
            if n >= 24:
                break

    (OUT / "priority.json").write_text(
        json.dumps(
            {
                "note": "First-wave SMF42 candidates for HLASM maps (verify IFASMFR labels)",
                "count": len(priority),
                "fields": priority,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    asm = [
        "* Suggested SMF42 header fields — VERIFY IFASMFR labels on z/OS",
        "* Generated from IBM Docs scrape (catalog/smf42)",
        "TABLE42   SMF_START",
        "",
    ]
    for f in priority:
        if f.get("ibm_name") in {
            "SMF42RTY",
            "SMF42SID",
            "SMF42SSI",
            "SMF42STY",
            "SMF42TME",
            "SMF42DTE",
        } and f.get("hlasm_type") and f.get("json_key"):
            asm.append(
                f"         SMF_FIELD {f['ibm_name']}-SMF42RCL,TYPE={f['hlasm_type']},JSON={f['json_key']}"
            )
            asm.append("")
    asm += ["         SMF_END", ""]
    (OUT / "priority_suggested.asm").write_text("\n".join(asm), encoding="utf-8")

    summary = {
        "smf_type": 42,
        "title": "DFSMS statistics and configuration",
        "source_manual": "SA38-0667 / IBM Docs ieag200 Record type 42",
        "source_url": "https://www.ibm.com/docs/en/SSLTBW_3.2.0/com.ibm.zos.v3r2.ieag200/rec42.htm",
        "scrape": {
            "tool": "tools/ibm_docs/crawl_smf42.mjs",
            "pages_scraped": len(raw),
            "pages_with_field_tables": sum(1 for p in raw if p.get("field_tables")),
            "raw_field_rows": sum(
                len(t["fields"]) for p in raw for t in p.get("field_tables") or []
            ),
            "raw_dir": "catalog/smf42/raw/",
        },
        "subtypes_documented": sorted(int(k) for k in summary_subtypes),
        "subtypes": summary_subtypes,
        "note": (
            "Field layouts scraped from IBM Docs section tables via Playwright. "
            "Assembler labels must still be verified against IFASMFR before MAP42*.asm wiring. "
            "Type 42 is NOT in Gatherer OpenAPI."
        ),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"Subtypes: {sorted(summary_subtypes)}")
    print(
        "todo=",
        sum(s["status_counts"].get("todo", 0) for s in summary_subtypes.values()),
        "needs_engine=",
        sum(s["status_counts"].get("needs_engine", 0) for s in summary_subtypes.values()),
        "priority=",
        len(priority),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
