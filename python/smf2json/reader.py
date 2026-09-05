"""VB / VBS SMF dump reader (RDW-framed records)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterator, List, Optional


LogFn = Callable[[str], None]
ProgressFn = Callable[[int, int], None]


@dataclass
class SmfRecord:
    index: int
    rdw_length: int
    span_flags: int
    data: bytes  # payload after RDW (starts at SMFxLEN mapping = includes RDW in IBM offsets)

    @property
    def record_type(self) -> int:
        # IBM offsets include RDW: SMFxRTY at offset 5 from SMFxLEN
        if len(self.data) > 5:
            return self.data[5]
        return -1

    @property
    def subtype(self) -> Optional[int]:
        # SMFxSTY at offset 22 when the header uses subtypes
        if len(self.data) >= 24:
            return int.from_bytes(self.data[22:24], "big")
        return None


def _looks_packed_date(raw: bytes) -> bool:
    if len(raw) < 4:
        return False
    if raw[3] & 0x0F not in (0x0C, 0x0F):
        return False
    try:
        ddd = int(raw.hex()[4:7], 10)
    except ValueError:
        return False
    return 1 <= ddd <= 366


def _is_bdw_at(blob: bytes, pos: int, n: int) -> bool:
    """True when pos is a block descriptor, not an SMF RDW."""
    if pos + 18 > n:
        return False
    block_ll = int.from_bytes(blob[pos : pos + 2], "big")
    if blob[pos + 2] != 0 or blob[pos + 3] != 0:
        return False
    if block_ll < 8 or pos + block_ll > n:
        return False
    inner_ll = int.from_bytes(blob[pos + 4 : pos + 6], "big")
    if inner_ll < 18 or 4 + inner_ll > block_ll:
        return False
    date_at_10 = _looks_packed_date(blob[pos + 10 : pos + 14])
    date_at_14 = _looks_packed_date(blob[pos + 14 : pos + 18])
    # Classic SMF: packed date at +10, SID at +14.
    if date_at_10 and not date_at_14:
        return False
    inner_rty = blob[pos + 9]
    inner_flg = blob[pos + 8]
    if date_at_14 and inner_rty != 0:
        if inner_flg & 0x1E == 0x1E or inner_rty in (30, 80, 89, 119):
            return True
    return False


def normalize_smf_payload(payload: bytes) -> bytes:
    """Ensure ``data`` starts at SMFxLEN (4-byte RDW) so IBM offsets apply."""
    if len(payload) < 6:
        return payload
    if _looks_packed_date(payload[10:14]) and payload[5] != 0:
        return payload
    if len(payload) >= 18 and _looks_packed_date(payload[14:18]) and payload[9] != 0:
        return payload[4:]
    if len(payload) >= 14 and payload[1] != 0 and _looks_packed_date(payload[6:10]):
        total = len(payload) + 4
        return total.to_bytes(2, "big") + b"\x00\x00" + payload
    return payload


def iter_vb_records(
    blob: bytes,
    *,
    skip_types: Optional[set[int]] = None,
    log: Optional[LogFn] = None,
    progress: Optional[ProgressFn] = None,
) -> Iterator[SmfRecord]:
    """
    Walk a binary SMF dump.

    Supports:
    - RECFM=VB  (RDW LL00 + data; span flags usually 0)
    - RECFM=VBS (spanned): assemble segments until complete

    IBM SMF mappings treat the record as starting at the RDW (SMFxLEN).
    We therefore keep the 4-byte RDW prefix inside ``data`` so offsets
    from IFASMFR / pacsys tables apply directly.
    """
    skip_types = skip_types or {2, 3}
    n = len(blob)
    pos = 0
    idx = 0
    pending: List[bytes] = []
    pending_rdw_len = 0

    while pos + 4 <= n:
        if _is_bdw_at(blob, pos, n):
            pos += 4
            continue
        rdw = blob[pos : pos + 4]
        rec_len = int.from_bytes(rdw[0:2], "big")
        flags = rdw[2]
        if rec_len < 4 or pos + rec_len > n:
            rest = blob[pos:]
            if len(rest) >= 14 and rest[1] != 0 and _looks_packed_date(rest[6:10]):
                payload = normalize_smf_payload(rest)
                pos = n
                if progress:
                    progress(pos, n)
                if len(payload) > 5 and payload[5] not in skip_types:
                    rec = SmfRecord(
                        index=idx,
                        rdw_length=int.from_bytes(payload[0:2], "big"),
                        span_flags=0,
                        data=payload,
                    )
                    idx += 1
                    yield rec
                break
            if log:
                log(f"WARN: bad RDW at offset {pos}: len={rec_len} — stopping")
            break

        segment = blob[pos : pos + rec_len]  # includes RDW
        pos += rec_len
        if progress:
            progress(pos, n)

        # Spanned records: bit flags in byte 2 — x'01' first, x'02' last, x'03' middle
        # Non-spanned: flags == 0
        if flags == 0x00:
            payload = segment
            if pending:
                if log:
                    log(f"WARN: discarding incomplete spanned group before record @{pos}")
                pending.clear()
        else:
            # spanned segment — strip RDW from continuation pieces when assembling
            if not pending:
                pending_rdw_len = rec_len
                pending.append(segment)
            else:
                pending.append(segment[4:])  # append data only
            is_last = bool(flags & 0x02) and not bool(flags & 0x01 and flags == 0x01)
            # Common convention: 0x01=first, 0x02=last, 0x03=middle
            if flags == 0x02 or (flags & 0x02):
                # complete
                payload = b"".join(pending)
                # fix RDW length of assembled record to total size
                total = len(payload)
                payload = total.to_bytes(2, "big") + b"\x00\x00" + payload[4:]
                pending.clear()
                if log:
                    log(f"DEBUG: assembled spanned record idx={idx} bytes={total}")
            else:
                if log:
                    log(f"DEBUG: spanned segment flags=0x{flags:02X} at idx~{idx}")
                continue

        payload = normalize_smf_payload(payload)
        if len(payload) <= 5:
            continue
        rty = payload[5]
        if rty in skip_types:
            if log:
                log(f"DEBUG: skip type {rty} (dump control)")
            continue

        rec = SmfRecord(index=idx, rdw_length=int.from_bytes(payload[0:2], "big"), span_flags=0, data=payload)
        if log:
            log(f"DEBUG: record[{idx}] type={rty} len={rec.rdw_length}")
        idx += 1
        yield rec


def iter_dump(
    path: str,
    log: Optional[LogFn] = None,
    progress: Optional[ProgressFn] = None,
) -> Iterator[SmfRecord]:
    """Read the dump once, then yield records without building a full list."""
    with open(path, "rb") as f:
        blob = f.read()
    if log:
        log(f"INFO: loaded {path} ({len(blob)} bytes)")
    if progress:
        progress(0, len(blob))
    yield from iter_vb_records(blob, log=log, progress=progress)
    if progress:
        progress(len(blob), len(blob))


def read_dump(path: str, log: Optional[LogFn] = None) -> List[SmfRecord]:
    return list(iter_dump(path, log=log))
