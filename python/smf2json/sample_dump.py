"""Build minimal synthetic SMF dumps for offline testing."""

from __future__ import annotations

import argparse
from pathlib import Path


def _ebcdic(s: str, n: int) -> bytes:
    return s.encode("cp037")[:n].ljust(n, b"\x40")


def _u16(v: int) -> bytes:
    return int(v).to_bytes(2, "big")


def _u32(v: int) -> bytes:
    return int(v).to_bytes(4, "big")


def _smf_date(year: int, month: int, day: int) -> bytes:
    from datetime import date

    d = date(year, month, day)
    ddd = d.timetuple().tm_yday
    yy = year % 100
    c = 1 if year >= 2000 else 0
    # packed 0c yy ddd F
    nibbles = f"0{c}{yy:02d}{ddd:03d}f"
    return bytes.fromhex(nibbles)


def _smf_time(hh: int, mm: int, ss: int) -> bytes:
    hundredths = ((hh * 3600) + (mm * 60) + ss) * 100
    return _u32(hundredths)


def build_smf30() -> bytes:
    """One type-30 record with header + subsystem + identification + processor."""
    # Layout plan (absolute offsets including RDW):
    # 0-23 header self-defining start
    # triplets at 24,32,40,48,56,64,72,80,88 — we fill SOF,IOF,COF
    # section subsystem at 128
    # identification at 192
    # processor at 400

    buf = bytearray(512)
    # RDW filled at end
    buf[4] = 0x1E  # flags subtypes
    buf[5] = 30
    buf[6:10] = _smf_time(12, 13, 59)
    buf[10:14] = _smf_date(2026, 3, 25)
    buf[14:18] = _ebcdic("PROD", 4)
    buf[18:22] = _ebcdic("JOB", 4)
    buf[22:24] = _u16(4)  # subtype 4 step total (informational)

    sof, iof, cof = 128, 192, 400
    buf[24:28] = _u32(sof)
    buf[28:30] = _u16(40)
    buf[30:32] = _u16(1)
    buf[32:36] = _u32(iof)
    buf[36:38] = _u16(200)
    buf[38:40] = _u16(1)
    buf[56:60] = _u32(cof)
    buf[60:62] = _u16(96)
    buf[62:64] = _u16(1)

    # Subsystem section @128
    buf[sof + 4 : sof + 6] = _ebcdic("05", 2)
    buf[sof + 6 : sof + 14] = _ebcdic("SMF", 8)
    buf[sof + 14 : sof + 22] = _ebcdic("Z/OS", 8)
    buf[sof + 22 : sof + 30] = _ebcdic("SYS1", 8)
    buf[sof + 30 : sof + 38] = _ebcdic("PLEX1", 8)

    # Identification @192
    buf[iof + 0 : iof + 8] = _ebcdic("PAYROLL", 8)
    buf[iof + 8 : iof + 16] = _ebcdic("IFASMFDP", 8)
    buf[iof + 16 : iof + 24] = _ebcdic("STEP1", 8)
    buf[iof + 24 : iof + 32] = _ebcdic("IBMUSER", 8)
    buf[iof + 32 : iof + 40] = _ebcdic("JOB12345", 8)
    buf[iof + 40 : iof + 42] = _u16(1)
    buf[iof + 42] = _ebcdic("A", 1)[0]
    buf[iof + 80 : iof + 100] = _ebcdic("TEST PROGRAMMER", 20)
    buf[iof + 100 : iof + 108] = _ebcdic("SYS1", 8)
    buf[iof + 108 : iof + 116] = _ebcdic("IBMUSER", 8)

    # Processor @400
    buf[cof + 4 : cof + 8] = _u32(1906)  # CPT
    buf[cof + 8 : cof + 12] = _u32(679)  # CPS

    total = 512
    buf[0:2] = _u16(total)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def build_smf80() -> bytes:
    """Type-80 with one relocate section (class name tag 17)."""
    # Fixed header through REL/CNT, then relocate at 128
    rel = 128
    body = bytearray(rel + 32)
    body[4] = 0x00
    body[5] = 80
    body[6:10] = _smf_time(12, 20, 29)
    body[10:14] = _smf_date(2026, 3, 25)
    body[14:18] = _ebcdic("PROD", 4)
    body[18:20] = _u16(0)
    body[20] = 1
    body[21] = 0
    body[22:30] = _ebcdic("IBMUSER", 8)
    body[30:38] = _ebcdic("SYS1", 8)
    body[38:40] = _u16(rel)
    body[40:42] = _u16(2)
    # relocate entries: tag1 old resource, tag17 class
    p = rel
    name = _ebcdic("IBMUSER.REXX", 12)
    body[p] = 1
    body[p + 1] = len(name)
    body[p + 2 : p + 2 + len(name)] = name
    p = p + 2 + len(name)
    cls = _ebcdic("DATASET", 8)
    body[p] = 17
    body[p + 1] = len(cls)
    body[p + 2 : p + 2 + len(cls)] = cls
    total = len(body)
    body[0:2] = _u16(total)
    body[2:4] = b"\x00\x00"
    return bytes(body)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate sample SMF VB dump")
    ap.add_argument("-o", "--output", default="python/samples/sample.smf")
    args = ap.parse_args()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = build_smf30() + build_smf80()
    path.write_bytes(blob)
    print(f"Wrote {path} ({len(blob)} bytes)")


if __name__ == "__main__":
    main()
