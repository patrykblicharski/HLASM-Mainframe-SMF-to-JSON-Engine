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


def build_smf17() -> bytes:
    """Type 17 — Scratch Data Set Status (one volume)."""
    # Fixed through SMF17NVL @91, then one 8-byte volume entry @92.
    total = 100
    buf = bytearray(total)
    buf[4] = 0x00
    buf[5] = 17
    buf[6:10] = _smf_time(15, 30, 0)
    buf[10:14] = _smf_date(2026, 3, 25)
    buf[14:18] = _ebcdic("PROD", 4)
    buf[18:26] = _ebcdic("SCRJOB01", 8)
    buf[26:30] = _smf_time(9, 0, 0)
    buf[30:34] = _smf_date(2026, 3, 25)
    buf[34:42] = _ebcdic("IBMUSER", 8)
    buf[42:44] = b"\x00\x00"  # SMF17RIN reserved
    buf[44:88] = _ebcdic("IBMUSER.TEMP.DATA", 44)
    buf[91] = 1  # SMF17NVL
    buf[94:100] = _ebcdic("SCR001", 6)
    buf[0:2] = _u16(total)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def build_smf15() -> bytes:
    """Type 15 — OUTPUT data set activity (header + TIOT/JFCB + DCB/DEB + one UCB)."""
    # Fixed layout: DCB/DEB @244 (SDC=28), first UCB @272, UCB size 24 (DASD + tracks).
    sdc, nuc, suc = 28, 1, 24
    ucb = 244 + sdc
    total = ucb + suc
    buf = bytearray(total)
    buf[4] = 0x00
    buf[5] = 15
    buf[6:10] = _smf_time(15, 30, 45)
    buf[10:14] = _smf_date(2026, 3, 25)
    buf[14:18] = _ebcdic("PROD", 4)
    buf[18:26] = _ebcdic("PAYROLL", 8)
    buf[26:30] = _smf_time(8, 0, 1)
    buf[30:34] = _smf_date(2026, 3, 25)
    buf[34:42] = _ebcdic("IBMUSER", 8)
    buf[42:44] = b"\x20\x00"  # SMF15RIN: DASD (bit 2)
    buf[44] = sdc
    buf[45] = nuc
    buf[46] = suc
    buf[47] = 0
    buf[48:52] = _smf_time(15, 0, 0)
    # TIOT DDNAME @56
    buf[56:64] = _ebcdic("SYSOUT", 8)
    # JFCB
    buf[68:112] = _ebcdic("SYS1.PAYROLL.OUT", 44)
    buf[112:120] = _ebcdic("MEMBER1", 8)
    buf[155] = 0xC0  # DISP=NEW
    buf[166] = 0x40  # PS
    buf[168] = 0x90  # FB
    buf[170:172] = _u16(32760)
    buf[172:174] = _u16(80)
    buf[185] = 1
    buf[186:192] = _ebcdic("WORK01", 6)
    # DCB/DEB @244 + DASD open date @268
    buf[244:246] = b"\x40\x00"  # DSORG=PS
    buf[246] = 0x90
    buf[268:272] = _smf_date(2026, 3, 25)
    # UCB @272
    buf[ucb : ucb + 2] = b"\x1A\x2B"  # device
    buf[ucb + 2 : ucb + 8] = _ebcdic("WORK01", 6)
    buf[ucb + 8 : ucb + 12] = b"\x20\x10\x0F\x01"  # unit type
    buf[ucb + 13] = 3  # extents
    buf[ucb + 16 : ucb + 20] = _u32(1234)  # EXCP
    buf[ucb + 20 : ucb + 24] = _u32(150)  # tracks allocated

    buf[0:2] = _u16(total)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def _smf30_header(buf: bytearray, subtype: int) -> None:
    buf[4] = 0x1E  # new format + subtypes
    buf[5] = 30
    buf[6:10] = _smf_time(12, 13, 59)
    buf[10:14] = _smf_date(2026, 3, 25)
    buf[14:18] = _ebcdic("PROD", 4)
    buf[18:22] = _ebcdic("JOB", 4)
    buf[22:24] = _u16(subtype)


def _smf30_subsystem(buf: bytearray, sof: int) -> None:
    buf[sof + 4 : sof + 6] = _ebcdic("05", 2)
    buf[sof + 6 : sof + 14] = _ebcdic("SMF", 8)
    buf[sof + 14 : sof + 22] = _ebcdic("Z/OS", 8)
    buf[sof + 22 : sof + 30] = _ebcdic("SYS1", 8)
    buf[sof + 30 : sof + 38] = _ebcdic("PLEX1", 8)


def _smf30_identification(buf: bytearray, iof: int, *, job: str = "PAYROLL") -> None:
    buf[iof + 0 : iof + 8] = _ebcdic(job, 8)
    buf[iof + 8 : iof + 16] = _ebcdic("IFASMFDP", 8)
    buf[iof + 16 : iof + 24] = _ebcdic("STEP1", 8)
    buf[iof + 24 : iof + 32] = _ebcdic("IBMUSER", 8)
    buf[iof + 32 : iof + 40] = _ebcdic("JOB12345", 8)
    buf[iof + 40 : iof + 42] = _u16(1)
    buf[iof + 42] = _ebcdic("A", 1)[0]
    buf[iof + 80 : iof + 100] = _ebcdic("TEST PROGRAMMER", 20)
    buf[iof + 100 : iof + 108] = _ebcdic("SYS1", 8)
    buf[iof + 108 : iof + 116] = _ebcdic("IBMUSER", 8)


def _smf30_triplet(buf: bytearray, trip: int, off: int, length: int, number: int = 1) -> None:
    buf[trip : trip + 4] = _u32(off)
    buf[trip + 4 : trip + 6] = _u16(length)
    buf[trip + 6 : trip + 8] = _u16(number)


def build_smf30() -> bytes:
    """Type-30 subtype 4 (step total) — header + subsystem + identification + processor.

    Historical synthetic layout used by unit tests; preserves offsets/values.
    """
    # Layout plan (absolute offsets including RDW):
    # triplets SOF@24, IOF@32, COF@56 — subsystem@128, identification@192, processor@400
    buf = bytearray(512)
    _smf30_header(buf, 4)

    sof, iof, cof = 128, 192, 400
    _smf30_triplet(buf, 24, sof, 40)
    _smf30_triplet(buf, 32, iof, 200)
    _smf30_triplet(buf, 56, cof, 96)

    _smf30_subsystem(buf, sof)
    _smf30_identification(buf, iof)

    buf[cof + 4 : cof + 8] = _u32(1906)  # CPT
    buf[cof + 8 : cof + 12] = _u32(679)  # CPS

    buf[0:2] = _u16(512)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def build_smf30_st01() -> bytes:
    """Type-30 subtype 1 (job initiation) — header + subsystem + identification only."""
    buf = bytearray(400)
    _smf30_header(buf, 1)
    sof, iof = 128, 192
    _smf30_triplet(buf, 24, sof, 40)
    _smf30_triplet(buf, 32, iof, 200)
    _smf30_subsystem(buf, sof)
    _smf30_identification(buf, iof, job="INITJOB1")
    buf[0:2] = _u16(400)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def build_smf30_st05() -> bytes:
    """Type-30 subtype 5 (job termination) — identification + completion + processor."""
    buf = bytearray(512)
    _smf30_header(buf, 5)
    sof, iof, tof, cof = 128, 192, 392, 408
    _smf30_triplet(buf, 24, sof, 40)
    _smf30_triplet(buf, 32, iof, 200)
    _smf30_triplet(buf, 48, tof, 8)  # completion
    _smf30_triplet(buf, 56, cof, 96)
    _smf30_subsystem(buf, sof)
    _smf30_identification(buf, iof, job="TERMJOB1")
    buf[tof : tof + 2] = _u16(0)  # SCC normal
    buf[tof + 2 : tof + 4] = _u16(0)  # STI
    buf[tof + 4 : tof + 8] = _u32(0)  # ARC
    buf[cof + 4 : cof + 8] = _u32(2500)
    buf[cof + 8 : cof + 12] = _u32(100)
    buf[0:2] = _u16(512)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def build_smf14() -> bytes:
    """Type-14 INPUT data set activity (header + TIOT + JFCB + DCB/DEB + one UCB)."""
    # Contiguous layout (IBM offsets include RDW):
    #   TIOT @52, JFCB @68 (176 bytes → through 243), DCB/DEB @244 size 28,
    #   first UCB @272 size 24 (DASD extension with EXCP + tracks).
    sdc, suc = 28, 24
    ucb = 244 + sdc
    total = ucb + suc
    buf = bytearray(total)

    buf[4] = 0x00
    buf[5] = 14
    buf[6:10] = _smf_time(9, 15, 30)
    buf[10:14] = _smf_date(2026, 3, 25)
    buf[14:18] = _ebcdic("PROD", 4)
    buf[18:26] = _ebcdic("PAYROLL", 8)
    buf[26:30] = _smf_time(8, 0, 0)
    buf[30:34] = _smf_date(2026, 3, 25)
    buf[34:42] = _ebcdic("IBMUSER", 8)
    buf[42] = 0x20  # SMF14DAD — DASD
    buf[43] = 0x00
    buf[44] = sdc
    buf[45] = 1  # one UCB
    buf[46] = suc
    buf[47] = 0
    buf[48:52] = _smf_time(9, 10, 0)

    # TIOT DDNAME @56
    buf[52] = 16
    buf[56:64] = _ebcdic("INFILE", 8)

    # JFCB @68
    buf[68:112] = _ebcdic("SYS1.PAYROLL.MASTER", 44)
    buf[112:120] = _ebcdic(" ", 8)
    buf[166] = 0x40  # PS
    buf[168] = 0x90  # FB
    buf[170:172] = _u16(27998)
    buf[172:174] = _u16(80)
    buf[185] = 1
    buf[186:192] = _ebcdic("SCR001", 6)

    # DCB/DEB @244 — open date in DASD extension @268
    buf[244:246] = b"\x40\x00"  # PS
    buf[246] = 0x90
    buf[268:272] = _smf_date(2026, 3, 25)

    # UCB @272
    buf[ucb : ucb + 2] = _u16(0x1234)
    buf[ucb + 2 : ucb + 8] = _ebcdic("SCR001", 6)
    buf[ucb + 8 : ucb + 12] = bytes((0x30, 0x20, 0x0F, 0x01))  # sample UCBTYP
    buf[ucb + 13] = 1
    buf[ucb + 16 : ucb + 20] = _u32(4200)
    buf[ucb + 20 : ucb + 24] = _u32(150)

    buf[0:2] = _u16(total)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def build_smf80() -> bytes:
    """Type-80 RACF resource-access sample (z/OS 3.1; PACSYS fixed + relocates).

    ``SMF80REL`` / ``SMF80RL2`` are offsets from ``SMF80FLG`` (absolute =
    value + 4 with RDW). Event 2 / qualifier 0 = successful resource access.
    Includes classic tags 1/3/4/15/17 and extended MFA tag 441.
    """
    # Fixed section ends at 98; classic relocate then extended.
    abs_rel = 98
    smf80rel = abs_rel - 4

    entries: list[tuple[int, bytes]] = [
        (1, _ebcdic("IBMUSER.REXX", 12)),
        (3, bytes((0x02,))),  # UPDATE requested
        (4, bytes((0x08,))),  # ALTER allowed
        (15, _ebcdic("SYS001", 6)),
        (17, _ebcdic("DATASET", 8)),
    ]
    reloc_len = sum(2 + len(payload) for _tag, payload in entries)

    # Extended-length: TP2=441 (MFA factor name)
    ext_entries: list[tuple[int, bytes]] = [
        (441, _ebcdic("AZFTOTP1", 8)),
    ]
    ext_len = sum(4 + len(payload) for _tag, payload in ext_entries)
    abs_ext = abs_rel + reloc_len
    smf80rl2 = abs_ext - 4

    body = bytearray(abs_ext + ext_len)

    body[4] = 0x00
    body[5] = 80
    body[6:10] = _smf_time(12, 20, 29)
    body[10:14] = _smf_date(2026, 3, 25)
    body[14:18] = _ebcdic("PROD", 4)
    body[18:20] = _u16(0x0010)  # SMF80DES: VRM present (bit 4)
    body[20] = 2  # SMF80EVT — resource access
    body[21] = 0  # SMF80EVQ — successful access
    body[22:30] = _ebcdic("IBMUSER", 8)
    body[30:38] = _ebcdic("SYS1", 8)
    body[38:40] = _u16(smf80rel)
    body[40:42] = _u16(len(entries))
    body[42] = 0x80  # SMF80ATH — normal authority check
    body[43] = 0x10  # SMF80REA — resource AUDIT
    body[44] = 0
    body[45] = 0
    body[46:54] = _ebcdic("TSO001", 8)
    body[54:62] = _ebcdic("IBMUSER", 8)
    body[62:66] = _smf_time(8, 0, 0)
    body[66:70] = _smf_date(2026, 3, 25)
    body[70:78] = _ebcdic("IBMUSER", 8)
    body[78] = 8
    body[79] = 0
    body[80:84] = _ebcdic("77E0", 4)  # z/OS 3.1 RACF FMID
    body[84:92] = _ebcdic("SYSLOW", 8)
    body[92:94] = _u16(smf80rl2)
    body[94:96] = _u16(len(ext_entries))
    body[96] = 0
    body[97] = 0

    p = abs_rel
    for tag, payload in entries:
        body[p] = tag
        body[p + 1] = len(payload)
        body[p + 2 : p + 2 + len(payload)] = payload
        p += 2 + len(payload)

    p = abs_ext
    for tag, payload in ext_entries:
        body[p : p + 2] = _u16(tag)
        body[p + 2 : p + 4] = _u16(len(payload))
        body[p + 4 : p + 4 + len(payload)] = payload
        p += 4 + len(payload)

    total = len(body)
    body[0:2] = _u16(total)
    body[2:4] = b"\x00\x00"
    return bytes(body)


def build_smf80_jobinit() -> bytes:
    """Type-80 EVT 1 (job initiation / TSO logon) with application relocate tag 20."""
    abs_rel = 98
    smf80rel = abs_rel - 4
    entries: list[tuple[int, bytes]] = [
        (20, _ebcdic("TSO", 3)),
    ]
    reloc_len = sum(2 + len(payload) for _tag, payload in entries)
    body = bytearray(abs_rel + reloc_len)

    body[4] = 0x00
    body[5] = 80
    body[6:10] = _smf_time(11, 47, 18)
    body[10:14] = _smf_date(2026, 3, 25)
    body[14:18] = _ebcdic("PROD", 4)
    body[18:20] = _u16(0x0010)
    body[20] = 1  # job initiation / TSO
    body[21] = 0  # successful RACINIT
    body[22:30] = _ebcdic("WITADM4", 8)
    body[30:38] = _ebcdic("WITADMGP", 8)
    body[38:40] = _u16(smf80rel)
    body[40:42] = _u16(len(entries))
    body[42] = 0x80
    body[54:62] = _ebcdic("XH4AMGS", 8)
    body[80:84] = _ebcdic("77E0", 4)

    p = abs_rel
    for tag, payload in entries:
        body[p] = tag
        body[p + 1] = len(payload)
        body[p + 2 : p + 2 + len(payload)] = payload
        p += 2 + len(payload)

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


def build_smf119_st04() -> bytes:
    """Type 119 subtype 4 — TCP/IP profile (Ident + PICommon + TCPCFG).

    Partial NMTP sample: fixed triplets for PICommon (1) and TCPCFG (6);
    intermediate profile sections are absent (Num=0).
    """
    # Eyecatchers as EBCDIC four-char ids (big-endian u32)
    eye_pico = 0xD7C9C3D6  # PICO
    eye_tccf = 0xE3C3C3C6  # TCCF
    ntrip = 7  # Ident + PICommon..TCPCFG (triplet indices 0..6)
    ident = 88
    pico = 152
    pico_len = 136
    tccf = pico + pico_len
    tccf_len = 56
    total = tccf + tccf_len
    buf = bytearray(total)
    _smf119_header(buf, 4, ntrip, ident)
    # triplet 1 — PICommon
    buf[36:40] = _u32(pico)
    buf[40:42] = _u16(pico_len)
    buf[42:44] = _u16(1)
    # triplets 2–5 left Num=0
    # triplet 6 — TCPCFG
    buf[76:80] = _u32(tccf)
    buf[80:82] = _u16(tccf_len)
    buf[82:84] = _u16(1)
    _fill_ident(buf, ident, "STACK")

    buf[pico : pico + 4] = _u32(eye_pico)
    buf[pico + 12 : pico + 16] = _smf_date(2026, 1, 15)
    buf[pico + 24 : pico + 28] = _smf_date(2026, 3, 25)
    buf[pico + 28] = 1  # OBEYFILE
    buf[pico + 29] = 0x80  # PROFCOMPLETE
    buf[pico + 40 : pico + 48] = _ebcdic("CONS01", 8)
    buf[pico + 48 : pico + 56] = _ebcdic("PLEXGRP", 8)

    buf[tccf : tccf + 4] = _u32(eye_tccf)
    buf[tccf + 4 : tccf + 6] = _u16(0x8000)  # DELAYACKS
    buf[tccf + 12 : tccf + 16] = _u32(1024)  # SOMAXCONN
    buf[tccf + 20 : tccf + 24] = _u32(65535)
    buf[tccf + 24 : tccf + 28] = _u32(65535)
    buf[tccf + 28 : tccf + 30] = _u16(1024)
    buf[tccf + 30 : tccf + 32] = _u16(65535)

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


def _build_icf(
    rty: int,
    *,
    action: str,
    fnc: bytes,
    job: str,
    catalog: str,
    entry_type: str,
    entry_name: str,
    new_name: str = "",
    hh: int = 11,
    mm: int = 30,
    ss: int = 0,
) -> bytes:
    """Types 61/65/66 — ICF catalog activity (product @40, minimal CRC @208)."""
    pof, pln, dof = 40, 168, 208
    # Minimal catalog record: 2-byte length + empty body
    crc = _u16(2)
    total = dof + len(crc)
    buf = bytearray(total)
    buf[4] = 0x00
    buf[5] = rty
    buf[6:10] = _smf_time(hh, mm, ss)
    buf[10:14] = _smf_date(2026, 3, 25)
    buf[14:18] = _ebcdic("PROD", 4)
    buf[18:22] = b"\x00\x00\x00\x00"  # reserved SBS
    buf[22:24] = _ebcdic(action, 2)
    buf[24:28] = _u32(pof)
    buf[28:30] = _u16(pln)
    buf[30:32] = _u16(1)
    buf[32:36] = _u32(dof)
    buf[36:38] = _u16(len(crc))
    buf[38:40] = _u16(1)
    # Product section
    buf[40:42] = _ebcdic("01", 2)
    buf[42:50] = _ebcdic("IGG0CLX0", 8)
    buf[50:58] = _ebcdic(job, 8)
    buf[58:62] = _smf_time(8, 0, 0)
    buf[62:66] = _smf_date(2026, 3, 25)
    buf[66:74] = _ebcdic("IBMUSER", 8)
    buf[74:75] = fnc
    buf[75:119] = _ebcdic(catalog, 44)
    buf[119:120] = _ebcdic(entry_type, 1)
    buf[120:164] = _ebcdic(entry_name, 44)
    buf[164:208] = _ebcdic(new_name, 44)
    buf[dof : dof + len(crc)] = crc
    buf[0:2] = _u16(total)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def _smf42_header(buf: bytearray, subtype: int, ntrip: int) -> None:
    buf[4] = 0x1E  # subsystem id + subtypes
    buf[5] = 42
    buf[6:10] = _smf_time(16, 20, 0)
    buf[10:14] = _smf_date(2026, 3, 25)
    buf[14:18] = _ebcdic("PROD", 4)
    buf[18:22] = _ebcdic("SMS", 4)
    buf[22:24] = _u16(subtype)
    buf[24:26] = _u16(ntrip)


def _smf42_product(buf: bytearray, offs: int) -> None:
    buf[offs + 0 : offs + 8] = _ebcdic("ZOS2.5.0", 8)
    buf[offs + 8 : offs + 18] = _ebcdic("DFSMS", 10)
    buf[offs + 18] = 1  # SMF42PSV


def _smf42_triplet(buf: bytearray, trip: int, offs: int, length: int, number: int = 1) -> None:
    buf[trip : trip + 4] = _u32(offs)
    buf[trip + 4 : trip + 6] = _u16(length)
    buf[trip + 6 : trip + 8] = _u16(number)


def build_smf42_st20() -> bytes:
    """Type 42 subtype 20 — STOW Initialize (product + job/DSN + user token)."""
    ntrip, prod_len, kn1_len, kn4_len = 3, 40, 74, 80
    hdr_end = 28 + 8 * ntrip  # 52
    prod, kn1 = hdr_end, hdr_end + prod_len
    kn4 = kn1 + kn1_len
    total = kn4 + kn4_len
    buf = bytearray(total)
    _smf42_header(buf, 20, ntrip)
    _smf42_triplet(buf, 28, prod, prod_len)
    _smf42_triplet(buf, 36, kn1, kn1_len)
    _smf42_triplet(buf, 44, kn4, kn4_len)
    _smf42_product(buf, prod)
    buf[kn1 + 0 : kn1 + 8] = _ebcdic("STOWJOB1", 8)
    buf[kn1 + 8 : kn1 + 16] = _ebcdic("STEP1", 8)
    buf[kn1 + 16 : kn1 + 24] = _ebcdic(" ", 8)
    buf[kn1 + 24 : kn1 + 68] = _ebcdic("SYS1.PROCLIB", 44)
    buf[kn1 + 68 : kn1 + 74] = _ebcdic("SYSRES", 6)
    buf[kn4 : kn4 + 16] = bytes(range(16))
    buf[0:2] = _u16(total)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def build_smf42_st21() -> bytes:
    """Type 42 subtype 21 — Member Delete (product + job/DSN/member + alias + user)."""
    member = _ebcdic("MEMBER1", 7)
    ntrip, prod_len = 4, 40
    kn1_len = 80 + len(member)
    alias_len, user_len = 2, 80
    hdr_end = 28 + 8 * ntrip  # 60
    prod = hdr_end
    ln1 = prod + prod_len
    ln4 = ln1 + kn1_len
    ln7 = ln4 + alias_len
    total = ln7 + user_len
    buf = bytearray(total)
    _smf42_header(buf, 21, ntrip)
    _smf42_triplet(buf, 28, prod, prod_len)
    _smf42_triplet(buf, 36, ln1, kn1_len)
    _smf42_triplet(buf, 44, ln4, alias_len)
    _smf42_triplet(buf, 52, ln7, user_len)
    _smf42_product(buf, prod)
    buf[ln1 + 0 : ln1 + 8] = _ebcdic("DELJOB01", 8)
    buf[ln1 + 8 : ln1 + 16] = _ebcdic("STEP1", 8)
    buf[ln1 + 16 : ln1 + 24] = _ebcdic(" ", 8)
    buf[ln1 + 24 : ln1 + 68] = _ebcdic("IBMUSER.SOURCE.PDS", 44)
    buf[ln1 + 68 : ln1 + 74] = _ebcdic("TSO001", 6)
    buf[ln1 + 74 : ln1 + 76] = _u16(len(member))
    buf[ln1 + 76 : ln1 + 80] = b"\x00\x00\x00\x00"
    buf[ln1 + 80 : ln1 + 80 + len(member)] = member
    buf[ln4 : ln4 + 2] = _u16(0)
    buf[ln7 : ln7 + 16] = bytes(range(16, 32))
    buf[0:2] = _u16(total)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def build_smf42_st24() -> bytes:
    """Type 42 subtype 24 — Member add/replace (product + job/DSN/member + alias + user)."""
    member = _ebcdic("NEWMEM", 6)
    ntrip, prod_len = 4, 40
    pn1_len = 80 + len(member)
    alias_len, user_len = 2, 80
    hdr_end = 28 + 8 * ntrip
    prod = hdr_end
    pn1 = prod + prod_len
    pn4 = pn1 + pn1_len
    pn7 = pn4 + alias_len
    total = pn7 + user_len
    buf = bytearray(total)
    _smf42_header(buf, 24, ntrip)
    _smf42_triplet(buf, 28, prod, prod_len)
    _smf42_triplet(buf, 36, pn1, pn1_len)
    _smf42_triplet(buf, 44, pn4, alias_len)
    _smf42_triplet(buf, 52, pn7, user_len)
    _smf42_product(buf, prod)
    buf[pn1 + 0 : pn1 + 8] = _ebcdic("ADDJOB01", 8)
    buf[pn1 + 8 : pn1 + 16] = _ebcdic("STEP1", 8)
    buf[pn1 + 16 : pn1 + 24] = _ebcdic(" ", 8)
    buf[pn1 + 24 : pn1 + 68] = _ebcdic("IBMUSER.SOURCE.PDSE", 44)
    buf[pn1 + 68 : pn1 + 74] = _ebcdic("WORK01", 6)
    buf[pn1 + 74 : pn1 + 76] = _u16(len(member))
    buf[pn1 + 76] = 0x40  # new member bit
    buf[pn1 + 80 : pn1 + 80 + len(member)] = member
    buf[pn4 : pn4 + 2] = _u16(0)
    buf[pn7 : pn7 + 16] = bytes(range(32, 48))
    buf[0:2] = _u16(total)
    buf[2:4] = b"\x00\x00"
    return bytes(buf)


def build_smf61() -> bytes:
    """Type 61 — ICF DEFINE (insert non-VSAM)."""
    return _build_icf(
        61,
        action="IN",
        fnc=b"\x00",
        job="DEFJOB01",
        catalog="CATALOG.USER.ICF",
        entry_type="A",
        entry_name="IBMUSER.NEW.DATASET",
        hh=11,
        mm=31,
        ss=13,
    )


def build_smf65() -> bytes:
    """Type 65 — ICF DELETE (scratch)."""
    return _build_icf(
        65,
        action="DE",
        fnc=_ebcdic("S", 1),
        job="DELJOB01",
        catalog="CATALOG.USER.ICF",
        entry_type="A",
        entry_name="IBMUSER.OLD.DATASET",
        hh=11,
        mm=41,
        ss=7,
    )


def build_smf66() -> bytes:
    """Type 66 — ICF ALTER (rename)."""
    return _build_icf(
        66,
        action="UP",
        fnc=_ebcdic("R", 1),
        job="ALTJOB01",
        catalog="CATALOG.USER.ICF",
        entry_type="A",
        entry_name="IBMUSER.OLD.NAME",
        new_name="IBMUSER.NEW.NAME",
        hh=11,
        mm=45,
        ss=0,
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate sample SMF VB dump")
    ap.add_argument("-o", "--output", default="python/samples/sample.smf")
    args = ap.parse_args()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = (
        build_smf14()
        + build_smf15()
        + build_smf17()
        + build_smf30_st01()
        + build_smf30()
        + build_smf30_st05()
        + build_smf42_st20()
        + build_smf42_st21()
        + build_smf42_st24()
        + build_smf61()
        + build_smf65()
        + build_smf66()
        + build_smf80()
        + build_smf80_jobinit()
        + build_smf119_st01()
        + build_smf119_st02()
        + build_smf119_st03()
        + build_smf119_st04()
        + build_smf119_st10()
    )
    path.write_bytes(blob)
    print(f"Wrote {path} ({len(blob)} bytes)")


if __name__ == "__main__":
    main()
