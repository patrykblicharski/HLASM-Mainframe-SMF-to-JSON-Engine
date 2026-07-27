#!/usr/bin/env python3
"""Generate MAP*.asm + SMF2JSON dispatch for all Gatherer OpenAPI type/subtype pairs."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "ref" / "openapi_spec.json"
SRC = ROOT / "src"
CATALOG = ROOT / "catalog"

# Keep richer hand-authored maps; generator skips overwriting these.
HANDCRAFTED = {
    (30, 1),
    (30, 2),
    (30, 3),
    (30, 4),
    (30, 5),
    (30, 6),
    (70, 1),
    (70, 2),
    (71, 1),
    (72, 3),
}

TITLES = {
    (30, 1): "Job start / start of other work unit",
    (30, 2): "Interval activity",
    (30, 3): "Last interval before step end",
    (30, 4): "Step total",
    (30, 5): "Job termination",
    (30, 6): "System address space",
    (70, 1): "CPU, PR/SM, and ICF activity",
    (70, 2): "Cryptographic hardware activity",
    (71, 1): "Paging activity",
    (72, 3): "Workload activity (WLM)",
    (72, 4): "Storage data",
    (72, 5): "Serialization delay",
    (73, 1): "Channel path activity",
    (74, 1): "Device activity",
    (74, 2): "XCF activity",
    (74, 3): "OMVS kernel activity",
    (74, 4): "Coupling facility activity",
    (74, 5): "Cache subsystem device activity",
    (74, 6): "HFS statistics",
    (74, 7): "FICON director statistics",
    (74, 8): "Enterprise disk system statistics",
    (74, 9): "PCI Express based function activity",
    (74, 10): "EADM statistics",
    (75, 1): "Page data set activity",
    (76, 1): "Trace activity",
    (77, 1): "Enqueue activity",
    (78, 2): "Virtual storage activity",
    (78, 3): "I/O queuing activity",
    (79, 1): "Address space state data",
    (79, 2): "Address space resource data",
    (79, 3): "Storage/processor data",
    (79, 4): "Paging activity",
    (79, 5): "Address space SRM data",
    (79, 6): "Reserve data",
    (79, 7): "Enqueue contention data",
    (79, 9): "Device activity",
    (79, 11): "Page data set activity",
    (79, 12): "Channel path activity",
    (79, 14): "I/O queuing activity",
    (79, 15): "IRLM long lock detection",
    (99, 1): "System-level / SRM / resource groups",
    (99, 2): "Service class data",
    (99, 6): "Plot / miscellaneous",
    (99, 12): "Subtype 12",
    (99, 14): "Subtype 14",
    (113, 1): "Hardware capacity / scavenging counters",
    (113, 2): "Hardware event counters",
}


def load_roots(schemas: dict) -> list[tuple[int, int, str]]:
    roots = []
    for name in schemas:
        m = re.fullmatch(r"SMF(\d+)_SUBTYPE(\d+)", name)
        if m:
            roots.append((int(m.group(1)), int(m.group(2)), name))
    roots.sort()
    return roots


def map_member(typ: int, sub: int) -> str:
    return f"MAP{typ}S{sub}"


def table_label(typ: int, sub: int) -> str:
    return f"TABLE{typ}_{sub}"


def field_line(off: str, typ: str, js: str, triplet: str | None = None) -> str:
    if triplet:
        return (
            f"         SMF_FIELD {off},TRIPLET={triplet},        X\n"
            f"               TYPE={typ},JSON={js}\n"
        )
    return f"         SMF_FIELD {off},TYPE={typ},JSON={js}\n"


def gen_rmf_style_map(typ: int, sub: int, schemas: dict, root_name: str) -> str:
    """Header + optional product section for RMF-like records (70-79)."""
    prefix = f"SMF{typ}"
    title = TITLES.get((typ, sub), f"SMF type {typ} subtype {sub}")
    props = schemas[root_name].get("properties") or {}

    lines = [
        f"* ====================================================================\n"
        f"* SMF TYPE {typ} SUBTYPE {sub} — {title}\n"
        f"* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)\n"
        f"* ====================================================================\n"
        f"{table_label(typ, sub)} SMF_START\n\n"
    ]

    # Header fields present in schema
    header_specs = [
        (f"{prefix}RTY", f"{prefix}LEN", "T_DEC1", "smf_record_type", None),
        (f"{prefix}SID", f"{prefix}LEN", "T_CHR4", "smf_system_id", None),
        (f"{prefix}TME", f"{prefix}LEN", "T_TME", "time", None),
        (f"{prefix}DTE", f"{prefix}LEN", "T_DTE", "date", None),
    ]
    if f"{prefix}SSI" in props:
        header_specs.append(
            (f"{prefix}SSI", f"{prefix}LEN", "T_CHR4", "subsystem_id", None)
        )
    if f"{prefix}STY" in props:
        header_specs.append(
            (f"{prefix}STY", f"{prefix}LEN", "T_DEC2", "subtype", None)
        )

    for ibm, base, t, js, _ in header_specs:
        if ibm in props:
            lines.append(field_line(f"{ibm}-{base}", t, js))
            lines.append("\n")

    # Product section via SMFxxPRS / SMFxxMFV
    prs = f"{prefix}PRS"
    mfv = f"{prefix}MFV"
    prd = f"{prefix}PRD"
    mvs = f"{prefix}MVS"
    product_schema = None
    for k, v in props.items():
        if isinstance(v, dict) and "$ref" in v and "PRODUCT" in v["$ref"].upper():
            product_schema = v["$ref"].rsplit("/", 1)[-1]
            break
    if prs in props and product_schema:
        pprops = schemas.get(product_schema, {}).get("properties") or {}
        # section base = first real field name if MFV absent
        base = mfv if mfv in pprops else next(iter(pprops), mfv)
        if prd in pprops:
            lines.append(
                field_line(f"{prd}-{base}", "T_CHR8", "product_name", f"{prs}-{prefix}LEN")
            )
            lines.append("\n")
        if mvs in pprops:
            lines.append(
                field_line(f"{mvs}-{base}", "T_CHR8", "mvs_level", f"{prs}-{prefix}LEN")
            )
            lines.append("\n")

    lines.append("         SMF_END\n")
    return "".join(lines)


def gen_99_map(typ: int, sub: int, schemas: dict, root_name: str) -> str:
    title = TITLES.get((typ, sub), f"SMF type {typ} subtype {sub}")
    props = schemas[root_name].get("properties") or {}
    lines = [
        f"* ====================================================================\n"
        f"* SMF TYPE {typ} SUBTYPE {sub} — {title}\n"
        f"* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)\n"
        f"* ====================================================================\n"
        f"{table_label(typ, sub)} SMF_START\n\n"
    ]
    specs = [
        ("SMF99RTY", "SMF99LEN", "T_DEC1", "smf_record_type"),
        ("SMF99SID", "SMF99LEN", "T_CHR4", "smf_system_id"),
        ("SMF99TME", "SMF99LEN", "T_TME", "time"),
        ("SMF99DTE", "SMF99LEN", "T_DTE", "date"),
        ("SMF99SSID", "SMF99LEN", "T_CHR4", "subsystem_id"),
        ("SMF99TID", "SMF99LEN", "T_DEC2", "subtype"),
    ]
    for ibm, base, t, js in specs:
        if ibm in props:
            lines.append(field_line(f"{ibm}-{base}", t, js))
            lines.append("\n")
    lines.append("         SMF_END\n")
    return "".join(lines)


def gen_113_map(typ: int, sub: int, schemas: dict, root_name: str) -> str:
    title = TITLES.get((typ, sub), f"SMF type {typ} subtype {sub}")
    props = schemas[root_name].get("properties") or {}
    lines = [
        f"* ====================================================================\n"
        f"* SMF TYPE {typ} SUBTYPE {sub} — {title}\n"
        f"* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)\n"
        f"* ====================================================================\n"
        f"{table_label(typ, sub)} SMF_START\n\n"
    ]
    specs = [
        ("SMF113RTY", "SMF113LEN", "T_DEC1", "smf_record_type"),
        ("SMF113SID", "SMF113LEN", "T_CHR4", "smf_system_id"),
        ("SMF113TME", "SMF113LEN", "T_TME", "time"),
        ("SMF113DTE", "SMF113LEN", "T_DTE", "date"),
        ("SMF113WID", "SMF113LEN", "T_CHR4", "subsystem_id"),
        ("SMF113STY", "SMF113LEN", "T_DEC2", "subtype"),
    ]
    for ibm, base, t, js in specs:
        if ibm in props:
            lines.append(field_line(f"{ibm}-{base}", t, js))
            lines.append("\n")
    lines.append("         SMF_END\n")
    return "".join(lines)


def gen_map(typ: int, sub: int, schemas: dict, root_name: str) -> str:
    if typ == 99:
        return gen_99_map(typ, sub, schemas, root_name)
    if typ == 113:
        return gen_113_map(typ, sub, schemas, root_name)
    if typ == 30:
        raise RuntimeError("type 30 maps are handcrafted")
    return gen_rmf_style_map(typ, sub, schemas, root_name)


def gen_dispatch(pairs: list[tuple[int, int]]) -> str:
    """ASM fragment for type/subtype selection (inserted into SMF2JSON)."""
    by_type: dict[int, list[int]] = {}
    for t, s in pairs:
        by_type.setdefault(t, []).append(s)
    for t in by_type:
        by_type[t].sort()

    out = []
    out.append("* --- BEGIN GENERATED DISPATCH (tools/gen_gatherer_maps.py) ---\n")
    for typ in sorted(by_type):
        subs = by_type[typ]
        out.append(f"* ---  TYPE {typ} ---\n")
        out.append(f"         CLI   5(R9),{typ}\n")
        out.append(f"         BNE   NO_{typ}\n")
        out.append(f"         LH    R1,22(,R9)        * subtype halfword\n")
        for i, sub in enumerate(subs):
            label = f"T{typ}_{sub}"
            next_label = f"T{typ}_{subs[i+1]}" if i + 1 < len(subs) else f"T{typ}_DEF"
            out.append(f"{label:<8} CHI   R1,{sub}\n")
            if i + 1 < len(subs):
                out.append(f"         BNE   {next_label}\n")
            else:
                out.append(f"         BNE   T{typ}_DEF\n")
            out.append(f"         LARL  R8,{table_label(typ, sub)}\n")
            out.append(f"         J     JSONOBJ\n")
        out.append(f"T{typ}_DEF EQU   *\n")
        if typ == 30:
            out.append(f"         LARL  R8,TABLE30        * unknown subtype default\n")
            out.append(f"         J     JSONOBJ\n")
        else:
            out.append(f"         J     NEXT_SMF          * unsupported subtype\n")
        out.append(f"NO_{typ}   EQU   *\n\n")

    # Keep non-Gatherer maps
    out.append("* ---  TYPE 80 ---\n")
    out.append("         CLI   5(R9),80\n")
    out.append("         BNE   NO_80\n")
    out.append("         LARL  R8,TABLE80\n")
    out.append("         J     JSONOBJ\n")
    out.append("NO_80    EQU   *\n\n")
    out.append("* ---  TYPE 89 ---\n")
    out.append("         CLI   5(R9),89\n")
    out.append("         BNE   NO_89\n")
    out.append("         LARL  R8,TABLE89\n")
    out.append("         J     JSONOBJ\n")
    out.append("NO_89    J     NEXT_SMF\n")
    out.append("* --- END GENERATED DISPATCH ---\n")
    return "".join(out)


def gen_copy_list(pairs: list[tuple[int, int]]) -> str:
    lines = [
        "*--- Mapping Tables ---*\n",
        "         DS    0F                  * Alignement\n",
        "         COPY  TYPES               * T_* datatype constants\n",
        "         COPY  MAP30               * type 30 default\n",
    ]
    # type 30 subtype maps first for readability
    for t, s in pairs:
        if t == 30:
            lines.append(f"         COPY  {map_member(t, s)}\n")
    for t, s in pairs:
        if t != 30:
            lines.append(f"         COPY  {map_member(t, s)}\n")
    lines.append("         COPY  MAP80\n")
    lines.append("         COPY  MAP89\n")
    return "".join(lines)


def patch_smf2json(dispatch: str, copy_list: str, types: list[int]) -> None:
    path = SRC / "SMF2JSON.asm"
    text = path.read_text(encoding="utf-8")

    # IFASMFR list
    ifasmfr_types = sorted(set(types) | {80, 89})
    ifasmfr = "         IFASMFR (" + ",".join(str(t) for t in ifasmfr_types) + ")  * IBM SMF Record Mappings\n"
    text = re.sub(r"         IFASMFR \([^)]+\)[^\n]*\n", ifasmfr, text, count=1)

    # Purpose line
    text = re.sub(
        r"\* PURPOSE: CONVERT SMF RECORDS[^\n]*\n",
        f"* PURPOSE: CONVERT SMF RECORDS ({'/'.join(str(t) for t in ifasmfr_types)}) TO JSON *\n",
        text,
        count=1,
    )

    # Replace dispatch block through JSONOBJ
    begin = "* --- BEGIN GENERATED DISPATCH"
    end = "* --- END GENERATED DISPATCH ---"
    if begin in text and end in text:
        pre, rest = text.split(begin, 1)
        _, post = rest.split(end, 1)
        # keep a single newline before whatever follows the end marker
        text = pre + dispatch + post.lstrip("\n")
        if not text[len(pre) + len(dispatch) :].startswith("\n"):
            pass
    else:
        m = re.search(
            r"\* ---  TYPE 30.*?\nNO_89\s+J\s+NEXT_SMF\s*\n",
            text,
            re.S,
        )
        if not m:
            raise SystemExit("Could not locate dispatch section in SMF2JSON.asm")
        text = text[: m.start()] + dispatch + "\n" + text[m.end() :]

    # Replace mapping COPY block
    m = re.search(
        r"\*--- Mapping Tables ---\*.*?(?=DYNAMIC_WORK DSECT)",
        text,
        re.S,
    )
    if not m:
        raise SystemExit("Could not locate mapping tables COPY block")
    text = text[: m.start()] + copy_list + "\n" + text[m.end() :]

    path.write_text(text, encoding="utf-8")


def main() -> int:
    spec = json.loads(OPENAPI.read_text(encoding="utf-8"))
    schemas = spec["components"]["schemas"]
    roots = load_roots(schemas)
    pairs = [(t, s) for t, s, _ in roots]

    generated = []
    for typ, sub, root_name in roots:
        if (typ, sub) in HANDCRAFTED:
            generated.append(
                {
                    "type": typ,
                    "subtype": sub,
                    "table": table_label(typ, sub) if typ != 30 or True else table_label(typ, sub),
                    "map": f"src/{map_member(typ, sub)}.asm",
                    "title": TITLES.get((typ, sub), ""),
                    "handcrafted": True,
                }
            )
            continue
        body = gen_map(typ, sub, schemas, root_name)
        out = SRC / f"{map_member(typ, sub)}.asm"
        out.write_text(body, encoding="utf-8")
        generated.append(
            {
                "type": typ,
                "subtype": sub,
                "table": table_label(typ, sub),
                "map": f"src/{map_member(typ, sub)}.asm",
                "title": TITLES.get((typ, sub), ""),
                "handcrafted": False,
            }
        )

    # Fix table names for type 30 handcrafted
    for g in generated:
        if g["type"] == 30:
            g["table"] = f"TABLE30_{g['subtype']}"

    dispatch = gen_dispatch(pairs)
    copy_list = gen_copy_list(pairs)
    types = sorted({t for t, _ in pairs})
    patch_smf2json(dispatch, copy_list, types)

    planned = {
        "note": "All Gatherer OpenAPI type/subtype pairs wired in HLASM (+ MAP80/MAP89)",
        "source": "ref/openapi_spec.json",
        "count": len(generated),
        "engine_types": [
            "T_CHR1",
            "T_CHR2",
            "T_CHR4",
            "T_CHR8",
            "T_CHR20",
            "T_DEC1",
            "T_DEC2",
            "T_DEC4",
            "T_DTE",
            "T_TME",
            "T_RS_STR",
            "T_HEX2",
        ],
        "pairs": generated,
        "also_supported_non_gatherer": [
            {"type": 80, "map": "src/MAP80.asm", "table": "TABLE80"},
            {"type": 89, "map": "src/MAP89.asm", "table": "TABLE89"},
        ],
    }
    CATALOG.mkdir(exist_ok=True)
    (CATALOG / "planned_subtypes.json").write_text(
        json.dumps(planned, indent=2) + "\n", encoding="utf-8"
    )

    # Update extract JCL TYPE lists
    type_list = ",".join(str(t) for t in sorted(set(types) | {80, 89, 101, 102}))
    for jcl in (ROOT / "jcl" / "SMFEXTRT.jcl", ROOT / "jcl" / "SMFEXTRL.jcl"):
        text = jcl.read_text(encoding="utf-8")
        text2 = re.sub(
            r"OUTDD\(DUMPOUT,TYPE\([^)]+\)\)",
            f"OUTDD(DUMPOUT,TYPE({type_list}))",
            text,
        )
        jcl.write_text(text2, encoding="utf-8")

    print(f"Pairs: {len(pairs)}")
    print(f"Generated maps: {sum(1 for g in generated if not g['handcrafted'])}")
    print(f"Handcrafted kept: {sum(1 for g in generated if g['handcrafted'])}")
    print(f"IFASMFR types: {types}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
