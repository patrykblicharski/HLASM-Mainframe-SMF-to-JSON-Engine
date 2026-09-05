"""Scan a binary IFASMFDP-style dump for Gatherer SMF records."""
from __future__ import annotations

import struct
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .catalog import GATHERER_SUBTYPES, GATHERER_TYPES, title_for
from .ebcdic import ebcdic_to_str, looks_like_ebcdic_id


@dataclass(frozen=True)
class SmfRecordRef:
    offset: int
    length: int
    smf_type: int
    subtype: int
    system_id: str
    subsystem_id: str


@dataclass
class DumpIndex:
    path: Path
    size: int
    records: list[SmfRecordRef] = field(default_factory=list)

    def discovery_rows(self) -> list[dict]:
        """Aggregate type/subtype inventory for the UI list."""
        buckets: dict[tuple[int, int], dict] = {}
        systems: dict[tuple[int, int], set[str]] = defaultdict(set)
        for rec in self.records:
            key = (rec.smf_type, rec.subtype)
            systems[key].add(rec.system_id.strip())
            row = buckets.get(key)
            if row is None:
                buckets[key] = {
                    "type": rec.smf_type,
                    "subtype": rec.subtype,
                    "title": title_for(rec.smf_type, rec.subtype),
                    "count": 1,
                    "systems": "",
                }
            else:
                row["count"] += 1
        rows = []
        for key, row in sorted(buckets.items()):
            row["systems"] = ", ".join(sorted(s for s in systems[key] if s))
            rows.append(row)
        return rows

    def records_for(self, smf_type: int, subtype: int) -> list[SmfRecordRef]:
        return [r for r in self.records if r.smf_type == smf_type and r.subtype == subtype]


def _parse_header_at(data: memoryview, offset: int) -> SmfRecordRef | None:
    if offset + 24 > len(data):
        return None
    length = struct.unpack_from(">H", data, offset)[0]
    if length < 24 or length > 32760 or offset + length > len(data):
        return None
    smf_type = data[offset + 5]
    if smf_type not in GATHERER_TYPES:
        return None
    subtype = struct.unpack_from(">H", data, offset + 22)[0]
    allowed = GATHERER_SUBTYPES.get(smf_type)
    if not allowed or subtype not in allowed:
        return None
    sid_raw = bytes(data[offset + 14 : offset + 18])
    ssi_raw = bytes(data[offset + 18 : offset + 22])
    if not looks_like_ebcdic_id(sid_raw):
        return None
    if not looks_like_ebcdic_id(ssi_raw):
        return None
    # Prefer records that declare subtypes-used (bit 1 of flag byte).
    flag = data[offset + 4]
    if not (flag & 0x02):
        return None
    return SmfRecordRef(
        offset=offset,
        length=length,
        smf_type=smf_type,
        subtype=subtype,
        system_id=ebcdic_to_str(sid_raw),
        subsystem_id=ebcdic_to_str(ssi_raw),
    )


def _candidate_offsets(raw: bytes) -> list[int]:
    """Find offsets where SMF type byte (header+5) is a Gatherer type."""
    n = len(raw)
    found: set[int] = set()
    for smf_type in GATHERER_TYPES:
        needle = bytes([smf_type])
        start = 0
        while True:
            pos = raw.find(needle, start)
            if pos < 0:
                break
            # type is at record_offset+5
            rec_off = pos - 5
            if rec_off >= 0 and rec_off + 24 <= n:
                found.add(rec_off)
            start = pos + 1
    return sorted(found)


def scan_dump(path: str | Path, *, progress=None) -> DumpIndex:
    """Index Gatherer SMF records inside a binary dump file.

    The sample IFASMFDP download is not a clean contiguous RDW stream: SMF
    records sit among padding/other data. We therefore scan for standard
    24-byte SMF headers that match Gatherer type/subtype + EBCDIC SID/SSI.
    """
    path = Path(path)
    raw = path.read_bytes()
    data = memoryview(raw)
    total = len(raw)
    if progress:
        progress(0, total)

    candidates = _candidate_offsets(raw)
    records: list[SmfRecordRef] = []
    occupied: list[tuple[int, int]] = []

    for idx, offset in enumerate(candidates):
        if progress and idx % 2000 == 0:
            progress(min(offset, total), total)
        if any(start <= offset < end for start, end in occupied[-16:]):
            continue
        ref = _parse_header_at(data, offset)
        if ref is None:
            continue
        # Reject overlapping an earlier accepted record
        if any(not (ref.offset + ref.length <= s or ref.offset >= e) for s, e in occupied):
            continue
        records.append(ref)
        occupied.append((ref.offset, ref.offset + ref.length))

    records.sort(key=lambda r: r.offset)
    if progress:
        progress(total, total)
    return DumpIndex(path=path, size=total, records=records)


def read_record_bytes(path: str | Path, ref: SmfRecordRef) -> bytes:
    with open(path, "rb") as fh:
        fh.seek(ref.offset)
        return fh.read(ref.length)
