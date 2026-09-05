"""EBCDIC (CP037 subset) helpers for SMF header IDs."""
from __future__ import annotations

# IBM CP037: digits, A-I, J-R, S-Z, space
_EBCDIC_TO_ASCII = {
    **{0xF0 + i: ord("0") + i for i in range(10)},
    **{0xC1 + i: ord("A") + i for i in range(9)},
    **{0xD1 + i: ord("J") + i for i in range(9)},
    **{0xE2 + i: ord("S") + i for i in range(8)},
    0x40: ord(" "),
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
    stripped = text.strip()
    if not stripped:
        return False
    return all(c.isalnum() or c == " " for c in text)
