"""SMF field type converters (mirrors SMF2ZIIP CASE handlers)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Any, Callable, Optional


@dataclass(frozen=True)
class FieldSpec:
    """One map entry — equivalent of an SMF_FIELD macro expansion."""

    json_key: str
    ibm_name: str
    ftype: str
    offset: int  # relative to section base (0 for header fields)
    triplet_offset: Optional[int] = None  # absolute offset of section triplet in header
    length: Optional[int] = None  # for CHR / RS; inferred from ftype when None
    tag: Optional[int] = None  # relocate-section tag id
    description: str = ""


TYPE_LENGTHS = {
    "BIN1": 1,
    "CHR1": 1,
    "CHR2": 2,
    "CHR4": 4,
    "CHR8": 8,
    "CHR16": 16,
    "CHR20": 20,
    "DEC1": 1,
    "DEC2": 2,
    "DEC4": 4,
    "DTE": 4,
    "TME": 4,
    "RS_STR": 0,
}


# Accept both DTE and DTE alias from maps
TYPE_LENGTHS["DTE"] = 4


def ebcdic_to_str(data: bytes) -> str:
    # Null-padded and space-padded EBCDIC fields are common in SMF.
    return data.decode("cp037", errors="replace").rstrip(" \x00")


def parse_smf_date(raw: bytes) -> str:
    """Packed 0cyydddF → YYYY-MM-DD (same rules as GET_DATE)."""
    if len(raw) < 4:
        return ""
    century_byte = raw[0]
    # IBM SMF date: byte0 low nibble often century indicator in 0c form;
    # common layout is 0cyydddF as packed. Mirror HLASM TM X'01' on first byte.
    year_hi = 20 if (century_byte & 0x01) else 19
    # Unpack yy from bytes 1 (often packed with ddd)
    # HLASM does UNPK from bytes 1-2 for YY then days from byte 2 area.
    # Practical form used by SMF: x'0c yy dd dF' packed → nibbles.
    # Use classic approach: interpret as packed decimal 0cyydddF.
    try:
        hexdigs = raw.hex()
        # e.g. 0125084f → c=1, yy=25, ddd=084
        if len(hexdigs) < 8:
            return ""
        c = int(hexdigs[1], 16)
        yy = int(hexdigs[2:4], 10)
        ddd = int(hexdigs[4:7], 10)
        year = (2000 if c else 1900) + yy
        # Prefer century bit rule from HLASM when packed form ambiguous
        if century_byte & 0x01:
            year = 2000 + yy
        else:
            # if high nibble suggests 0c packed century
            if c == 1:
                year = 2000 + yy
            elif c == 0:
                year = 1900 + yy
            else:
                year = year_hi * 100 + yy
        if not (1 <= ddd <= 366):
            return ""
        dt = date(year, 1, 1).fromordinal(date(year, 1, 1).toordinal() + ddd - 1)
        return dt.isoformat()
    except Exception:
        return ""


def parse_smf_time(raw: bytes) -> str:
    """Binary hundredths since midnight → HH:MM:SS."""
    if len(raw) < 4:
        return ""
    hundredths = int.from_bytes(raw[:4], "big", signed=False)
    total_sec = hundredths // 100
    hh = total_sec // 3600
    mm = (total_sec % 3600) // 60
    ss = total_sec % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def parse_dec(raw: bytes) -> str:
    if not raw:
        return ""
    return str(int.from_bytes(raw, "big", signed=False))


def field_length(spec: FieldSpec) -> int:
    if spec.length is not None:
        return spec.length
    return TYPE_LENGTHS.get(spec.ftype.upper(), 0)


def convert_value(spec: FieldSpec, raw: bytes) -> str:
    ft = spec.ftype.upper()
    if ft.startswith("CHR") or ft == "BIN1":
        if ft == "BIN1":
            return parse_dec(raw[:1])
        return ebcdic_to_str(raw)
    if ft.startswith("DEC"):
        return parse_dec(raw)
    if ft in ("DTE", "DATE"):
        return parse_smf_date(raw)
    if ft in ("TME", "TIME"):
        return parse_smf_time(raw)
    return ebcdic_to_str(raw)
