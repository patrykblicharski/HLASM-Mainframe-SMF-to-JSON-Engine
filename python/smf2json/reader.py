"""VB / VBS SMF dump reader (RDW-framed records)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterator, List, Optional


LogFn = Callable[[str], None]


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


def iter_vb_records(
    blob: bytes,
    *,
    skip_types: Optional[set[int]] = None,
    log: Optional[LogFn] = None,
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
    log = log or (lambda _m: None)
    n = len(blob)
    pos = 0
    idx = 0
    pending: List[bytes] = []
    pending_rdw_len = 0

    while pos + 4 <= n:
        rdw = blob[pos : pos + 4]
        rec_len = int.from_bytes(rdw[0:2], "big")
        flags = rdw[2]
        if rec_len < 4 or pos + rec_len > n:
            log(f"WARN: bad RDW at offset {pos}: len={rec_len} — stopping")
            break

        segment = blob[pos : pos + rec_len]  # includes RDW
        pos += rec_len

        # Spanned records: bit flags in byte 2 — x'01' first, x'02' last, x'03' middle
        # Non-spanned: flags == 0
        if flags == 0x00:
            payload = segment
            if pending:
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
                log(f"DEBUG: assembled spanned record idx={idx} bytes={total}")
            else:
                log(f"DEBUG: spanned segment flags=0x{flags:02X} at idx~{idx}")
                continue

        if len(payload) <= 5:
            continue
        rty = payload[5]
        if rty in skip_types:
            log(f"DEBUG: skip type {rty} (dump control)")
            continue

        rec = SmfRecord(index=idx, rdw_length=int.from_bytes(payload[0:2], "big"), span_flags=0, data=payload)
        log(f"DEBUG: record[{idx}] type={rty} len={rec.rdw_length}")
        idx += 1
        yield rec


def read_dump(path: str, log: Optional[LogFn] = None) -> List[SmfRecord]:
    with open(path, "rb") as f:
        blob = f.read()
    if log:
        log(f"INFO: loaded {path} ({len(blob)} bytes)")
    return list(iter_vb_records(blob, log=log))
