#!/usr/bin/env python3
"""Generate smf2json SMF 119 subtype section maps from temp/smf119-app layouts.

Run from the repo (any cwd):

    python python/tools/gen_smf119_maps.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
APP = REPO / "temp" / "smf119-app"
OUT = REPO / "python" / "smf2json" / "maps" / "smf119_generated.py"

sys.path.insert(0, str(APP))

from parser import layouts_loader  # noqa: E402, F401  — registers stXX slots
from parser.layout import field_size  # noqa: E402
from parser.registry import SUBTYPE_SECTIONS  # noqa: E402
from parser.subtypes import SUBTYPES  # noqa: E402

# Absolute offset of Ident triplet (SMF119IDOff) from RDW / SMF119LEN.
IDENT_TRIPLET = 28

# json_key overrides: keep subtype-1 GUI/test names and share them on sibling records.
IBM_JSON_KEYS = {
    "SMF119AP_TIRName": "resource_name",
    "SMF119AP_TIConnID": "connection_id",
    "SMF119AP_TISubTask": "subtask_tcb",
    "SMF119AP_TIRIP": "remote_ip",
    "SMF119AP_TILIP": "local_ip",
    "SMF119AP_TIRPort": "remote_port",
    "SMF119AP_TILPort": "local_port",
    "SMF119AP_TITime": "conn_time",
    "SMF119AP_TIDate": "conn_date",
    "SMF119AP_TISTCK": "conn_stck",
    "SMF119AP_TISTCK_T": "conn_stck",
    "SMF119AP_TTRName": "resource_name",
    "SMF119AP_TTConnID": "connection_id",
    "SMF119AP_TTSubtask": "subtask_tcb",
    "SMF119AP_TTTermCode": "term_code",
    "SMF119AP_TTRIP": "remote_ip",
    "SMF119AP_TTLIP": "local_ip",
    "SMF119AP_TTRPort": "remote_port",
    "SMF119AP_TTLPort": "local_port",
    "SMF119AP_TTSTime": "conn_time",
    "SMF119AP_TTSDate": "conn_date",
    "SMF119AP_TTETime": "conn_end_time",
    "SMF119AP_TTEDate": "conn_end_date",
    "SMF119AP_TTInBytes": "in_bytes",
    "SMF119AP_TTOutBytes": "out_bytes",
    "SMF119AP_TTInSeg": "in_segments",
    "SMF119AP_TTOutSeg": "out_segments",
    "SMF119AP_TTStatus": "socket_status",
    "SMF119UD_UCRname": "resource_name",
    "SMF119UD_UCConnID": "connection_id",
    "SMF119UD_UCSubTask": "subtask_tcb",
    "SMF119UD_UCRIP": "remote_ip",
    "SMF119UD_UCLIP": "local_ip",
    "SMF119UD_UCRPort": "remote_port",
    "SMF119UD_UCLPort": "local_port",
    "SMF119UD_UCOTime": "conn_time",
    "SMF119UD_UCODate": "conn_date",
    "SMF119UD_UCCTime": "conn_end_time",
    "SMF119UD_UCCDate": "conn_end_date",
    "SMF119UD_UCInBytes": "in_bytes",
    "SMF119UD_UCOutBytes": "out_bytes",
    "SMF119UD_UCInDgrams": "in_datagrams",
    "SMF119UD_UCOutDgrams": "out_datagrams",
    "SMF119FT_FCCmd": "ftp_cmd",
    "SMF119FT_FCFileName": "file_name",
    "SMF119FT_FCBytes": "bytes_transferred",
    "SMF119FT_FCRUser": "remote_user",
    "SMF119FT_FCLUser": "local_user",
    "SMF119FT_FSCmd": "ftp_cmd",
    "SMF119FT_FSFileName1": "file_name",
    "SMF119FT_FSBytes": "bytes_transferred",
    "SMF119FT_FSSUser": "server_user",
    "SMF119FT_FSHostname": "hostname",
}


def triplet_offset(triplet_index: int) -> int:
    """Ident is triplet 0 at +28; S1 is triplet 1 at +36, etc."""
    return IDENT_TRIPLET + triplet_index * 8


def ibm_to_key(name: str) -> str:
    if name in IBM_JSON_KEYS:
        return IBM_JSON_KEYS[name]
    s = re.sub(r"^SMF119(?:[A-Z]{1,2})?_", "", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = s.replace("-", "_").replace(" ", "_")
    s = re.sub(r"_+", "_", s).strip("_").lower()
    if not s:
        s = re.sub(r"[^a-z0-9_]+", "_", name.lower()).strip("_")
    if s[0].isdigit():
        s = "f_" + s
    return s


def unique_key(name: str, used: set[str]) -> str:
    base = ibm_to_key(name)
    key = base
    n = 2
    while key in used:
        key = f"{base}_{n}"
        n += 1
    used.add(key)
    return key


def map_field(f, used: set[str]) -> dict | None:
    if f.reserved:
        return None
    n = f.name.lower()
    if n.startswith("_rsv") or n.startswith("_pad") or n.endswith("pad"):
        return None
    desc_raw = (f.description or "").strip()
    if desc_raw.lower() == "reserved":
        return None
    kind = f.kind
    size = 0 if kind == "var_ebcdic" else field_size(f)
    name = f.name
    desc = (f.description or "").replace("\n", " ").strip()
    if len(desc) > 220:
        desc = desc[:217] + "..."
    key = unique_key(name, used)
    off = None  # filled by caller from layout.offsets

    lname = name.lower()
    hint = f.decode or ""

    if kind == "var_ebcdic":
        return dict(key=key, ibm=name, ftype="VAR_CHR", off=0, length=None, desc=desc)
    if kind == "ipv4":
        return dict(key=key, ibm=name, ftype="IP4", off=0, length=None, desc=desc)
    if kind in ("ipv6", "ipv6mapped"):
        return dict(key=key, ibm=name, ftype="IP16", off=0, length=None, desc=desc)
    if kind == "ipunion":
        return dict(key=key, ibm=name, ftype="IPUN", off=0, length=None, desc=desc)
    if kind == "char":
        ftype, length = _chr_type(size)
        return dict(key=key, ibm=name, ftype=ftype, off=0, length=length, desc=desc)
    if kind in ("bytes", "hex", "raw"):
        if hint == "date_hex" or lname.endswith("date"):
            return dict(key=key, ibm=name, ftype="DTE", off=0, length=None, desc=desc)
        ftype, length = _hex_type(size)
        return dict(key=key, ibm=name, ftype=ftype, off=0, length=length, desc=desc)
    if kind in ("u8", "i8"):
        ftype = "HEX1" if _looks_flag(lname) else "DEC1"
        return dict(key=key, ibm=name, ftype=ftype, off=0, length=None, desc=desc)
    if kind in ("u16", "i16"):
        ftype = "HEX2" if _looks_flag(lname) else "DEC2"
        return dict(key=key, ibm=name, ftype=ftype, off=0, length=None, desc=desc)
    if kind in ("u32", "i32"):
        if "stck" in lname or "subtask" in lname or lname.endswith("tcb"):
            return dict(key=key, ibm=name, ftype="HEX4", off=0, length=None, desc=desc)
        if _looks_time(lname):
            return dict(key=key, ibm=name, ftype="TME", off=0, length=None, desc=desc)
        if lname.endswith("date"):
            return dict(key=key, ibm=name, ftype="DTE", off=0, length=None, desc=desc)
        return dict(key=key, ibm=name, ftype="DEC4", off=0, length=None, desc=desc)
    if kind in ("u64", "i64"):
        if "stck" in lname:
            return dict(key=key, ibm=name, ftype="HEX8", off=0, length=None, desc=desc)
        return dict(key=key, ibm=name, ftype="DEC8", off=0, length=None, desc=desc)
    ftype, length = _hex_type(size or 1)
    return dict(key=key, ibm=name, ftype=ftype, off=0, length=length, desc=desc)


def _looks_flag(lname: str) -> bool:
    tokens = ("flag", "flags", "reason", "status", "code", "proto", "prot", "type", "mode")
    return any(tok in lname for tok in tokens)


def _looks_time(lname: str) -> bool:
    if "duration" in lname or lname.endswith("dur"):
        return False
    return lname.endswith("time") or lname.endswith("stime") or lname.endswith("etime")


def _chr_type(n: int) -> tuple[str, int | None]:
    if n in (1, 2, 4, 8, 16, 20):
        return f"CHR{n}", None
    return "CHR", n


def _hex_type(n: int) -> tuple[str, int | None]:
    if n in (1, 2, 4, 8):
        return f"HEX{n}", None
    return "HEX", n


def emit_field(rec: dict, trip: int) -> str:
    desc = json.dumps(rec["desc"], ensure_ascii=False)
    key = json.dumps(rec["key"])
    ibm = json.dumps(rec["ibm"])
    ftype = json.dumps(rec["ftype"])
    args = [key, ibm, ftype, str(rec["off"]), str(trip)]
    extra = []
    if rec["length"] is not None:
        extra.append(f"length={rec['length']}")
    extra.append(f"description={desc}")
    return f"        F({', '.join(args)}, {', '.join(extra)}),"


def collect_subtype(sty: int) -> list[str]:
    slots = SUBTYPE_SECTIONS.get(sty) or []
    used: set[str] = set()
    lines: list[str] = []
    for slot in slots:
        layout = slot.layout
        trip = triplet_offset(slot.triplet_index)
        for f in layout.fields:
            rec = map_field(f, used)
            if rec is None:
                continue
            rec["off"] = layout.offsets[f.name]
            lines.append(emit_field(rec, trip))
    return lines


def main() -> int:
    if not APP.is_dir():
        print(f"missing layout source: {APP}", file=sys.stderr)
        return 1

    chunks: list[str] = [
        '"""Auto-generated SMF 119 subtype section maps (PACSYS / IBM IFASMFR).',
        "",
        "Do not edit by hand. Regenerate with:",
        "    python python/tools/gen_smf119_maps.py",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from ..types import FieldSpec as F",
        "",
        "SUBTYPE_TITLES = {",
    ]
    for sty in sorted(SUBTYPES):
        title = json.dumps(SUBTYPES[sty], ensure_ascii=False)
        chunks.append(f"    {sty}: {title},")
    chunks.append("}")
    chunks.append("")
    chunks.append("SECTION_FIELDS: dict[int, list[F]] = {")

    mapped = []
    for sty in sorted(SUBTYPE_SECTIONS):
        body = collect_subtype(sty)
        if not body:
            continue
        mapped.append(sty)
        title = SUBTYPES.get(sty, f"subtype {sty}")
        chunks.append(f"    # {sty}: {title}")
        chunks.append(f"    {sty}: [")
        chunks.extend(body)
        chunks.append("    ],")
    chunks.append("}")
    chunks.append("")

    OUT.write_text("\n".join(chunks) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(mapped)} subtypes: {mapped})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
