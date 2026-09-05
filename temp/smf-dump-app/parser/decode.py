"""Decode SMF record bytes using OpenAPI x-zml field layouts."""
from __future__ import annotations

import json
import struct
from functools import lru_cache
from pathlib import Path
from typing import Any

from .catalog import openapi_root_name
from .ebcdic import ebcdic_to_str
from .dump_index import SmfRecordRef

# Prefer mock OpenAPI (same IBM Gatherer field map the rest of the repo uses).
_DEFAULT_SPEC_CANDIDATES = [
    Path(__file__).resolve().parents[2] / "smf-mock" / "mock_server" / "openapi_spec.json",
    Path(__file__).resolve().parents[2] / "api-doc.json",
]


@lru_cache(maxsize=1)
def load_openapi_schemas(spec_path: str | None = None) -> dict[str, Any]:
    if spec_path:
        path = Path(spec_path)
    else:
        path = next((p for p in _DEFAULT_SPEC_CANDIDATES if p.exists()), None)
        if path is None:
            raise FileNotFoundError("OpenAPI spec not found (smf-mock/openapi_spec.json)")
    spec = json.loads(path.read_text(encoding="utf-8"))
    return spec["components"]["schemas"]


def decode_standard_header(record: bytes) -> dict[str, Any]:
    """Always-available 24-byte SMF header fields."""
    if len(record) < 24:
        raise ValueError("record too short for SMF header")
    length = struct.unpack_from(">H", record, 0)[0]
    seg = struct.unpack_from(">H", record, 2)[0]
    flag = record[4]
    rty = record[5]
    # Time: hundredths of seconds since midnight (binary, big-endian)
    tod_hsec = struct.unpack_from(">I", record, 6)[0]
    hours = tod_hsec // (100 * 3600)
    minutes = (tod_hsec // (100 * 60)) % 60
    seconds = (tod_hsec // 100) % 60
    hundredths = tod_hsec % 100
    date_raw = record[10:14]
    return {
        "SMF_LEN": length,
        "SMF_SEG": seg,
        "SMF_FLG": f"{flag:08b}",
        "SMF_RTY": rty,
        "SMF_TME": f"{hours:02d}:{minutes:02d}:{seconds:02d}.{hundredths:02d}",
        "SMF_DTE_RAW": date_raw.hex(),
        "SMF_SID": ebcdic_to_str(record[14:18]).strip(),
        "SMF_SSI": ebcdic_to_str(record[18:22]).strip(),
        "SMF_STY": struct.unpack_from(">H", record, 22)[0],
    }


def _decode_leaf(record: bytes, base: int, prop: dict[str, Any]) -> Any:
    offset = base + int(prop.get("x-zml-offset") or 0)
    size = int(prop.get("x-zml-size") or 0)
    datatype = prop.get("x-zml-datatype")
    typ = prop.get("type")

    if datatype == "BIT":
        # Flag bit inside a byte at x-zml-offset; bit-offset from IBM docs.
        if offset >= len(record):
            return None
        bit = int(prop.get("x-zml-bit-offset") or 0)
        return bool(record[offset] & (0x80 >> bit))

    if size <= 0 or offset < 0 or offset + size > len(record):
        return None

    chunk = record[offset : offset + size]

    if datatype == "CHARACTER":
        return ebcdic_to_str(chunk).rstrip()
    if datatype in ("HEX_STR", "BIN_STR"):
        if datatype == "BIN_STR":
            return "".join(f"{b:08b}" for b in chunk)
        return chunk.hex()
    if datatype in ("UNSIGNED", "SIGNED") or typ == "integer":
        # Big-endian integer; signed only when declared SIGNED.
        if size == 1:
            val = chunk[0]
            if datatype == "SIGNED" and val >= 0x80:
                val -= 0x100
            return val
        if size == 2:
            val = struct.unpack(">H", chunk)[0]
            if datatype == "SIGNED" and val >= 0x8000:
                val -= 0x10000
            return val
        if size == 4:
            val = struct.unpack(">I", chunk)[0]
            if datatype == "SIGNED" and val >= 0x80000000:
                val -= 0x100000000
            return val
        if size == 8:
            val = struct.unpack(">Q", chunk)[0]
            if datatype == "SIGNED" and val >= 0x8000000000000000:
                val -= 0x10000000000000000
            return val
        return int.from_bytes(chunk, "big", signed=(datatype == "SIGNED"))
    if typ == "string" or datatype in ("PACKED_DATE_2", "TOD", "PACKED_TIME_2", "PACKED_TIME_3", "PACKED_TIME_4"):
        # Keep raw hex for packed/TOD until dedicated formatters exist.
        if prop.get("format") == "date":
            return chunk.hex()
        if prop.get("format") == "time":
            return chunk.hex()
        if prop.get("format") == "date-time":
            return chunk.hex()
        return ebcdic_to_str(chunk).rstrip() if datatype == "CHARACTER" else chunk.hex()
    if typ == "boolean":
        return chunk != b"\x00" * size
    return chunk.hex()


def decode_openapi_root(record: bytes, smf_type: int, subtype: int) -> dict[str, Any]:
    """Decode leaf fields declared on the OpenAPI root schema (header section)."""
    schemas = load_openapi_schemas()
    root_name = openapi_root_name(smf_type, subtype)
    schema = schemas.get(root_name)
    if not schema:
        return {}
    out: dict[str, Any] = {}
    for name, prop in (schema.get("properties") or {}).items():
        if "$ref" in prop:
            continue
        if prop.get("type") == "object" or "additionalProperties" in prop:
            continue
        # Skip pure meta triplet counters unless useful — still include non-meta.
        try:
            out[name] = _decode_leaf(record, 0, prop)
        except Exception:
            out[name] = None
    return out


def decode_record(record: bytes, ref: SmfRecordRef) -> dict[str, Any]:
    """Header fields + OpenAPI root leafs for one physical SMF record."""
    row = decode_standard_header(record)
    row["_offset"] = ref.offset
    row["_length"] = ref.length
    openapi_fields = decode_openapi_root(record, ref.smf_type, ref.subtype)
    # OpenAPI names win on overlap (they match Gatherer field names).
    row.update(openapi_fields)
    return row


def decode_records(
    path: str | Path,
    refs: list[SmfRecordRef],
    *,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Decode all (or first ``limit``) record refs. ``limit=None`` means no cap."""
    path = Path(path)
    rows: list[dict[str, Any]] = []
    selected = refs if limit is None else refs[:limit]
    with path.open("rb") as fh:
        for ref in selected:
            fh.seek(ref.offset)
            blob = fh.read(ref.length)
            if len(blob) != ref.length:
                continue
            rows.append(decode_record(blob, ref))
    return rows
