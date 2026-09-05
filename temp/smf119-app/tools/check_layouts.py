#!/usr/bin/env python3
"""Validate SMF 119 layout registry coverage and basic structural integrity.

Usage:
    python3 tools/check_layouts.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from parser.catalog import all_layouts, field_catalog_rows, subtype_catalog_rows  # noqa: E402
from parser.nmtp_layouts import PROFILE_SECTIONS  # noqa: E402
from parser.registry import COVERAGE, EYE_LAYOUTS, SUBTYPE_SECTIONS  # noqa: E402
from parser.subtypes import SUBTYPES  # noqa: E402
from parser.views import columns_for  # noqa: E402

EXTERNAL = {94, 95, 96, 97, 98}
ERRORS: list[str] = []
WARNINGS: list[str] = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        ERRORS.append(msg)


def main() -> int:
    # Every catalog subtype except OpenSSH externals must be mapped
    for st in sorted(SUBTYPES):
        cov = COVERAGE.get(st, "unmapped")
        if st in EXTERNAL:
            check(cov == "external", f"subtype {st}: expected coverage=external, got {cov}")
            continue
        if st == 4:
            check(cov == "mapped", f"subtype 4: expected mapped, got {cov}")
            check(len(PROFILE_SECTIONS) > 0, "subtype 4: PROFILE_SECTIONS empty")
            continue
        check(st in SUBTYPE_SECTIONS, f"subtype {st}: missing from SUBTYPE_SECTIONS")
        check(cov == "mapped", f"subtype {st}: expected mapped, got {cov}")
        slots = SUBTYPE_SECTIONS.get(st, [])
        check(len(slots) >= 1, f"subtype {st}: no section slots")
        seen_idx = set()
        for slot in slots:
            check(slot.triplet_index >= 1, f"subtype {st}: bad triplet_index {slot.triplet_index}")
            check(slot.triplet_index not in seen_idx, f"subtype {st}: duplicate triplet {slot.triplet_index}")
            seen_idx.add(slot.triplet_index)
            layout = slot.layout
            check(layout is not None, f"subtype {st} slot {slot.key}: no layout")
            if layout.variable:
                check(
                    any(f.kind == "var_ebcdic" for f in layout.fields),
                    f"{layout.name}: variable layout without var_ebcdic field",
                )
            else:
                check(layout.size > 0, f"{layout.name}: fixed layout size is 0")
            # offsets must be monotonic for non-var fields
            prev = -1
            for f in layout.fields:
                off = layout.offsets[f.name]
                if f.kind == "var_ebcdic":
                    continue
                check(off >= prev, f"{layout.name}.{f.name}: offset {off} < previous {prev}")
                prev = off

    # Eyecatcher registry consistency
    for eye, layout in EYE_LAYOUTS.items():
        check(layout.eyecatcher in (None, eye), f"eye 0x{eye:08X}: layout eyecatcher mismatch")

    # Summary columns always available
    for st in sorted(SUBTYPES):
        cols = columns_for(st)
        check(len(cols) >= 4, f"subtype {st}: summary columns too short ({len(cols)})")
        keys = {c.key for c in cols}
        for required in ("offset", "time", "sid", "stack"):
            check(required in keys, f"subtype {st}: missing base column {required}")

    # Catalog sanity
    fields = field_catalog_rows()
    check(len(fields) > 500, f"field catalog unexpectedly small: {len(fields)}")
    layouts = all_layouts()
    check(len(layouts) > 50, f"layout count unexpectedly small: {len(layouts)}")

    # Smoke: decode a synthetic subtype-1 record (header + Ident + TI)
    try:
        from parser.decode import decode_record, summary_row
        from parser.header_layouts import HEADER, IDENT
        from parser.layouts.st01 import AP_TI_S1
        from parser.layout import decode_struct  # noqa: F401

        sid = bytes([0xE2, 0xE8, 0xE2, 0xF1])  # SYS1
        ssi = bytes([0xE3, 0xC3, 0xD7, 0xC9])  # TCPI
        # Build Ident with stack name TCPIP
        ident = bytearray(IDENT.size)
        ident[0:8] = sid + bytes([0x40, 0x40, 0x40, 0x40])
        # stack at 16
        stack = bytes([0xE3, 0xC3, 0xD7, 0xC9, 0xD7, 0x40, 0x40, 0x40])  # TCPIP
        ident[16:24] = stack
        ti = bytearray(AP_TI_S1.size)
        # resource name
        ti[0:8] = bytes([0xC6, 0xE3, 0xD7, 0xC4, 0xC1, 0xC5, 0xD4, 0xD6])  # FTPDAEMO approx
        import struct as _st

        # RIP at 20, LIP at 36, RPort 52, LPort 54
        ti[20:36] = b"\x00" * 10 + b"\xff\xff" + bytes([10, 9, 8, 7])
        ti[36:52] = b"\x00" * 10 + b"\xff\xff" + bytes([10, 1, 2, 3])
        _st.pack_into(">HH", ti, 52, 443, 21)

        # triplets: Ident then S1
        # record layout: header(24) + sdef(4) + 2*triplet(8) = 44, then sections
        trn = 2
        ident_off = 44
        ti_off = ident_off + IDENT.size
        total = ti_off + AP_TI_S1.size
        rec = bytearray(total)
        _st.pack_into(">H", rec, 0, total)  # length
        rec[4] = 0x40  # subtypes used
        rec[5] = 119
        rec[14:18] = sid
        rec[18:22] = ssi
        _st.pack_into(">H", rec, 22, 1)  # subtype 1
        _st.pack_into(">H", rec, 24, trn)  # SD_TRN (check SDEF layout)
        from parser.header_layouts import SDEF_PROLOGUE

        # rewrite sdef properly
        rec[24 : 24 + SDEF_PROLOGUE.size] = b"\x00" * SDEF_PROLOGUE.size
        # pack TRN into sdef
        sdef_fields = {f.name: f for f in SDEF_PROLOGUE.fields}
        # assume first field is TRN
        for f in SDEF_PROLOGUE.fields:
            if "TRN" in f.name:
                off = SDEF_PROLOGUE.offsets[f.name]
                if f.kind == "u16":
                    _st.pack_into(">H", rec, 24 + off, trn)
                elif f.kind == "u32":
                    _st.pack_into(">I", rec, 24 + off, trn)
        trip_base = 24 + SDEF_PROLOGUE.size
        # triplet 0 Ident
        _st.pack_into(">IHH", rec, trip_base, ident_off, IDENT.size, 1)
        # triplet 1 TI
        _st.pack_into(">IHH", rec, trip_base + 8, ti_off, AP_TI_S1.size, 1)
        rec[ident_off : ident_off + IDENT.size] = ident
        rec[ti_off : ti_off + AP_TI_S1.size] = ti
        decoded = decode_record(bytes(rec))
        check(decoded.subtype == 1, f"synthetic subtype got {decoded.subtype}")
        check(decoded.ident is not None, "synthetic: Ident not decoded")
        row = summary_row(decoded, file_offset=0)
        check(row.get("stack"), f"synthetic: missing stack in summary ({row})")
        check(row.get("lip") == "10.1.2.3", f"synthetic: lip={row.get('lip')}")
        check(row.get("rip") == "10.9.8.7", f"synthetic: rip={row.get('rip')}")
        print("synthetic subtype-1 decode: OK")
    except Exception as exc:  # noqa: BLE001
        ERRORS.append(f"synthetic decode failed: {exc}")

    rows = subtype_catalog_rows()
    mapped = sum(1 for r in rows if r["coverage"] == "mapped")
    external = sum(1 for r in rows if r["coverage"] == "external")
    unmapped = sum(1 for r in rows if r["coverage"] == "unmapped")
    print(f"layouts: {len(layouts)}")
    print(f"catalog fields: {len(fields)}")
    print(f"subtypes: mapped={mapped} external={external} unmapped={unmapped}")
    print(f"eye registry: {len(EYE_LAYOUTS)}")
    print(f"registered subtypes: {sorted(SUBTYPE_SECTIONS)}")

    if WARNINGS:
        print("WARNINGS:")
        for w in WARNINGS:
            print(f"  - {w}")
    if ERRORS:
        print("ERRORS:")
        for e in ERRORS:
            print(f"  - {e}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
