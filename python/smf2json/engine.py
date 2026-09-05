"""Table-driven SMF → dict conversion engine."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence

from .maps import MAPS_BY_SUBTYPE, MAPS_BY_TYPE, fields_for
from .reader import ProgressFn, SmfRecord, iter_dump
from .types import FieldSpec, convert_value, ebcdic_to_str, field_length


LogFn = Callable[[str], None]


def _u16(data: bytes, off: int) -> int:
    return int.from_bytes(data[off : off + 2], "big")


def _u32(data: bytes, off: int) -> int:
    return int.from_bytes(data[off : off + 4], "big")


def read_triplet(data: bytes, trip: int) -> Optional[tuple[int, int, int]]:
    """Return (section_offset, section_length, section_number) or None if absent.

    IBM self-defining triplets mark a section absent with number=0 (and often
    length=0). The offset may still point at the next section — do not treat a
    non-zero offset alone as presence.
    """
    if trip + 8 > len(data):
        return None
    section_off = _u32(data, trip)
    section_len = _u16(data, trip + 4)
    section_num = _u16(data, trip + 6)
    if section_off == 0 or section_num == 0:
        return None
    return section_off, section_len, section_num


def resolve_address(data: bytes, spec: FieldSpec, log: Optional[LogFn] = None) -> Optional[int]:
    if spec.triplet_offset is None:
        return spec.offset

    trip = spec.triplet_offset
    if trip + 8 > len(data):
        if log:
            log(f"DEBUG: {spec.json_key}: triplet @{trip} past EOF")
        return None
    section_off = _u32(data, trip)
    section_num = _u16(data, trip + 6)
    if section_off == 0 or section_num == 0:
        if log:
            log(
                f"DEBUG: {spec.json_key}: section triplet @{trip:#x} absent "
                f"(off={section_off} num={section_num})"
            )
        return None
    return section_off + spec.offset


def _rs_scan(
    data: bytes,
    control_offset: int,
    tag: int,
    *,
    as_hex: bool = False,
    log: Optional[LogFn] = None,
) -> str:
    """Find a 1-byte-tag relocate payload.

    IBM SMF80REL / SMF80RL2 are offsets from SMF80FLG (absolute = value + 4
    when the RDW is present in ``data``).
    """
    if control_offset + 4 > len(data):
        return ""
    rel = _u16(data, control_offset)
    cnt = _u16(data, control_offset + 2)
    if rel == 0 or cnt == 0:
        return ""
    # Offset from SMF80FLG (== RDW length when RDW is kept in the buffer).
    pos = rel + 4
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
            if as_hex:
                val = payload.hex().upper()
            else:
                val = ebcdic_to_str(payload)
            if log:
                log(f"DEBUG: RS tag={tag} hit len={dln} value={val!r}")
            return val
    if log:
        log(f"DEBUG: RS tag={tag} not found (cnt={cnt})")
    return ""


def extract_rs_string(data: bytes, control_offset: int, tag: int, log: Optional[LogFn] = None) -> str:
    return _rs_scan(data, control_offset, tag, as_hex=False, log=log)


def extract_rs_hex(data: bytes, control_offset: int, tag: int, log: Optional[LogFn] = None) -> str:
    return _rs_scan(data, control_offset, tag, as_hex=True, log=log)


def _rs2_scan(
    data: bytes,
    control_offset: int,
    tag: int,
    *,
    as_hex: bool = False,
    log: Optional[LogFn] = None,
) -> str:
    """Find an extended-length relocate payload (SMF80TP2 / DL2 / DA2).

    Control word at ``SMF80RL2`` (offset 92): offset + count, both u16.
    Offset is from SMF80FLG (absolute = value + 4 with RDW). Each entry is
    2-byte type, 2-byte length, then data (PACSYS / IBM IFASMFR).
    """
    if control_offset + 4 > len(data):
        return ""
    rel = _u16(data, control_offset)
    cnt = _u16(data, control_offset + 2)
    if rel == 0 or cnt == 0:
        return ""
    pos = rel + 4
    for _ in range(cnt):
        if pos + 4 > len(data):
            break
        dtp = _u16(data, pos)
        dln = _u16(data, pos + 2)
        pos += 4
        if dln < 0 or pos + dln > len(data):
            break
        payload = data[pos : pos + dln]
        pos += dln
        if dtp == tag:
            if as_hex:
                val = payload.hex().upper()
            else:
                val = ebcdic_to_str(payload)
            if log:
                log(f"DEBUG: RS2 tag={tag} hit len={dln} value={val!r}")
            return val
    if log:
        log(f"DEBUG: RS2 tag={tag} not found (cnt={cnt})")
    return ""


def extract_rs2_string(data: bytes, control_offset: int, tag: int, log: Optional[LogFn] = None) -> str:
    return _rs2_scan(data, control_offset, tag, as_hex=False, log=log)


def extract_rs2_hex(data: bytes, control_offset: int, tag: int, log: Optional[LogFn] = None) -> str:
    return _rs2_scan(data, control_offset, tag, as_hex=True, log=log)


def _extract_var_chr(data: bytes, spec: FieldSpec, log: Optional[LogFn] = None) -> str:
    """EBCDIC string whose length is the triplet section length minus the field offset."""
    if spec.triplet_offset is None:
        return ""
    trip = read_triplet(data, spec.triplet_offset)
    if trip is None:
        if log:
            log(f"DEBUG: {spec.json_key}: VAR_CHR triplet absent")
        return ""
    section_off, section_len, _num = trip
    addr = section_off + spec.offset
    nbytes = section_len - spec.offset
    if nbytes <= 0 or addr < 0 or addr + nbytes > len(data):
        if log:
            log(
                f"DEBUG: {spec.json_key}: VAR_CHR addr={addr} len={nbytes} "
                f"OOB (rec={len(data)} seclen={section_len})"
            )
        return ""
    val = ebcdic_to_str(data[addr : addr + nbytes])
    if log:
        log(f"DEBUG: {spec.json_key} ({spec.ibm_name}) type=VAR_CHR @{addr:#x}/{nbytes} → {val!r}")
    return val


def convert_record(rec: SmfRecord, log: Optional[LogFn] = None) -> Optional[Dict[str, Any]]:
    rty = rec.record_type
    sty = rec.subtype
    fields: Sequence[FieldSpec] = fields_for(rty, sty)
    if not fields:
        if log:
            log(f"DEBUG: record[{rec.index}] type={rty} subtype={sty} — no map, skipped")
        return None

    if log:
        log(
            f"INFO: converting record[{rec.index}] type={rty} subtype={sty} "
            f"with {len(fields)} field specs"
        )
    out: Dict[str, Any] = {}
    data = rec.data

    for spec in fields:
        try:
            ft = spec.ftype.upper()
            if ft == "RS_STR":
                out[spec.json_key] = extract_rs_string(data, spec.offset, spec.tag or 0, log)
                continue
            if ft == "RS_HEX":
                out[spec.json_key] = extract_rs_hex(data, spec.offset, spec.tag or 0, log)
                continue
            if ft == "RS2_STR":
                out[spec.json_key] = extract_rs2_string(data, spec.offset, spec.tag or 0, log)
                continue
            if ft == "RS2_HEX":
                out[spec.json_key] = extract_rs2_hex(data, spec.offset, spec.tag or 0, log)
                continue

            if ft in ("VAR_CHR", "VARCHR"):
                out[spec.json_key] = _extract_var_chr(data, spec, log)
                continue

            addr = resolve_address(data, spec, log)
            if addr is None:
                out[spec.json_key] = ""
                continue
            ln = field_length(spec)
            if addr < 0 or addr + ln > len(data):
                if log:
                    log(f"DEBUG: {spec.json_key}: addr={addr} len={ln} OOB (rec={len(data)})")
                out[spec.json_key] = ""
                continue
            raw = data[addr : addr + ln]
            val = convert_value(spec, raw)
            out[spec.json_key] = val
            if log:
                log(
                    f"DEBUG: {spec.json_key} ({spec.ibm_name}) "
                    f"type={spec.ftype} @{addr:#x}/{ln} → {val!r}"
                )
        except Exception as exc:  # noqa: BLE001
            if log:
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


def convert_path(
    path: str,
    log: Optional[LogFn] = None,
    progress: Optional[ProgressFn] = None,
) -> Iterator[Dict[str, Any]]:
    """Yield mapped rows one at a time so callers can batch without holding every SMF record."""
    for rec in iter_dump(path, log=log, progress=progress):
        obj = convert_record(rec, log=log)
        if obj is not None:
            yield obj


def field_meta() -> Dict[str, Dict[str, Any]]:
    """json_key → label / description / IBM name / SMF types that define it."""
    meta: Dict[str, Dict[str, Any]] = {}
    catalogs: List[tuple[int, Sequence[FieldSpec]]] = [
        (rty, specs) for rty, specs in MAPS_BY_TYPE.items()
    ]
    catalogs.extend((rty, specs) for (rty, _sty), specs in MAPS_BY_SUBTYPE.items())
    for rty, specs in catalogs:
        for spec in specs:
            rec = meta.get(spec.json_key)
            if rec is None:
                meta[spec.json_key] = {
                    "key": spec.json_key,
                    "label": spec.description or spec.ibm_name or spec.json_key,
                    "description": spec.description,
                    "ibm_name": spec.ibm_name,
                    "ibm_by_type": {rty: spec.ibm_name},
                    "desc_by_type": {rty: spec.description},
                    "types": [rty],
                }
            elif rty not in rec["types"]:
                rec["types"].append(rty)
                rec["ibm_by_type"][rty] = spec.ibm_name
                rec["desc_by_type"][rty] = spec.description
    return meta


def field_descriptions_for_rows(rows: List[Dict[str, Any]]) -> Dict[str, str]:
    return {key: info["label"] for key, info in field_meta().items()}


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
