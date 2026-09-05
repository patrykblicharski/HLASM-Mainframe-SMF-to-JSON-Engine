"""Scan a binary dump for SMF Type 119 records."""
from __future__ import annotations

import struct
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .ebcdic import ebcdic_to_str, looks_like_ebcdic_id
from .subtypes import FLAG_SUBTYPES_USED, SMF_TYPE_119, title_for


@dataclass(frozen=True)
class Smf119Ref:
    offset: int
    length: int
    subtype: int
    system_id: str
    subsystem_id: str


@dataclass
class DumpIndex:
    path: Path
    size: int
    records: list[Smf119Ref] = field(default_factory=list)

    def discovery_rows(self) -> list[dict]:
        buckets: dict[int, dict] = {}
        systems: dict[int, set[str]] = defaultdict(set)
        for rec in self.records:
            systems[rec.subtype].add(rec.system_id.strip())
            row = buckets.get(rec.subtype)
            if row is None:
                buckets[rec.subtype] = {
                    "subtype": rec.subtype,
                    "title": title_for(rec.subtype),
                    "count": 1,
                    "systems": "",
                }
            else:
                row["count"] += 1
        rows = []
        for subtype, row in sorted(buckets.items()):
            row["systems"] = ", ".join(sorted(s for s in systems[subtype] if s))
            rows.append(row)
        return rows

    def records_for(self, subtype: int) -> list[Smf119Ref]:
        return [r for r in self.records if r.subtype == subtype]


def _parse_header_at(data: memoryview, offset: int) -> Smf119Ref | None:
    if offset + 24 > len(data):
        return None
    length = struct.unpack_from(">H", data, offset)[0]
    if length < 28 or length > 32756 or offset + length > len(data):
        return None
    if data[offset + 5] != SMF_TYPE_119:
        return None
    flag = data[offset + 4]
    if not (flag & FLAG_SUBTYPES_USED):
        return None
    sid_raw = bytes(data[offset + 14 : offset + 18])
    ssi_raw = bytes(data[offset + 18 : offset + 22])
    if not looks_like_ebcdic_id(sid_raw):
        return None
    if not looks_like_ebcdic_id(ssi_raw):
        return None
    subtype = struct.unpack_from(">H", data, offset + 22)[0]
    return Smf119Ref(
        offset=offset,
        length=length,
        subtype=subtype,
        system_id=ebcdic_to_str(sid_raw),
        subsystem_id=ebcdic_to_str(ssi_raw),
    )


def _candidate_offsets(raw: bytes) -> list[int]:
    needle = bytes([SMF_TYPE_119])
    found: set[int] = set()
    start = 0
    n = len(raw)
    while True:
        pos = raw.find(needle, start)
        if pos < 0:
            break
        rec_off = pos - 5
        if rec_off >= 0 and rec_off + 24 <= n:
            found.add(rec_off)
        start = pos + 1
    return sorted(found)


def scan_dump(path: str | Path, *, progress=None) -> DumpIndex:
    """Index SMF 119 records inside a binary IFASMFDP-style dump."""
    path = Path(path)
    raw = path.read_bytes()
    data = memoryview(raw)
    total = len(raw)
    if progress:
        progress(0, total)

    candidates = _candidate_offsets(raw)
    records: list[Smf119Ref] = []
    occupied: list[tuple[int, int]] = []

    for idx, offset in enumerate(candidates):
        if progress and idx % 2000 == 0:
            progress(min(offset, total), total)
        if any(start <= offset < end for start, end in occupied[-16:]):
            continue
        ref = _parse_header_at(data, offset)
        if ref is None:
            continue
        if any(not (ref.offset + ref.length <= s or ref.offset >= e) for s, e in occupied):
            continue
        records.append(ref)
        occupied.append((ref.offset, ref.offset + ref.length))

    records.sort(key=lambda r: r.offset)
    if progress:
        progress(total, total)
    return DumpIndex(path=path, size=total, records=records)


def read_record_bytes(path: str | Path, ref: Smf119Ref) -> bytes:
    with open(path, "rb") as fh:
        fh.seek(ref.offset)
        return fh.read(ref.length)
