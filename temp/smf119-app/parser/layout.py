"""Packed big-endian field layout engine for SMF 119 / NMTP sections."""
from __future__ import annotations

import ipaddress
import struct
from dataclasses import dataclass, field
from typing import Any, Iterable

from .ebcdic import ebcdic_eye_u32, ebcdic_to_str

_SCALAR = {
    "u8": (1, "B"),
    "i8": (1, "b"),
    "u16": (2, "H"),
    "i16": (2, "h"),
    "u32": (4, "I"),
    "i32": (4, "i"),
    "u64": (8, "Q"),
    "i64": (8, "q"),
}


@dataclass(frozen=True)
class FieldSpec:
    """One packed field in a C-style SMF/NMTP structure."""

    name: str
    kind: str
    description: str = ""
    size: int | None = None
    flags: dict[int, str] | None = None
    enum: dict[int, str] | None = None
    reserved: bool = False
    decode: str | None = None
    label: str | None = None  # short UI label; defaults to description or name


@dataclass
class StructLayout:
    name: str
    fields: list[FieldSpec]
    description: str = ""
    eyecatcher: int | None = None
    variable: bool = False  # whole section size = triplet Len
    size: int = field(init=False)
    offsets: dict[str, int] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        off = 0
        offsets: dict[str, int] = {}
        for f in self.fields:
            offsets[f.name] = off
            if f.kind == "var_ebcdic":
                # size determined at decode time; do not advance fixed size
                continue
            off += field_size(f)
        self.size = off
        self.offsets = offsets


def field_size(f: FieldSpec) -> int:
    if f.kind in _SCALAR:
        return _SCALAR[f.kind][0]
    if f.kind in ("char", "bytes", "hex", "raw"):
        if f.size is None:
            raise ValueError(f"{f.name}: size required for kind={f.kind}")
        return f.size
    if f.kind == "ipv4":
        return 4
    if f.kind in ("ipv6", "ipv6mapped"):
        return 16
    if f.kind == "ipunion":
        return f.size or 16
    if f.kind == "var_ebcdic":
        return f.size or 0
    raise ValueError(f"unknown kind {f.kind!r} on {f.name}")


def short_label(f: FieldSpec) -> str:
    if f.label:
        return f.label
    if f.description:
        # first clause / first 40 chars
        desc = f.description.split(":")[0].split(".")[0].strip()
        return desc[:48] if desc else f.name
    return f.name


def _fmt_flags(value: int, flags: dict[int, str] | None) -> str:
    if not flags or value == 0:
        return ""
    names = [label for bit, label in sorted(flags.items(), reverse=True) if value & bit]
    return ",".join(names)


def _decode_ipv6mapped(chunk: bytes) -> str:
    """Decode 16-byte IPv4-mapped or real IPv6 address to readable form."""
    if len(chunk) < 16:
        return chunk.hex()
    # IPv4-mapped: ::ffff:a.b.c.d
    if chunk[:10] == b"\x00" * 10 and chunk[10:12] == b"\xff\xff":
        return str(ipaddress.IPv4Address(chunk[12:16]))
    # IPv4-compatible (legacy) or plain IPv4 in last 4 with zeros
    if chunk[:12] == b"\x00" * 12:
        return str(ipaddress.IPv4Address(chunk[12:16]))
    return str(ipaddress.IPv6Address(chunk[:16]))


def _decode_value(chunk: bytes, f: FieldSpec) -> Any:
    kind = f.kind
    hint = f.decode

    if kind in _SCALAR:
        fmt = ">" + _SCALAR[kind][1]
        (val,) = struct.unpack(fmt, chunk)
        if hint == "eye" or f.name.endswith("Eye") or f.name.endswith("EYE"):
            return {"value": val, "hex": f"0x{val:08X}", "ebcdic": ebcdic_eye_u32(val)}
        if f.enum is not None:
            return {"value": val, "name": f.enum.get(val, "?")}
        if f.flags is not None:
            return {"value": val, "hex": f"0x{val:X}", "flags": _fmt_flags(val, f.flags)}
        return val

    if kind == "var_ebcdic" or (kind == "char" and hint == "ebcdic") or kind == "char":
        return ebcdic_to_str(chunk).rstrip()

    if kind == "ipv4" or hint == "ipv4":
        return str(ipaddress.IPv4Address(chunk[:4]))

    if kind == "ipv6mapped" or hint == "ipv6mapped":
        return _decode_ipv6mapped(chunk)

    if kind == "ipv6" or hint == "ipv6":
        return str(ipaddress.IPv6Address(chunk[:16]))

    if kind == "ipunion":
        v4 = str(ipaddress.IPv4Address(chunk[:4]))
        v6 = _decode_ipv6mapped(chunk[:16]) if len(chunk) >= 16 else v4
        return {"ipv4": v4, "ipv6": v6, "hex": chunk.hex()}

    if kind in ("bytes", "hex", "raw") or hint in ("hex", "tod_hex", "date_hex"):
        return chunk.hex()

    return chunk.hex()


def decode_struct(
    data: bytes,
    layout: StructLayout,
    *,
    base: int = 0,
    section_len: int | None = None,
) -> dict[str, Any]:
    """Decode one packed structure instance into a field dict."""
    out: dict[str, Any] = {
        "_layout": layout.name,
        "_offset": base,
        "_size": layout.size if not layout.variable else (section_len or len(data)),
    }
    effective_size = section_len if (layout.variable and section_len) else layout.size
    if len(data) < (layout.size if not layout.variable else 0) and not layout.variable:
        out["_truncated"] = True
        out["_available"] = len(data)

    for f in layout.fields:
        if f.reserved:
            continue
        off = layout.offsets[f.name]
        if f.kind == "var_ebcdic":
            # consume remaining section bytes
            end = section_len if section_len is not None else len(data)
            chunk = data[off:end]
            out[f.name] = _decode_value(chunk, f)
            continue
        sz = field_size(f)
        if off + sz > len(data):
            out[f.name] = None
            continue
        chunk = data[off : off + sz]
        out[f.name] = _decode_value(chunk, f)

    if layout.eyecatcher is not None and len(data) >= 4:
        eye = struct.unpack_from(">I", data, 0)[0]
        out["_eye_ok"] = eye == layout.eyecatcher
        out["_eye"] = ebcdic_eye_u32(eye)
    return out


def decode_repeated(
    data: bytes,
    layout: StructLayout,
    count: int,
    *,
    entry_len: int | None = None,
) -> list[dict[str, Any]]:
    """Decode ``count`` consecutive instances."""
    if layout.variable:
        # single variable blob (count should be 1 typically)
        return [decode_struct(data, layout, section_len=len(data))]
    stride = entry_len or layout.size
    rows: list[dict[str, Any]] = []
    for i in range(count):
        start = i * stride
        if start >= len(data):
            break
        chunk = data[start : start + min(stride, max(layout.size, 1), len(data) - start)]
        row = decode_struct(chunk, layout, base=start, section_len=stride)
        row["_index"] = i
        rows.append(row)
    return rows


def flatten_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        if "ebcdic" in value and "hex" in value:
            return f"{value['ebcdic']} ({value['hex']})"
        if "name" in value and "value" in value:
            return f"{value['value']} ({value['name']})"
        if "flags" in value:
            flags = value["flags"]
            return f"{value.get('hex', value.get('value'))}" + (f" [{flags}]" if flags else "")
        if "ipv4" in value and "ipv6" in value:
            return f"v4={value['ipv4']} v6={value['ipv6']}"
        return str(value)
    return str(value)


def iter_field_rows(
    decoded: dict[str, Any], layout: StructLayout, *, use_labels: bool = False
) -> Iterable[tuple[str, str, str]]:
    for f in layout.fields:
        if f.reserved:
            continue
        header = short_label(f) if use_labels else f.name
        yield header, flatten_value(decoded.get(f.name)), f.description


def build_layout(
    name: str,
    fields: list[FieldSpec],
    *,
    description: str = "",
    eyecatcher: int | None = None,
    variable: bool = False,
) -> StructLayout:
    return StructLayout(
        name=name,
        fields=fields,
        description=description,
        eyecatcher=eyecatcher,
        variable=variable,
    )


def U8(name: str, desc: str = "", **kw: Any) -> FieldSpec:
    return FieldSpec(name, "u8", desc, **kw)


def U16(name: str, desc: str = "", **kw: Any) -> FieldSpec:
    return FieldSpec(name, "u16", desc, **kw)


def U32(name: str, desc: str = "", **kw: Any) -> FieldSpec:
    return FieldSpec(name, "u32", desc, **kw)


def U64(name: str, desc: str = "", **kw: Any) -> FieldSpec:
    return FieldSpec(name, "u64", desc, **kw)


def I16(name: str, desc: str = "", **kw: Any) -> FieldSpec:
    return FieldSpec(name, "i16", desc, **kw)


def I32(name: str, desc: str = "", **kw: Any) -> FieldSpec:
    return FieldSpec(name, "i32", desc, **kw)


def CHAR(name: str, n: int, desc: str = "", **kw: Any) -> FieldSpec:
    return FieldSpec(name, "char", desc, size=n, decode="ebcdic", **kw)


def BYTES(name: str, n: int, desc: str = "", **kw: Any) -> FieldSpec:
    return FieldSpec(name, "bytes", desc, size=n, decode=kw.pop("decode", "hex"), **kw)


def IPV4(name: str, desc: str = "") -> FieldSpec:
    return FieldSpec(name, "ipv4", desc, size=4, decode="ipv4")


def IPV6(name: str, desc: str = "") -> FieldSpec:
    return FieldSpec(name, "ipv6", desc, size=16, decode="ipv6")


def IPV6MAPPED(name: str, desc: str = "") -> FieldSpec:
    return FieldSpec(name, "ipv6mapped", desc, size=16, decode="ipv6mapped")


def IPUNION(name: str, desc: str = "") -> FieldSpec:
    return FieldSpec(name, "ipunion", desc, size=16)


def VAR_EBCDIC(name: str, desc: str = "") -> FieldSpec:
    return FieldSpec(name, "var_ebcdic", desc, size=0, decode="ebcdic")


def RES(name: str, n: int) -> FieldSpec:
    return FieldSpec(name, "raw", "Reserved", size=n, reserved=True)


def EYE(name: str, desc: str = "Eyecatcher") -> FieldSpec:
    return FieldSpec(name, "u32", desc, decode="eye")
