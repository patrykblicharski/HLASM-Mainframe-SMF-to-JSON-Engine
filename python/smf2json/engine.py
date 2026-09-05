"""Table-driven SMF → dict conversion engine."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Sequence

from .maps import MAPS_BY_TYPE
from .reader import SmfRecord
from .types import FieldSpec, convert_value, field_length


LogFn = Callable[[str], None]


def _u16(data: bytes, off: int) -> int:
    return int.from_bytes(data[off : off + 2], "big")


def _u32(data: bytes, off: int) -> int:
    return int.from_bytes(data[off : off + 4], "big")


def resolve_address(data: bytes, spec: FieldSpec, log: LogFn) -> Optional[int]:
    if spec.triplet_offset is None:
        return spec.offset

    trip = spec.triplet_offset
    if trip + 4 > len(data):
        log(f"DEBUG: {spec.json_key}: triplet @{trip} past EOF")
        return None
    section_off = _u32(data, trip)
    if section_off == 0:
        log(f"DEBUG: {spec.json_key}: section triplet @{trip:#x} = 0 (absent)")
        return None
    return section_off + spec.offset


def extract_rs_string(data: bytes, control_offset: int, tag: int, log: LogFn) -> str:
    if control_offset + 4 > len(data):
        return ""
    rel = _u16(data, control_offset)
    cnt = _u16(data, control_offset + 2)
    if rel == 0 or cnt == 0:
        return ""
    pos = rel
    for _ in range(cnt):
        if pos + 2 > len(data):
            break
        dtp = data[pos]
        dln = data[pos + 1]
        pos += 2
        if pos + dln > len(data):
            break
        payload = data[pos : pos + dln]
        pos += dln
        if dtp == tag:
            from .types import ebcdic_to_str

            val = ebcdic_to_str(payload)
            log(f"DEBUG: RS tag={tag} hit len={dln} value={val!r}")
            return val
    log(f"DEBUG: RS tag={tag} not found (cnt={cnt})")
    return ""


def convert_record(rec: SmfRecord, log: Optional[LogFn] = None) -> Optional[Dict[str, Any]]:
    log = log or (lambda _m: None)
    rty = rec.record_type
    fields: Sequence[FieldSpec] = MAPS_BY_TYPE.get(rty, ())
    if not fields:
        log(f"DEBUG: record[{rec.index}] type={rty} — no map, skipped")
        return None

    log(f"INFO: converting record[{rec.index}] type={rty} with {len(fields)} field specs")
    out: Dict[str, Any] = {}
    data = rec.data

    for spec in fields:
        try:
            if spec.ftype == "RS_STR":
                out[spec.json_key] = extract_rs_string(data, spec.offset, spec.tag or 0, log)
                continue

            addr = resolve_address(data, spec, log)
            if addr is None:
                out[spec.json_key] = ""
                continue
            ln = field_length(spec)
            if addr < 0 or addr + ln > len(data):
                log(f"DEBUG: {spec.json_key}: addr={addr} len={ln} OOB (rec={len(data)})")
                out[spec.json_key] = ""
                continue
            raw = data[addr : addr + ln]
            val = convert_value(spec, raw)
            out[spec.json_key] = val
            log(
                f"DEBUG: {spec.json_key} ({spec.ibm_name}) "
                f"type={spec.ftype} @{addr:#x}/{ln} → {val!r}"
            )
        except Exception as exc:  # noqa: BLE001
            log(f"ERROR: {spec.json_key}: {exc}")
            out[spec.json_key] = ""
    return out


def convert_dump(records: List[SmfRecord], log: Optional[LogFn] = None) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for rec in records:
        obj = convert_record(rec, log=log)
        if obj is not None:
            rows.append(obj)
    if log:
        log(f"INFO: converted {len(rows)} records")
    return rows


def field_descriptions_for_rows(rows: List[Dict[str, Any]]) -> Dict[str, str]:
    desc: Dict[str, str] = {}
    for specs in MAPS_BY_TYPE.values():
        for s in specs:
            desc[s.json_key] = s.description or s.ibm_name
    return desc


def ordered_columns(rows: List[Dict[str, Any]]) -> List[str]:
    if not rows:
        return []
    cols: List[str] = []
    seen = set()
    for row in rows:
        for k in row:
            if k not in seen:
                seen.add(k)
                cols.append(k)
    return cols
