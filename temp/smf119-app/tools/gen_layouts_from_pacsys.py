#!/usr/bin/env python3
"""Generate Python StructLayout modules from PACSYS JSON specs."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_DIR = Path(__file__).resolve().parent / "pacsys_json"
OUT = ROOT / "parser" / "layouts"

# Map PACSYS triplet pointer name -> (section_key, layout_name hint)
TRIPLET_MAP = {
    "HEADER": None,  # skip — we already have header_layouts
    "SMF119IDOff": None,  # Ident already mapped
    "SMF119S1Off": ("S1", 1),
    "SMF119S2Off": ("S2", 2),
    "SMF119S3Off": ("S3", 3),
    "SMF119S4Off": ("S4", 4),
    "SMF119S5Off": ("S5", 5),
    "SMF119S6Off": ("S6", 6),
    "SMF119S7Off": ("S7", 7),
    "SMF119S50_IDOff": None,
    "SMF119S50_S1Off": ("S1", 1),
    "SMF119S50_S2Off": ("S2", 2),
    "SMF119S50_S3Off": ("S3", 3),
    "SMF119S50_S4Off": ("S4", 4),
}


def kind_for(field: dict) -> tuple[str, dict]:
    """Return (constructor_expr_args) style hint."""
    name = field["name"]
    length = field["length"]
    fmt = (field["format"] or "").lower()
    desc = field["description"].replace("\\", "\\\\").replace('"', '\\"')
    reserved = field.get("reserved", False)

    if reserved:
        try:
            n = int(length)
        except ValueError:
            n = 1
        return f'RES("{name}", {n})'

    if length == "VARIABLE":
        # Variable EBCDIC — size comes from triplet Len at decode time
        return f'VAR_EBCDIC("{name}", "{desc}")'

    try:
        n = int(length)
    except ValueError:
        n = 1

    if fmt == "ebcdic":
        return f'CHAR("{name}", {n}, "{desc}")'
    if fmt == "packed":
        return f'BYTES("{name}", {n}, "{desc}", decode="date_hex")'
    if fmt == "floating":
        return f'BYTES("{name}", {n}, "{desc}", decode="hex")'

    # Binary by size
    # Heuristic: 16-byte fields named *IP / *Addr often ipv6mapped
    lname = name.lower()
    if n == 16 and ("ip" in lname or "addr" in lname) and "stck" not in lname:
        return f'IPV6MAPPED("{name}", "{desc}")'
    if n == 4 and ("ip" in lname and "ipv6" not in lname) and "stck" not in lname and "conn" not in lname:
        # careful — many 4-byte counters; only if clearly address
        if lname.endswith("ip") or "addr" in lname:
            return f'IPV4("{name}", "{desc}")'

    if n == 1:
        return f'U8("{name}", "{desc}")'
    if n == 2:
        return f'U16("{name}", "{desc}")'
    if n == 4:
        return f'U32("{name}", "{desc}")'
    if n == 8:
        return f'U64("{name}", "{desc}")'
    return f'BYTES("{name}", {n}, "{desc}")'


def _common_field_prefix(fields: list[dict]) -> str:
    names = [
        f["name"]
        for f in fields
        if f["name"].startswith("SMF119")
        and not f["name"].startswith("SMF119TI")
        and not f["name"].startswith("_")
        and not f.get("reserved")
    ]
    if not names:
        return ""
    prefix = names[0]
    for n in names[1:]:
        while prefix and not n.startswith(prefix):
            prefix = prefix[:-1]
        if not prefix:
            break
    # Trim to last underscore boundary so we don't leave a partial token
    if "_" in prefix:
        prefix = prefix[: prefix.rfind("_") + 1].rstrip("_") if prefix.endswith("_") else prefix
        # Prefer stopping after structural token (e.g. SMF119SC_TLS)
        m = re.match(r"(SMF119[A-Za-z0-9]+_[A-Za-z0-9]+)", prefix)
        if m:
            return m.group(1)
    return prefix.rstrip("_")


def layout_name_from_fields(fields: list[dict], subtype: int, slot: int) -> str:
    # Prefer known multi-token section prefixes (longest first)
    known = (
        "SMF119AP_TTTel",
        "SMF119AP_TTTTLS",
        "SMF119AP_TTAPPL",
        "SMF119AP_TTFLTR",
        "SMF119AP_TT",
        "SMF119AP_TI",
        "SMF119AP_TSIP",
        "SMF119AP_TSTC",
        "SMF119AP_TSUD",
        "SMF119AP_TSIC",
        "SMF119AP_TSP6",
        "SMF119AP_TSC6",
        "SMF119AP_TSST",
        "SMF119IS_IFIP",
        "SMF119IS_IF",
        "SMF119SP_TC",
        "SMF119SP_UD",
        "SMF119TC_ST",
        "SMF119UD_UC",
        "SMF119FT_FCSO",
        "SMF119FT_FCSC",
        "SMF119FT_FCLM",
        "SMF119FT_FCFileName",
        "SMF119FT_FCUserID",
        "SMF119FT_FC",
        "SMF119FT_FSHostname",
        "SMF119FT_FSFileName1",
        "SMF119FT_FSFileName2",
        "SMF119FT_FS",
        "SMF119FT_FFSC",
        "SMF119FT_FF",
        "SMF119TN_NI",
        "SMF119TN_NTR",
        "SMF119TN_NTB",
        "SMF119TN_NT",
        "SMF119TN_CI",
        "SMF119TN_CT",
        "SMF119SC_IPFlt",
        "SMF119SC_IPSec",
        "SMF119SC_TLS",
        "SMF119SC_SSH",
        "SMF119SC_DN",
        "SMF119SC_SA",
        "SMF119SS_IPSec",
        "SMF119SS_TLS",
        "SMF119SS_SSH",
        "SMF119SS_DN",
        "SMF119SS_SA",
        "SMF119ML_",
    )
    for f in fields:
        n = f["name"]
        if n.startswith("SMF119") and not n.startswith("SMF119TI") and not n.startswith("_"):
            for prefix in known:
                if n.startswith(prefix):
                    return prefix.rstrip("_") if prefix.endswith("_") else prefix
    common = _common_field_prefix(fields)
    if common:
        return common
    return f"SMF119_ST{subtype}_S{slot}"


def fill_gaps(fields: list[dict]) -> list[dict]:
    """Insert RES gaps so packed offsets are contiguous from 0."""
    if not fields:
        return fields
    ordered = sorted(fields, key=lambda f: f["offset"])
    out = []
    cursor = 0
    for f in ordered:
        off = f["offset"]
        if off > cursor:
            out.append(
                {
                    "offset": cursor,
                    "name": f"_pad_{cursor}",
                    "length": str(off - cursor),
                    "format": "binary",
                    "description": "Padding",
                    "reserved": True,
                }
            )
            cursor = off
        if off < cursor:
            # overlapping / duplicate (e.g. STCK D/T aliases) — skip later alias
            continue
        out.append(f)
        length = f["length"]
        if length == "VARIABLE":
            # don't advance — variable sections are whole-triplet
            cursor = off
        else:
            cursor = off + int(length)
    return out


def generate_module(subtype: int, data: dict) -> str | None:
    blocks = []
    registry_entries = []  # (triplet_index, layout_var, key)

    for sec in data["sections"]:
        trip = sec["triplet"]
        mapped = TRIPLET_MAP.get(trip, ("?", -1))
        if mapped is None:
            continue
        key, slot = mapped
        fields = fill_gaps(sec["fields"])
        # Skip if only Ident-like (already have) — S1+ only
        if all(f["name"].startswith("SMF119TI") or f["name"].startswith("_") for f in fields):
            continue
        base_name = layout_name_from_fields(fields, subtype, slot)
        layout_struct = f"{base_name}_S{slot}"
        var = layout_struct.replace("SMF119", "").replace("__", "_")
        var = re.sub(r"[^A-Za-z0-9_]", "_", var)
        if not var or var[0].isdigit():
            var = "L_" + var

        field_lines = []
        for f in fields:
            field_lines.append("        " + kind_for(f) + ",")

        # Detect var_ebcdic whole-section
        is_var = any(f["length"] == "VARIABLE" for f in fields)
        if is_var and len(fields) == 1:
            f = fields[0]
            desc = f["description"][:120].replace("\\", "\\\\").replace('"', '\\"')
            blocks.append(
                f'{var} = build_layout(\n'
                f'    "{layout_struct}",\n'
                f'    [\n'
                f'        VAR_EBCDIC("{f["name"]}", "{desc}"),\n'
                f'    ],\n'
                f'    description="{layout_struct} (variable length)",\n'
                f'    variable=True,\n'
                f')\n'
            )
        else:
            blocks.append(
                f'{var} = build_layout(\n'
                f'    "{layout_struct}",\n'
                f'    [\n' + "\n".join(field_lines) + "\n"
                f'    ],\n'
                f'    description="{layout_struct}",\n'
                f')\n'
            )
        registry_entries.append((slot, var, key, layout_struct))

    if not blocks:
        return None

    body = "\n".join(blocks)
    exports = ", ".join(e[1] for e in registry_entries)
    reg_lines = ",\n".join(
        f"    SectionSlot(triplet_index={slot}, key={key!r}, layout={var})"
        for slot, var, key, _ in registry_entries
    )
    return f'''"""Auto-generated layouts for SMF 119 subtype {subtype} (from PACSYS offset tables)."""
from __future__ import annotations

from ..layout import (
    BYTES,
    CHAR,
    IPV4,
    IPV6MAPPED,
    RES,
    U8,
    U16,
    U32,
    U64,
    VAR_EBCDIC,
    build_layout,
)
from ..registry import SectionSlot

{body}
SECTION_SLOTS = [
{reg_lines},
]

__all__ = [{", ".join(repr(e[1]) for e in registry_entries)}, "SECTION_SLOTS"]
'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "__init__.py").write_text('"""Per-subtype SMF 119 section layouts."""\n')
    generated = {}
    for path in sorted(JSON_DIR.glob("st*.json")):
        if path.name == "summary.json":
            continue
        data = json.loads(path.read_text())
        subtype = data["subtype"]
        mod = generate_module(subtype, data)
        if not mod:
            print(f"skip {subtype}")
            continue
        out = OUT / f"st{subtype:02d}.py"
        out.write_text(mod)
        generated[subtype] = out.name
        print(f"wrote {out.name}")
    (OUT / "_generated.json").write_text(json.dumps(generated, indent=2))


if __name__ == "__main__":
    main()
