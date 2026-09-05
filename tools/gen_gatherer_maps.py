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


# Prefer stable JSON keys for common IBM names.
JSON_KEY_HINTS = {
    "SMF70LPM": "lpar_name",
    "SMF70CID": "cpu_id",
    "SMF70TYP": "cpu_type",
    "SMF74NUM": "device_num",
    "SMF74LCU": "lcu_num",
    "SMF74SSC": "ssch_count",
    "SMF74CNN": "connect_time",
    "SMF74PEN": "pending_time",
    "SMF77QNM": "major_name",
    "SMF77WTM": "wait_min",
    "SMF77WTX": "wait_max",
    "SMF77WTT": "wait_total",
    "SMF71PIN": "page_ins",
    "SMF71POT": "page_outs",
    "SMF71SIN": "swap_ins",
    "SMF71SOT": "swap_outs",
    "SMF71AVF": "avg_frames",
    "R723MCNM": "class_name",
    "R723MCPG": "period_count",
    "R723CPER": "period_number",
    "R723CCDE": "cpu_delay",
}


def field_line(off: str, typ: str, js: str, triplet: str | None = None) -> str:
    if triplet:
        return (
            f"         SMF_FIELD {off},TRIPLET={triplet},        X\n"
            f"               TYPE={typ},JSON={js}\n"
        )
    return f"         SMF_FIELD {off},TYPE={typ},JSON={js}\n"


def hlasm_type_for(node: dict) -> str | None:
    dt = (node.get("x-zml-datatype") or "").upper()
    sz = node.get("x-zml-size")
    fmt = node.get("format")
    try:
        sz_i = int(sz) if sz is not None else None
    except (TypeError, ValueError):
        sz_i = None
    if dt == "CHARACTER":
        return {1: "T_CHR1", 2: "T_CHR2", 4: "T_CHR4", 8: "T_CHR8", 20: "T_CHR20"}.get(sz_i)
    if dt in {"UNSIGNED", "SIGNED"}:
        if fmt == "time" and sz_i == 4:
            return "T_TME"
        return {1: "T_DEC1", 2: "T_DEC2", 4: "T_DEC4"}.get(sz_i)
    if dt == "PACKED_DATE_2":
        return "T_DTE"
    if dt == "HEX_STR" and sz_i == 2:
        return "T_HEX2"
    return None


# Common RMF/product suffix → stable JSON key (after stripping SMFnn/Rnnn prefix).
SUFFIX_KEY_HINTS = {
    "PRD": "product_name",
    "MVS": "mvs_level",
    "SNM": "system_name",
    "XNM": "sysplex_name",
    "SAM": "sample_count",
    "SRL": "rmf_release",
    "DAT": "interval_date",
}


def make_json_key(ibm: str, used: set[str]) -> str:
    if ibm in JSON_KEY_HINTS:
        key = JSON_KEY_HINTS[ibm]
    else:
        tail = re.sub(r"^(SMF\d+|R\d+)", "", ibm)
        tail = re.sub(r"[^A-Za-z0-9]", "", tail) or ibm
        key = SUFFIX_KEY_HINTS.get(tail.upper(), tail.lower())[:16]
        if not re.match(r"^[a-z]", key):
            key = ("f" + key)[:16]
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


def iter_section_schemas(props: dict) -> list[tuple[str, str]]:
    """Return (prop_name, schema_name) for section objects / maps."""
    out = []
    for key, node in props.items():
        if not isinstance(node, dict):
            continue
        if "$ref" in node:
            out.append((key, node["$ref"].rsplit("/", 1)[-1]))
        elif node.get("type") == "object":
            ap = node.get("additionalProperties")
            if isinstance(ap, dict) and "$ref" in ap:
                out.append((key, ap["$ref"].rsplit("/", 1)[-1]))
        elif node.get("type") == "array" and isinstance(node.get("items"), dict):
            items = node["items"]
            if "$ref" in items:
                out.append((key, items["$ref"].rsplit("/", 1)[-1]))
    return out


def offset_triplet_fields(props: dict) -> dict[str, str]:
    """Map offset-field name -> description for meta OFFSET TO ... fields."""
    found = {}
    for key, node in props.items():
        if not isinstance(node, dict) or "$ref" in node:
            continue
        desc = (node.get("description") or "").upper()
        if node.get("x-zdg-is-meta") and "OFFSET" in desc:
            found[key] = desc
    return found


_GENERIC_OFFSET_STOP = {
    "OFFSET",
    "TO",
    "THE",
    "FROM",
    "BEGINNING",
    "OF",
    "RECORD",
    "INCLUDING",
    "RDW",
    "A",
    "AN",
    "SECTION",
    "SECTIONS",
}


def offset_content_tokens(desc: str) -> set[str]:
    tokens = set(re.findall(r"[A-Z]+", desc.upper())) - _GENERIC_OFFSET_STOP
    if tokens & {"CNTL", "CTRL"}:
        tokens.add("CONTROL")
    return tokens


def match_triplet(section_schema: str, offsets: dict[str, str]) -> str | None:
    """Best-effort OFFSET-field match for a section schema name."""
    name_u = section_schema.upper()
    if "PRODUCT" in name_u:
        for name, desc in offsets.items():
            if name.endswith("PRS") or "PRODUCT" in desc.upper():
                return name

    # Type 99/113: OpenAPI "header" ≈ SDS generic "data section" triplet only.
    if "HEADER" in name_u and "SELF" not in name_u:
        for name, desc in offsets.items():
            content = offset_content_tokens(desc)
            if content == {"DATA"} or content == {"DATA", "SECTION"}:
                return name
            # 113: "OFFSET OF DATA SECTION FROM BEGINNING OF RECORD"
            if content == {"DATA"}:
                return name

    tokens = set(
        t
        for t in re.findall(r"[A-Z]+", name_u)
        if t not in {"SMF", "SUBTYPE", "SECTION", "AREA", "SELF", "DEFINING"}
        and not t.isdigit()
    )
    has_control = bool(tokens & {"CONTROL", "CNTL", "CTRL"})
    has_data = "DATA" in tokens

    best_name = None
    best_score = 0
    for name, desc in offsets.items():
        content = offset_content_tokens(desc)
        # Generic SDS "data section" must not match every *DATA* payload schema.
        if content <= {"DATA"}:
            continue

        score = len(tokens & content)
        desc_is_control = bool(content & {"CONTROL", "CNTL", "CTRL"})
        desc_is_data = "DATA" in content and not desc_is_control

        if has_control:
            if desc_is_control:
                score += 3
            elif desc_is_data:
                score -= 2
        elif has_data:
            if desc_is_data:
                score += 3
            elif desc_is_control:
                score -= 2

        if score > best_score:
            best_score = score
            best_name = name
    return best_name if best_score >= 1 else None


def section_base_label(section_props: dict) -> str | None:
    """First DSECT field name (IFASMFR section start), including meta/packed heads."""
    for key, node in section_props.items():
        if not isinstance(node, dict) or "$ref" in node:
            continue
        if isinstance(node.get("additionalProperties"), dict):
            continue
        # Nested OpenAPI object without a leaf datatype is not a DSECT field
        if node.get("type") == "object" and not node.get("x-zml-datatype"):
            continue
        return key
    return None


def select_section_fields(section_props: dict) -> list[tuple[str, str]]:
    """Return list of (ibm_name, T_*) supported fields (uncapped)."""
    hinted: list[tuple[str, str]] = []
    other: list[tuple[str, str]] = []
    for key, node in section_props.items():
        if not isinstance(node, dict) or "$ref" in node:
            continue
        if node.get("x-zdg-is-meta"):
            continue
        t = hlasm_type_for(node)
        if not t:
            continue
        (hinted if key in JSON_KEY_HINTS else other).append((key, t))
    return hinted + other


def fixed_triplet_offsets(root_props: dict, schemas: dict) -> dict[str, str]:
    """
    OFFSET fields stored at a compile-time-fixed place in the record.

    Root SDS triplets (RMF) and type 99/113 self-defining section triplets are
    safe for SMF_FIELD TRIPLET=label-SMFxxLEN. Triplets that live inside a
    relocatable section are not — the engine reads them via a fixed AL4 offset.
    """
    pool = offset_triplet_fields(root_props)
    for _prop, section_schema in iter_section_schemas(root_props):
        if "SELF_DEFINING" not in section_schema.upper():
            continue
        section_props = schemas.get(section_schema, {}).get("properties") or {}
        pool.update(offset_triplet_fields(section_props))
    return pool


def walk_section_targets(
    root_props: dict, schemas: dict
) -> list[tuple[str, dict[str, str]]]:
    """BFS over OpenAPI sections; every target shares the fixed triplet pool."""
    fixed = fixed_triplet_offsets(root_props, schemas)
    queue: list[str] = []
    for _prop, section_schema in iter_section_schemas(root_props):
        queue.append(section_schema)

    seen: set[str] = set()
    ordered: list[tuple[str, dict[str, str]]] = []
    while queue:
        section_schema = queue.pop(0)
        if section_schema in seen:
            continue
        seen.add(section_schema)
        section_props = schemas.get(section_schema, {}).get("properties") or {}
        ordered.append((section_schema, fixed))
        # Discover nested payload schemas (type 99/113), but do not adopt their
        # inner OFFSET metas as TRIPLET sources.
        for _prop, child in iter_section_schemas(section_props):
            queue.append(child)
    return ordered


def header_field_specs(typ: int, props: dict) -> list[tuple[str, str, str, str]]:
    """Common SMF header JSON fields for a type."""
    prefix = f"SMF{typ}"
    specs = [
        (f"{prefix}RTY", f"{prefix}LEN", "T_DEC1", "smf_record_type"),
        (f"{prefix}SID", f"{prefix}LEN", "T_CHR4", "smf_system_id"),
        (f"{prefix}TME", f"{prefix}LEN", "T_TME", "time"),
        (f"{prefix}DTE", f"{prefix}LEN", "T_DTE", "date"),
    ]
    if typ == 99:
        specs.extend(
            [
                ("SMF99SSID", "SMF99LEN", "T_CHR4", "subsystem_id"),
                ("SMF99TID", "SMF99LEN", "T_DEC2", "subtype"),
            ]
        )
    elif typ == 113:
        specs.extend(
            [
                ("SMF113WID", "SMF113LEN", "T_CHR4", "subsystem_id"),
                ("SMF113STY", "SMF113LEN", "T_DEC2", "subtype"),
            ]
        )
    else:
        if f"{prefix}SSI" in props:
            specs.append((f"{prefix}SSI", f"{prefix}LEN", "T_CHR4", "subsystem_id"))
        if f"{prefix}STY" in props:
            specs.append((f"{prefix}STY", f"{prefix}LEN", "T_DEC2", "subtype"))
    return specs


def gen_rmf_style_map(typ: int, sub: int, schemas: dict, root_name: str) -> str:
    """Header + product + supported fields from mapped sections."""
    prefix = f"SMF{typ}"
    title = TITLES.get((typ, sub), f"SMF type {typ} subtype {sub}")
    props = schemas[root_name].get("properties") or {}
    used_keys: set[str] = set()

    lines = [
        f"* ====================================================================\n"
        f"* SMF TYPE {typ} SUBTYPE {sub} — {title}\n"
        f"* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)\n"
        f"* All supported T_* section fields (no per-section caps)\n"
        f"* ====================================================================\n"
        f"{table_label(typ, sub)} SMF_START\n\n"
    ]

    for ibm, base, t, js in header_field_specs(typ, props):
        if ibm in props:
            used_keys.add(js)
            lines.append(field_line(f"{ibm}-{base}", t, js))
            lines.append("\n")

    used_triplets: set[str] = set()
    for section_schema, offsets in walk_section_targets(props, schemas):
        # Skip pure SDS wrappers (no payload fields)
        if "SELF_DEFINING" in section_schema.upper():
            continue
        section_props = schemas.get(section_schema, {}).get("properties") or {}
        if not section_props:
            continue
        triplet = match_triplet(section_schema, offsets)
        if not triplet or triplet in used_triplets:
            continue
        base = section_base_label(section_props)
        if not base:
            continue
        fields = select_section_fields(section_props)
        if not fields:
            continue
        used_triplets.add(triplet)
        lines.append(f"* --- section {section_schema} via {triplet} ---\n")
        for ibm, t in fields:
            js = make_json_key(ibm, used_keys)
            lines.append(
                field_line(f"{ibm}-{base}", t, js, f"{triplet}-{prefix}LEN")
            )
            lines.append("\n")

    lines.append("         SMF_END\n")
    return "".join(lines)


def gen_map(typ: int, sub: int, schemas: dict, root_name: str) -> str:
    if typ == 30:
        raise RuntimeError("type 30 maps are handcrafted")
    return gen_rmf_style_map(typ, sub, schemas, root_name)


def discover_extra_maps() -> dict[int, list[int]]:
    """Subtype lists for maps produced by tools/gen_extra_maps.py (if present)."""
    found: dict[int, list[int]] = {}
    if (SRC / "MAP14.asm").exists():
        found[14] = []
    if (SRC / "MAP15.asm").exists():
        found[15] = []
    for typ in (42, 119):
        subs = sorted(
            int(m.group(1))
            for p in SRC.glob(f"MAP{typ}S*.asm")
            if (m := re.match(rf"MAP{typ}S(\d+)\.asm", p.name))
        )
        if subs or (typ == 42 and (SRC / "MAP42.asm").exists()):
            found[typ] = subs
    return found


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

    # Preserve non-Gatherer maps from gen_extra_maps.py when present
    extras = discover_extra_maps()
    for typ in sorted(extras):
        subs = extras[typ]
        out.append(f"* ---  TYPE {typ} ---\n")
        out.append(f"         CLI   5(R9),{typ}\n")
        out.append(f"         BNE   NO_{typ}\n")
        if not subs:
            out.append(f"         LARL  R8,TABLE{typ}\n")
            out.append("         J     JSONOBJ\n")
        else:
            out.append("         LH    R1,22(,R9)        * subtype halfword\n")
            for i, sub in enumerate(subs):
                label = f"T{typ}_{sub}"
                next_label = f"T{typ}_{subs[i+1]}" if i + 1 < len(subs) else f"T{typ}_DEF"
                out.append(f"{label:<8} CHI   R1,{sub}\n")
                out.append(f"         BNE   {next_label}\n")
                out.append(f"         LARL  R8,TABLE{typ}_{sub}\n")
                out.append("         J     JSONOBJ\n")
            out.append(f"T{typ}_DEF EQU   *\n")
            if typ == 42 and (SRC / "MAP42.asm").exists():
                out.append("         LARL  R8,TABLE42\n")
                out.append("         J     JSONOBJ\n")
            else:
                out.append("         J     NEXT_SMF          * unsupported subtype\n")
        out.append(f"NO_{typ}   EQU   *\n\n")

    # Keep classic non-Gatherer maps
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
    extras = discover_extra_maps()
    if 14 in extras:
        lines.append("         COPY  MAP14\n")
    if 15 in extras:
        lines.append("         COPY  MAP15\n")
    if 42 in extras:
        if (SRC / "MAP42.asm").exists():
            lines.append("         COPY  MAP42\n")
        for s in extras[42]:
            lines.append(f"         COPY  MAP42S{s}\n")
    for t, s in pairs:
        if t != 30:
            lines.append(f"         COPY  {map_member(t, s)}\n")
    if 119 in extras:
        for s in extras[119]:
            lines.append(f"         COPY  MAP119S{s}\n")
    lines.append("         COPY  MAP80\n")
    lines.append("         COPY  MAP89\n")
    return "".join(lines)


def patch_smf2json(dispatch: str, copy_list: str, types: list[int]) -> None:
    path = SRC / "SMF2JSON.asm"
    text = path.read_text(encoding="utf-8")

    # IFASMFR list
    extras = discover_extra_maps()
    ifasmfr_types = sorted(set(types) | {80, 89} | set(extras))
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
            {"type": 14, "map": "src/MAP14.asm", "table": "TABLE14"},
            {"type": 15, "map": "src/MAP15.asm", "table": "TABLE15"},
            {"type": 42, "map": "src/MAP42*.asm", "note": "DFSMS catalog via gen_extra_maps"},
            {"type": 80, "map": "src/MAP80.asm", "table": "TABLE80"},
            {"type": 89, "map": "src/MAP89.asm", "table": "TABLE89"},
            {"type": 119, "map": "src/MAP119S*.asm", "note": "TCP/IP via gen_extra_maps"},
        ],
    }
    CATALOG.mkdir(exist_ok=True)
    (CATALOG / "planned_subtypes.json").write_text(
        json.dumps(planned, indent=2) + "\n", encoding="utf-8"
    )

    # Update extract JCL TYPE lists
    extras = discover_extra_maps()
    type_list = ",".join(
        str(t) for t in sorted(set(types) | {80, 89, 101, 102} | set(extras))
    )
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
    print(f"IFASMFR types: {sorted(set(types) | {80, 89} | set(extras))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
