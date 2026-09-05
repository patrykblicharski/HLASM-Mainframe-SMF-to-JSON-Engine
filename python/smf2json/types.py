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
    "DEC8": 8,
    "HEX1": 1,
    "HEX4": 4,
    "HEX8": 8,
    "IP16": 16,
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


def _hhmmss(total_sec: int) -> str:
    if total_sec < 0:
        return ""
    hh, rem = divmod(total_sec, 3600)
    mm, ss = divmod(rem, 60)
    if hh > 47:
        return ""
    return f"{hh % 24:02d}:{mm:02d}:{ss:02d}"


def _packed_hhmmss(raw: bytes) -> str:
    """Packed 0HHMMSSf / HHMMSSth → HH:MM:SS."""
    if len(raw) < 4:
        return ""
    hexdigs = raw.hex()
    if len(hexdigs) < 8:
        return ""
    sign = hexdigs[-1]
    if sign not in "cfCF":
        return ""
    digits = hexdigs[:-1]
    if not digits.isdigit() or len(digits) < 6:
        return ""
    body = digits[-6:]
    try:
        hh, mm, ss = int(body[0:2]), int(body[2:4]), int(body[4:6])
    except ValueError:
        return ""
    if hh > 23 or mm > 59 or ss > 59:
        return ""
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def parse_smf_time(raw: bytes) -> str:
    """SMF TOD: 4-byte binary hundredths since midnight, or packed 0HHMMSSf.

    Whole seconds stay ``HH:MM:SS`` (HLASM GET_TIME). A non-zero hundredths
    remainder is appended as ``.hh`` so values like x'00000046' are not shown
    as midnight.
    """
    if len(raw) < 4:
        return ""
    hundredths = int.from_bytes(raw[:4], "big", signed=False)
    if hundredths == 0:
        return "00:00:00"
    if hundredths <= 48 * 3600 * 100:
        total_sec, frac = divmod(hundredths, 100)
        formatted = _hhmmss(total_sec)
        if formatted:
            return f"{formatted}.{frac:02d}" if frac else formatted
    packed = _packed_hhmmss(raw)
    if packed:
        return packed
    return _hhmmss(hundredths // 100) or ""


def parse_dec(raw: bytes) -> str:
    if not raw:
        return ""
    return str(int.from_bytes(raw, "big", signed=False))


def parse_hex(raw: bytes) -> str:
    return raw.hex().upper() if raw else ""


def parse_ip16(raw: bytes) -> str:
    """16-byte TCP/IP address: IPv4-mapped, IPv4-compatible, or IPv6."""
    if len(raw) < 16:
        return ""
    chunk = raw[:16]
    if chunk == bytes(16):
        return ""
    if chunk[:10] == bytes(10) and chunk[10:12] == b"\xff\xff":
        return ".".join(str(b) for b in chunk[12:16])
    if chunk[:12] == bytes(12):
        return ".".join(str(b) for b in chunk[12:16])
    hextets = [f"{int.from_bytes(chunk[i : i + 2], 'big'):x}" for i in range(0, 16, 2)]
    return ":".join(hextets)


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
    if ft.startswith("HEX"):
        return parse_hex(raw)
    if ft == "IP16":
        return parse_ip16(raw)
    if ft in ("DTE", "DATE"):
        return parse_smf_date(raw)
    if ft in ("TME", "TIME"):
        return parse_smf_time(raw)
    return ebcdic_to_str(raw)
