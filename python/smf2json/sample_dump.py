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


def _ip4_mapped(a: int, b: int, c: int, d: int) -> bytes:
    return bytes(10) + b"\xff\xff" + bytes((a, b, c, d))


def _ip4_union(a: int, b: int, c: int, d: int) -> bytes:
    """16-byte IP union with IPv4 in the first 4 bytes."""
    return bytes((a, b, c, d)) + bytes(12)


def _u64(v: int) -> bytes:
    return int(v).to_bytes(8, "big")


def _fill_ident(buf: bytearray, ident: int, component: str = "TCP") -> None:
    buf[ident + 0 : ident + 8] = _ebcdic("SYS1", 8)
    buf[ident + 8 : ident + 16] = _ebcdic("PLEX1", 8)
    buf[ident + 16 : ident + 24] = _ebcdic("TCPIP", 8)
    buf[ident + 24 : ident + 32] = _ebcdic("CS&TM", 8)
    buf[ident + 32 : ident + 40] = _ebcdic(component, 8)
    buf[ident + 40 : ident + 48] = _ebcdic("FTPTA5", 8)
    buf[ident + 48 : ident + 56] = _ebcdic("IBMUSER", 8)
    buf[ident + 58 : ident + 60] = _u16(0x001A)
    buf[ident + 60] = 0x08


def _smf119_header(buf: bytearray, subtype: int, ntrip: int, ident: int) -> None:
    buf[4] = 0x1E  # new format + subtypes
    buf[5] = 119
    buf[6:10] = _smf_time(14, 4, 6)
    buf[10:14] = _smf_date(2026, 3, 25)
    buf[14:18] = _ebcdic("PROD", 4)
    buf[18:22] = _ebcdic("TCP", 4)
    buf[22:24] = _u16(subtype)
    buf[24:26] = _u16(ntrip)
    buf[28:32] = _u32(ident)
    buf[32:34] = _u16(64)
    buf[34:36] = _u16(1)


def build_smf119_st01() -> bytes:
    """Type 119 subtype 1 — TCP connection initiation (ident + S1)."""
    ident, s1 = 88, 152
    total = s1 + 72
    buf = bytearray(total)
    _smf119_header(buf, 1, 2, ident)
    buf[36:40] = _u32(s1)
    buf[40:42] = _u16(72)
    buf[42:44] = _u16(1)
    _fill_ident(buf, ident, "TCP")

    buf[s1 + 0 : s1 + 8] = _ebcdic("FTPTA5", 8)
    buf[s1 + 8 : s1 + 12] = _u32(0x0000A1B2)
    buf[s1 + 16 : s1 + 20] = bytes.fromhex("00ABCDEF")
    buf[s1 + 20 : s1 + 36] = _ip4_mapped(10, 1, 2, 3)
    buf[s1 + 36 : s1 + 52] = _ip4_mapped(192, 168, 1, 10)
    buf[s1 + 52 : s1 + 54] = _u16(443)
    buf[s1 + 54 : s1 + 56] = _u16(21)
    buf[s1 + 56 : s1 + 60] = _smf_time(14, 4, 6)
    buf[s1 + 60 : s1 + 64] = _smf_date(2026, 3, 25)
    buf[s1 + 64 : s1 + 72] = bytes.fromhex("00DECAFBAD010203")

    buf[0:2] = _u16(total)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def build_smf119_st02() -> bytes:
    """Type 119 subtype 2 — TCP connection termination (ident + S1)."""
    ident, s1 = 88, 152
    s1_len = 216
    total = s1 + s1_len
    buf = bytearray(total)
    _smf119_header(buf, 2, 2, ident)
    buf[36:40] = _u32(s1)
    buf[40:42] = _u16(s1_len)
    buf[42:44] = _u16(1)
    _fill_ident(buf, ident, "TCP")

    buf[s1 + 0 : s1 + 8] = _ebcdic("FTPTA5", 8)
    buf[s1 + 8 : s1 + 12] = _u32(0x0000A1B2)
    buf[s1 + 14] = 0x21  # term_code
    buf[s1 + 16 : s1 + 20] = bytes.fromhex("00ABCDEF")
    buf[s1 + 20 : s1 + 24] = _smf_time(14, 4, 6)
    buf[s1 + 24 : s1 + 28] = _smf_date(2026, 3, 25)
    buf[s1 + 28 : s1 + 32] = _smf_time(14, 5, 1)
    buf[s1 + 32 : s1 + 36] = _smf_date(2026, 3, 25)
    buf[s1 + 36 : s1 + 52] = _ip4_mapped(10, 1, 2, 3)
    buf[s1 + 52 : s1 + 68] = _ip4_mapped(192, 168, 1, 10)
    buf[s1 + 68 : s1 + 70] = _u16(443)
    buf[s1 + 70 : s1 + 72] = _u16(21)
    buf[s1 + 72 : s1 + 80] = _u64(4096)
    buf[s1 + 80 : s1 + 88] = _u64(2048)
    buf[s1 + 112] = 0x01  # active open

    buf[0:2] = _u16(total)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def build_smf119_st03() -> bytes:
    """Type 119 subtype 3 — FTP client completion (ident + S1 + filename)."""
    ident, s1 = 88, 152
    s1_len = 172
    name = _ebcdic("USER.FTP.DATA", 13)
    s2 = s1 + s1_len
    total = s2 + len(name)
    buf = bytearray(total)
    _smf119_header(buf, 3, 3, ident)
    buf[36:40] = _u32(s1)
    buf[40:42] = _u16(s1_len)
    buf[42:44] = _u16(1)
    buf[44:48] = _u32(s2)
    buf[48:50] = _u16(len(name))
    buf[50:52] = _u16(1)
    _fill_ident(buf, ident, "FTPC")

    buf[s1 + 0 : s1 + 4] = _ebcdic("RETR", 4)
    buf[s1 + 4 : s1 + 8] = _ebcdic("SEQ", 4)
    buf[s1 + 8 : s1 + 24] = _ip4_mapped(10, 1, 2, 3)
    buf[s1 + 24 : s1 + 40] = _ip4_mapped(192, 168, 1, 10)
    buf[s1 + 80 : s1 + 88] = _ebcdic("FTPUSER", 8)
    buf[s1 + 88 : s1 + 96] = _ebcdic("IBMUSER", 8)
    buf[s1 + 120 : s1 + 128] = _u64(8192)
    buf[s2 : s2 + len(name)] = name

    buf[0:2] = _u16(total)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def build_smf119_st10() -> bytes:
    """Type 119 subtype 10 — UDP endpoint close (ident + S1)."""
    ident, s1 = 88, 152
    s1_len = 104
    total = s1 + s1_len
    buf = bytearray(total)
    _smf119_header(buf, 10, 2, ident)
    buf[36:40] = _u32(s1)
    buf[40:42] = _u16(s1_len)
    buf[42:44] = _u16(1)
    _fill_ident(buf, ident, "UDP")

    buf[s1 + 0 : s1 + 8] = _ebcdic("UDPSRV", 8)
    buf[s1 + 8 : s1 + 12] = _u32(0x00000BEE)
    buf[s1 + 16 : s1 + 20] = _smf_time(14, 4, 6)
    buf[s1 + 20 : s1 + 24] = _smf_date(2026, 3, 25)
    buf[s1 + 24 : s1 + 28] = _smf_time(14, 6, 0)
    buf[s1 + 28 : s1 + 32] = _smf_date(2026, 3, 25)
    buf[s1 + 32 : s1 + 48] = _ip4_mapped(10, 9, 8, 7)
    buf[s1 + 48 : s1 + 64] = _ip4_mapped(192, 168, 1, 10)
    buf[s1 + 64 : s1 + 66] = _u16(53)
    buf[s1 + 66 : s1 + 68] = _u16(5353)
    buf[s1 + 88 : s1 + 96] = _u64(100)
    buf[s1 + 96 : s1 + 104] = _u64(200)

    buf[0:2] = _u16(total)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def build_smf119_st32() -> bytes:
    """Type 119 subtype 32 — DVIPA status change (ident + S1, IPv4 union)."""
    ident, s1 = 88, 152
    s1_len = 40
    total = s1 + s1_len
    buf = bytearray(total)
    _smf119_header(buf, 32, 2, ident)
    buf[36:40] = _u32(s1)
    buf[40:42] = _u16(s1_len)
    buf[42:44] = _u16(1)
    _fill_ident(buf, ident, "STACK")

    buf[s1 + 8 : s1 + 24] = _ip4_union(10, 20, 30, 40)
    buf[s1 + 24 : s1 + 32] = _ebcdic("DVIPA1", 8)

    buf[0:2] = _u16(total)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate sample SMF VB dump")
    ap.add_argument("-o", "--output", default="python/samples/sample.smf")
    args = ap.parse_args()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = (
        build_smf30()
        + build_smf80()
        + build_smf119_st01()
        + build_smf119_st02()
        + build_smf119_st03()
        + build_smf119_st10()
    )
    path.write_bytes(blob)
    print(f"Wrote {path} ({len(blob)} bytes)")


if __name__ == "__main__":
    main()
