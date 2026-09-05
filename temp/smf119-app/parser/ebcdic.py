"""EBCDIC (CP037) helpers for SMF 119 text fields."""
from __future__ import annotations

_EBCDIC_TO_ASCII = {
    **{0xF0 + i: ord("0") + i for i in range(10)},
    **{0xC1 + i: ord("A") + i for i in range(9)},
    **{0xD1 + i: ord("J") + i for i in range(9)},
    **{0xE2 + i: ord("S") + i for i in range(8)},
    0x40: ord(" "),
    0x4B: ord("."),
    0x6B: ord(","),
    0x60: ord("-"),
    0x61: ord("/"),
    0x7E: ord("="),
    0x5C: ord("*"),
    0x4D: ord("("),
    0x5D: ord(")"),
    0x7D: ord("'"),
    0x7F: ord('"'),
    0x50: ord("&"),
    0x4E: ord("+"),
    0x6C: ord("%"),
    0x6D: ord("_"),
    0x6E: ord(">"),
    0x4C: ord("<"),
    0x5E: ord(";"),
    0x5A: ord("!"),
    0x5F: ord("^"),
    0x7A: ord(":"),
    0x7B: ord("#"),
    0x7C: ord("@"),
    # lowercase a-i, j-r, s-z
    **{0x81 + i: ord("a") + i for i in range(9)},
    **{0x91 + i: ord("j") + i for i in range(9)},
    **{0xA2 + i: ord("s") + i for i in range(8)},
}


def ebcdic_to_str(data: bytes, *, keep_unknown: str = ".") -> str:
    chars: list[str] = []
    for b in data:
        if b in _EBCDIC_TO_ASCII:
            chars.append(chr(_EBCDIC_TO_ASCII[b]))
        else:
            chars.append(keep_unknown)
    return "".join(chars)


def looks_like_ebcdic_id(data: bytes) -> bool:
    """True if 4-byte SMF SID/SSI looks like a printable z/OS id."""
    if len(data) != 4:
        return False
    text = ebcdic_to_str(data, keep_unknown="\0")
    if "\0" in text:
        return False
    if not text.strip():
        return False
    return all(c.isalnum() or c == " " for c in text)


def ebcdic_eye_u32(value: int) -> str:
    """Decode a big-endian u32 eyecatcher to ASCII (e.g. PICO)."""
    return ebcdic_to_str(value.to_bytes(4, "big")).rstrip()
