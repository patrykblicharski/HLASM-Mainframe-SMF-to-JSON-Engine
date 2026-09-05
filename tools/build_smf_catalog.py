#!/usr/bin/env python3
"""Build HLASM-oriented SMF field catalogs from Gatherer OpenAPI + fields_dump."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OPENAPI = ROOT / "ref" / "openapi_spec.json"
DEFAULT_FIELDS_DUMP = ROOT / "ref" / "fields_dump.json"
DEFAULT_MAP30 = ROOT / "src" / "MAP30.asm"
DEFAULT_OUT = ROOT / "catalog" / "smf30"

# Type 30 section schema → IFASMFR section base + header triplet offset field.
# Used to propose portable SMF_FIELD operands (labels, not numeric offsets).
SMF30_SECTION_HINTS: dict[str, dict[str, str]] = {
    "SMF30_SUBSYSTEM_SECTION": {
        "section_base": "SMF30PSS",
        "triplet": "SMF30SOF",
        "case": "triplet",
    },
    "SMF30_IDENTIFICATION_SECTION": {
        "section_base": "SMF30JBN",
        "triplet": "SMF30IOF",
        "case": "triplet",
    },
    "SMF30_SUBTYPE1_IDENTIFICATION_SECTION": {
        "section_base": "SMF30JBN",
        "triplet": "SMF30IOF",
        "case": "triplet",
    },
    "SMF30_SUBTYPE6_IDENTIFICATION_SECTION": {
        "section_base": "SMF30JBN",
        "triplet": "SMF30IOF",
        "case": "triplet",
    },
    "SMF30_PROCESSOR_ACCOUNTING_SECTION": {
        "section_base": "SMF30PTY",
        "triplet": "SMF30COF",
        "case": "triplet",
    },
    "SMF30_IO_ACTIVITY_SECTION": {
        "section_base": "SMF30INDC",  # best-effort; verify in IFASMFR before ASM
        "triplet": "SMF30UOF",
        "case": "triplet",
    },
    "SMF30_COMPLETION_SECTION": {
        "section_base": "SMF30SCC",
        "triplet": "SMF30TOF",
        "case": "triplet",
    },
    "SMF30_STORAGE_AND_PAGING_SECTION": {
        "section_base": "SMF30RSV",
        "triplet": "SMF30ROF",
        "case": "triplet",
    },
    "SMF30_PERFORMANCE_SECTION": {
        "section_base": "SMF30PFL",
        "triplet": "SMF30POF",
        "case": "triplet",
    },
    "SMF30_OPERATOR_SECTION": {
        "section_base": "SMF30OPF",
        "triplet": "SMF30OOF",
        "case": "triplet",
    },
    "SMF30_EXECUTE_CHANNEL_PROGRAM_SECTION": {
        "section_base": "SMF30DEV",
        "triplet": "SMF30EOF",
        "case": "triplet",
    },
    "SMF30_ACCOUNTING_SECTION": {
        "section_base": "SMF30ACL",
        "triplet": "SMF30AOF",
        "case": "triplet",
    },
}

# Preferred HLASM JSON keys (≤16). Includes shipped MAP30 + first-wave names.
JSON_KEY_OVERRIDES: dict[str, str] = {
    "SMF30RTY": "smf_record_type",
    "SMF30SID": "smf_system_id",
    "SMF30TME": "time",
    "SMF30DTE": "date",
    "SMF30STP": "subtype",
    "SMF30WID": "work_class_id",
    "SMF30RVN": "rec_version",
    "SMF30PNM": "addr_space_ind",
    "SMF30JBN": "job_name",
    "SMF30PGM": "program_name",
    "SMF30STM": "step_name",
    "SMF30JNM": "jes_job_num",
    "SMF30USR": "user_name",
    "SMF30CPT": "cpu_step_time",
    "SMF30CPS": "srb_time",
    "SMF30SCC": "step_comp_code",
    "SMF30ARC": "abend_reason",
}

# Explorer smfexplorer name → preferred HLASM JSON key (≤16).
EXPLORER_JSON_OVERRIDES: dict[str, str] = {
    "job_name": "job_name",
    "step_name": "step_name",
    "step_time": "cpu_step_time",
    "srb_step_cpu_time": "srb_time",
    "sys_name": "smf_system_id",
    "user_name": "user_name",
    "step_completion_code": "step_comp_code",
    "pgm_prog_name": "program_name",
}

# Curated first-wave fields for HLASM (engine-supported types only).
PRIORITY_IBM_FIELDS: list[str] = [
    "SMF30RTY",
    "SMF30SID",
    "SMF30TME",
    "SMF30DTE",
    "SMF30STP",
    "SMF30WID",
    "SMF30RVN",
    "SMF30PNM",
    "SMF30JBN",
    "SMF30PGM",
    "SMF30STM",
    "SMF30USR",
    "SMF30JNM",
    "SMF30CPT",
    "SMF30CPS",
    "SMF30SCC",
    "SMF30ARC",
]

STOPWORDS = {
    "the",
    "a",
    "an",
    "of",
    "to",
    "for",
    "and",
    "or",
    "in",
    "on",
    "is",
    "be",
    "this",
    "that",
    "with",
    "from",
    "record",
    "section",
    "segment",
    "number",
    "offset",
    "length",
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def parse_map_asm(path: Path) -> dict[str, dict[str, str]]:
    """Return ibm_field -> {json, type, triplet?} from a MAP*.asm (follows COPY)."""
    mapped: dict[str, dict[str, str]] = {}
    if not path.exists():
        return mapped

    def expand(p: Path) -> list[str]:
        lines: list[str] = []
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            mcopy = re.match(r"\s*COPY\s+(\S+)", line, re.I)
            if mcopy:
                name = mcopy.group(1).strip().strip("'").upper()
                # HLASM member name without extension
                cand = p.parent / f"{name}.asm"
                if not cand.exists():
                    cand = p.parent / name
                if cand.exists():
                    lines.extend(expand(cand))
                continue
            lines.append(line)
        return lines

    logical: list[str] = []
    buf = ""
    for line in expand(path):
        if not line.strip() or line.lstrip().startswith("*"):
            continue
        if line.rstrip().endswith("X"):
            buf += line.rstrip()[:-1].rstrip() + " "
            continue
        buf += line
        logical.append(buf)
        buf = ""
    if buf:
        logical.append(buf)

    for line in logical:
        m2 = re.search(r"SMF_FIELD\s+([A-Z0-9]+)-", line, re.I)
        if not m2:
            continue
        ibm = m2.group(1).upper()
        typ = re.search(r"TYPE=(T_[A-Z0-9_]+)", line)
        js = re.search(r"JSON=([A-Za-z0-9_]+)", line)
        trip = re.search(r"TRIPLET=([A-Z0-9]+)-", line)
        if typ and js:
            mapped[ibm] = {
                "json": js.group(1),
                "type": typ.group(1),
                "triplet": trip.group(1) if trip else "",
            }
    return mapped


def parse_map30(path: Path) -> dict[str, dict[str, str]]:
    """Compatibility wrapper — prefer MAP30CMN via COPY inside MAP30.asm."""
    return parse_map_asm(path)


def suggest_hlasm_type(datatype: str | None, size: int | None) -> tuple[str | None, str]:
    """Return (T_* or None, status)."""
    dt = (datatype or "").upper()
    sz = int(size or 0)
    if dt in {"CHARACTER", "EBCDIC"}:
        if sz == 1:
            return "T_CHR1", "supported"
        if sz == 2:
            return "T_CHR2", "supported"
        if sz == 4:
            return "T_CHR4", "supported"
        if sz == 8:
            return "T_CHR8", "supported"
        if sz == 20:
            return "T_CHR20", "supported"
        return None, "needs_engine"  # other lengths
    if dt in {"HEX_STR"}:
        if sz == 2:
            return "T_HEX2", "supported"
        return None, "needs_engine"
    if dt in {"UNSIGNED", "SIGNED"}:
        if sz == 1:
            return "T_DEC1", "supported"
        if sz == 2:
            return "T_DEC2", "supported"
        if sz == 4:
            return "T_DEC4", "supported"
        return None, "needs_engine"
    if dt in {"PACKED_DATE_2"}:
        return "T_DTE", "supported"
    if dt in {"SIGNED", "UNSIGNED"} and False:
        pass
    # SMF time often SIGNED/UNSIGNED size 4 with format time — handled by caller
    if dt in {"TOD", "ETOD", "FLOAT", "PACKED", "PACKED_TIME_2", "PACKED_TIME_3", "PACKED_TIME_4"}:
        return None, "needs_engine"
    if dt in {"BIT", "BIN_STR", "HEX_STR", "ADDRESS"}:
        return None, "needs_engine"
    if not dt:
        return None, "unknown"
    return None, "needs_engine"


def suggest_json_key(
    ibm: str,
    description: str,
    explorer_name: str | None,
    used: set[str],
) -> str:
    if ibm in JSON_KEY_OVERRIDES:
        return JSON_KEY_OVERRIDES[ibm]
    if explorer_name and explorer_name in EXPLORER_JSON_OVERRIDES:
        key = EXPLORER_JSON_OVERRIDES[explorer_name]
        return uniquify(key, used)
    if explorer_name and re.fullmatch(r"[a-z][a-z0-9_]{0,15}", explorer_name):
        return uniquify(explorer_name[:16], used)

    # From IBM trailing token: SMF30CPT -> cpt, prefer description words
    words = re.findall(r"[A-Za-z]+", description or "")
    words = [w.lower() for w in words if w.lower() not in STOPWORDS and len(w) > 1]
    key = "_".join(words[:4])
    key = re.sub(r"_+", "_", key).strip("_")
    if not key or len(key) > 16:
        tail = re.sub(r"^SMF\d+", "", ibm, flags=re.I).lower()
        tail = re.sub(r"[^a-z0-9]", "", tail) or ibm.lower()[-8:]
        # expand common tails
        commons = {
            "jbn": "job_name",
            "stm": "step_name",
            "pgm": "program_name",
            "usr": "user_name",
            "jnm": "job_num",
            "stp": "subtype",
            "wid": "work_class",
            "scc": "step_comp_code",
            "arc": "abend_reason",
            "sid": "smf_system_id",
            "rty": "smf_record_type",
        }
        key = commons.get(tail, tail)[:16]
    key = key[:16]
    if not re.match(r"^[a-z]", key):
        key = "f_" + key
        key = key[:16]
    return uniquify(key, used)


def uniquify(key: str, used: set[str]) -> str:
    base = key[:16]
    if base not in used:
        used.add(base)
        return base
    n = 2
    while True:
        suffix = str(n)
        cand = (base[: 16 - len(suffix)] + suffix)[:16]
        if cand not in used:
            used.add(cand)
            return cand
        n += 1


def resolve_ref(schemas: dict, node: dict) -> dict:
    if "$ref" in node:
        name = node["$ref"].rsplit("/", 1)[-1]
        return schemas[name]
    return node


def iter_leaves(
    schemas: dict,
    obj: dict,
    section: str,
    prefix: str = "",
):
    props = obj.get("properties") or {}
    for key, raw in props.items():
        node = resolve_ref(schemas, raw) if "$ref" in raw else raw
        path = f"{prefix}.{key}" if prefix else key
        if "$ref" in raw:
            ref_name = raw["$ref"].rsplit("/", 1)[-1]
            # section schemas
            if re.search(r"_SECTION|_AREA|_DATA$", ref_name):
                yield from iter_leaves(schemas, node, ref_name, path)
            elif re.fullmatch(r"SMF\d+_SUBTYPE\d+", ref_name):
                yield from iter_leaves(schemas, node, section, path)
            else:
                yield from iter_leaves(schemas, node, section or ref_name, path)
            continue
        if node.get("type") == "array" and isinstance(node.get("items"), dict):
            items = node["items"]
            if "$ref" in items:
                ref_name = items["$ref"].rsplit("/", 1)[-1]
                yield from iter_leaves(
                    schemas, resolve_ref(schemas, items), ref_name, path + "[]"
                )
            else:
                yield path, key, items, section
            continue
        if node.get("type") == "object" and "properties" in node:
            yield from iter_leaves(schemas, node, section, path)
            continue
        yield path, key, node, section


def index_fields_dump(dump: dict) -> dict[str, list[dict]]:
    """ibm-ish token from description → explorer fields; also by name."""
    by_ibm: dict[str, list[dict]] = defaultdict(list)
    for module, fields in dump.items():
        if not module.startswith("SMF30"):
            continue
        for field in fields:
            desc = field.get("description") or ""
            # descriptions often contain SMF30XXX
            for ibm in re.findall(r"\bSMF30[A-Z0-9]+\b", desc.upper()):
                by_ibm[ibm].append({**field, "_module": module})
            by_ibm[field["name"]].append({**field, "_module": module})
    return by_ibm


def find_explorer_match(by_ibm: dict, ibm: str, description: str) -> dict | None:
    if ibm in by_ibm:
        # prefer non-virtual
        cands = by_ibm[ibm]
        real = [c for c in cands if not c.get("virtual")]
        return (real or cands)[0]
    # match explorer fields whose description mentions ibm
    return None


def build_subtype(
    schemas: dict,
    subtype: int,
    map30: dict[str, dict[str, str]],
    by_ibm: dict,
) -> dict:
    root_name = f"SMF30_SUBTYPE{subtype}"
    root = schemas[root_name]
    used_keys: set[str] = set()
    fields_out = []
    status_counts: Counter = Counter()

    for path, ibm, node, section in iter_leaves(schemas, root, "HEADER"):
        if not ibm.startswith("SMF"):
            # skip non-SMF property names at roots if any
            pass
        desc = (node.get("description") or "").strip()
        datatype = node.get("x-zml-datatype")
        size = node.get("x-zml-size")
        offset = node.get("x-zml-offset")
        fmt = node.get("format")
        is_meta = bool(node.get("x-zdg-is-meta"))

        # Time fields: OpenAPI often marks SMF30TME as SIGNED + format time
        hlasm_type, support = suggest_hlasm_type(datatype, size)
        if ibm.endswith("TME") or (fmt == "time" and size == 4):
            hlasm_type, support = "T_TME", "supported"
        if ibm.endswith("DTE") or datatype == "PACKED_DATE_2":
            hlasm_type, support = "T_DTE", "supported"

        explorer = find_explorer_match(by_ibm, ibm, desc)
        explorer_name = explorer.get("name") if explorer else None
        json_key = suggest_json_key(ibm, desc, explorer_name, used_keys)

        mapped = map30.get(ibm)
        if mapped:
            status = "mapped"
            json_key = mapped["json"]
            hlasm_type = mapped["type"]
            used_keys.add(json_key)
        elif is_meta:
            status = "skip_meta"
        elif support == "supported":
            status = "todo"
        elif support == "needs_engine":
            status = "needs_engine"
        else:
            status = "unknown"

        # Header detection: no section / subtype root properties
        case = "header"
        section_base = "SMF30LEN"
        triplet = ""
        if section and section != "HEADER" and not section.startswith("SMF30_SUBTYPE"):
            hint = SMF30_SECTION_HINTS.get(section)
            if hint:
                case = hint["case"]
                section_base = hint["section_base"]
                triplet = hint["triplet"]
            else:
                case = "triplet_unknown_section"
                section_base = ""
                triplet = ""
        elif section.startswith("SMF30_SUBTYPE") or section == "HEADER":
            header_names = {
                "SMF30LEN",
                "SMF30SEG",
                "SMF30FLG",
                "SMF30RTY",
                "SMF30TME",
                "SMF30DTE",
                "SMF30SID",
                "SMF30WID",
                "SMF30STP",
            }
            if ibm in header_names or (
                section == "HEADER"
                and offset is not None
                and int(offset) < 24
                and not any(
                    ibm.startswith(p)
                    for p in (
                        "SMF30S",
                        "SMF30I",
                        "SMF30U",
                        "SMF30T",
                        "SMF30C",
                        "SMF30A",
                        "SMF30R",
                        "SMF30P",
                        "SMF30O",
                        "SMF30E",
                    )
                )
            ):
                case = "header"
                section_base = "SMF30LEN"
                triplet = ""
            elif section in SMF30_SECTION_HINTS:
                hint = SMF30_SECTION_HINTS[section]
                case = hint["case"]
                section_base = hint["section_base"]
                triplet = hint["triplet"]

        status_counts[status] += 1
        fields_out.append(
            {
                "ibm_name": ibm,
                "path": path,
                "section": section,
                "case": case,
                "section_base": section_base,
                "triplet": triplet,
                "description": desc,
                "openapi_datatype": datatype,
                "openapi_format": fmt,
                "openapi_offset": offset,
                "openapi_size": size,
                "is_meta": is_meta,
                "explorer_name": explorer_name,
                "hlasm_type": hlasm_type,
                "json_key": json_key,
                "status": status,
                "priority": ibm in PRIORITY_IBM_FIELDS,
            }
        )

    return {
        "smf_type": 30,
        "subtype": subtype,
        "schema": root_name,
        "field_count": len(fields_out),
        "status_counts": dict(status_counts),
        "fields": fields_out,
    }


def render_priority_asm(priority_fields: list[dict]) -> str:
    lines = [
        "* Auto-suggested SMF_FIELD lines from catalog/smf30/priority.json",
        "* VERIFY section_base / triplet labels against IFASMFR before assemble.",
        "",
    ]
    seen = set()
    for f in priority_fields:
        ibm = f["ibm_name"]
        if ibm in seen:
            continue
        seen.add(ibm)
        if f["status"] == "mapped":
            lines.append(f"* already mapped: {ibm} -> {f['json_key']}")
            continue
        if f["status"] != "todo" or not f.get("hlasm_type"):
            lines.append(
                f"* skip {ibm}: status={f['status']} type={f.get('hlasm_type')}"
            )
            continue
        base = f.get("section_base") or "SMF30LEN"
        typ = f["hlasm_type"]
        js = f["json_key"]
        if f.get("triplet"):
            lines.append(
                f"         SMF_FIELD {ibm}-{base},TRIPLET={f['triplet']}-SMF30LEN,        X"
            )
            lines.append(f"               TYPE={typ},JSON={js}")
        else:
            lines.append(
                f"         SMF_FIELD {ibm}-{base},TYPE={typ},JSON={js}"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--openapi", type=Path, default=DEFAULT_OPENAPI)
    ap.add_argument("--fields-dump", type=Path, default=DEFAULT_FIELDS_DUMP)
    ap.add_argument("--map30", type=Path, default=DEFAULT_MAP30)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    spec = load_json(args.openapi)
    schemas = spec["components"]["schemas"]
    dump = load_json(args.fields_dump) if args.fields_dump.exists() else {}
    by_ibm = index_fields_dump(dump)
    map30 = parse_map30(args.map30) if args.map30.exists() else {}

    args.out.mkdir(parents=True, exist_ok=True)
    summary = {
        "smf_type": 30,
        "source_openapi": str(args.openapi.relative_to(ROOT)),
        "source_fields_dump": str(args.fields_dump.relative_to(ROOT))
        if args.fields_dump.exists()
        else None,
        "map30_mapped_fields": sorted(map30),
        "subtypes": {},
    }

    all_priority: list[dict] = []
    for subtype in range(1, 7):
        cat = build_subtype(schemas, subtype, map30, by_ibm)
        out_path = args.out / f"subtype_{subtype}.json"
        out_path.write_text(json.dumps(cat, indent=2) + "\n", encoding="utf-8")
        summary["subtypes"][str(subtype)] = {
            "field_count": cat["field_count"],
            "status_counts": cat["status_counts"],
            "file": f"subtype_{subtype}.json",
        }
        for f in cat["fields"]:
            if f["priority"]:
                all_priority.append({**f, "subtype": subtype})

    # Dedup priority by ibm_name (prefer subtype 4 — step total — as canonical)
    by_name: dict[str, dict] = {}
    for f in sorted(all_priority, key=lambda x: (0 if x["subtype"] == 4 else 1, x["subtype"])):
        by_name.setdefault(f["ibm_name"], f)
    priority_list = [by_name[k] for k in PRIORITY_IBM_FIELDS if k in by_name]
    # also include any priority-flagged extras
    for ibm, f in by_name.items():
        if ibm not in PRIORITY_IBM_FIELDS:
            priority_list.append(f)

    priority_doc = {
        "smf_type": 30,
        "note": (
            "First-wave HLASM candidates. json_key ≤16. "
            "section_base/triplet hints must be verified with IFASMFR."
        ),
        "fields": priority_list,
    }
    (args.out / "priority.json").write_text(
        json.dumps(priority_doc, indent=2) + "\n", encoding="utf-8"
    )
    (args.out / "priority_suggested.asm").write_text(
        render_priority_asm(priority_list), encoding="utf-8"
    )
    (args.out / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Wrote catalog to {args.out}")
    print(json.dumps(summary["subtypes"], indent=2))
    print(f"MAP30 mapped: {len(map30)} fields")
    print(f"Priority entries: {len(priority_list)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
