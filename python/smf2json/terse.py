"""AMATERSE / TRSMAIN TERSE unpacker (PACK + SPACK), stdlib only.

Binary host files (typical SMF) are written with RDW on RECFM=V/VB/VBS.
Text mode (optional) applies the IBM EBC→ASCII table used by TerseDecompress.

Algorithm port of Open Mainframe Project TerseDecompress (Apache-2.0).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Callable, List, Optional

from .progress import PROGRESS_EVERY_BYTES, CliProgress, fmt_bytes

TREESIZE = 0x1000
RECORDMARK = 257
BASE = 0
CODESIZE = 257
NONE = -1
STACKSIZE = 0x07FF

ProgressFn = Callable[[int, int, int], None]  # input_pos, input_total, bytes_written


def _progressive_tick(
    progress: Optional[ProgressFn],
    reader: "_BitReader",
    writer: "_Writer",
    total: int,
    last_pos: list[int],
    *,
    force: bool = False,
) -> None:
    if not progress:
        return
    pos = reader.pos
    if not force and pos - last_pos[0] < PROGRESS_EVERY_BYTES:
        return
    last_pos[0] = pos
    progress(pos, total, writer.bytes_written)


# IBM TerseDecompress host text mapping (not cp037).
EBC_TO_ASC = (
    0x00, 0x01, 0x02, 0x03, 0xCF, 0x09, 0xD3, 0x7F, 0xD4, 0xD5, 0xC3, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
    0x10, 0x11, 0x12, 0x13, 0xC7, 0xB4, 0x08, 0xC9, 0x18, 0x19, 0xCC, 0xCD, 0x83, 0x1D, 0xD2, 0x1F,
    0x81, 0x82, 0x1C, 0x84, 0x86, 0x0A, 0x17, 0x1B, 0x89, 0x91, 0x92, 0x95, 0xA2, 0x05, 0x06, 0x07,
    0xE0, 0xEE, 0x16, 0xE5, 0xD0, 0x1E, 0xEA, 0x04, 0x8A, 0xF6, 0xC6, 0xC2, 0x14, 0x15, 0xC1, 0x1A,
    0x20, 0xA6, 0xE1, 0x80, 0xEB, 0x90, 0x9F, 0xE2, 0xAB, 0x8B, 0x9B, 0x2E, 0x3C, 0x28, 0x2B, 0x7C,
    0x26, 0xA9, 0xAA, 0x9C, 0xDB, 0xA5, 0x99, 0xE3, 0xA8, 0x9E, 0x21, 0x24, 0x2A, 0x29, 0x3B, 0x5E,
    0x2D, 0x2F, 0xDF, 0xDC, 0x9A, 0xDD, 0xDE, 0x98, 0x9D, 0xAC, 0xBA, 0x2C, 0x25, 0x5F, 0x3E, 0x3F,
    0xD7, 0x88, 0x94, 0xB0, 0xB1, 0xB2, 0xFC, 0xD6, 0xFB, 0x60, 0x3A, 0x23, 0x40, 0x27, 0x3D, 0x22,
    0xF8, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x96, 0xA4, 0xF3, 0xAF, 0xAE, 0xC5,
    0x8C, 0x6A, 0x6B, 0x6C, 0x6D, 0x6E, 0x6F, 0x70, 0x71, 0x72, 0x97, 0x87, 0xCE, 0x93, 0xF1, 0xFE,
    0xC8, 0x7E, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7A, 0xEF, 0xC0, 0xDA, 0x5B, 0xF2, 0xF9,
    0xB5, 0xB6, 0xFD, 0xB7, 0xB8, 0xB9, 0xE6, 0xBB, 0xBC, 0xBD, 0x8D, 0xD9, 0xBF, 0x5D, 0xD8, 0xC4,
    0x7B, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0xCB, 0xCA, 0xBE, 0xE8, 0xEC, 0xED,
    0x7D, 0x4A, 0x4B, 0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x51, 0x52, 0xA1, 0xAD, 0xF5, 0xF4, 0xA3, 0x8F,
    0x5C, 0xE7, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5A, 0xA0, 0x85, 0x8E, 0xE9, 0xE4, 0xD1,
    0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0xB3, 0xF7, 0xF0, 0xFA, 0xA7, 0xFF,
)


class TerseError(ValueError):
    """Invalid TERSE header or corrupt payload."""


@dataclass(frozen=True)
class TerseHeader:
    version_flag: int
    spack: bool
    host: bool
    recfm_v: bool
    record_length: int
    flags: int = 0
    ratio: int = 0
    block_size: int = 0

    @property
    def method(self) -> str:
        if self.version_flag in (0x01, 0x07):
            return "NATIVE"
        return "SPACK" if self.spack else "PACK"


def default_output_path(src: Path) -> Path:
    return src.with_name(src.name + ".raw.dump")


def parse_header(buf: bytes, pos: int = 0) -> tuple[TerseHeader, int]:
    if pos >= len(buf):
        raise TerseError("empty TERSE file")
    version = buf[pos]
    pos += 1
    if version in (0x01, 0x07):
        if pos + 5 > len(buf):
            raise TerseError("truncated native TERSE header")
        if buf[pos : pos + 3] != b"\x89\x69\xa5":
            raise TerseError("invalid native TERSE magic")
        rec_len = int.from_bytes(buf[pos + 3 : pos + 5], "big")
        return TerseHeader(version, False, False, False, rec_len), pos + 5
    if version in (0x02, 0x05):
        if pos + 11 > len(buf):
            raise TerseError("truncated host TERSE header")
        variable = buf[pos]
        rec1 = int.from_bytes(buf[pos + 1 : pos + 3], "big")
        flags = buf[pos + 3]
        ratio = buf[pos + 4]
        blk = int.from_bytes(buf[pos + 5 : pos + 7], "big")
        rec2 = int.from_bytes(buf[pos + 7 : pos + 11], "big")
        pos += 11
        if variable not in (0x00, 0x01):
            raise TerseError(f"record format flag not recognized: {variable}")
        if rec1 == 0 and rec2 == 0:
            raise TerseError("record length is 0")
        if rec1 and rec2 and rec1 != rec2:
            raise TerseError("ambiguous record length")
        if flags & 0x04 == 0 and (flags or ratio or blk):
            raise TerseError("non-MVS header extras must be 0")
        rec_len = rec1 or rec2
        return (
            TerseHeader(version, version == 0x05, True, variable == 0x01, rec_len, flags, ratio, blk),
            pos,
        )
    raise TerseError(f"TERSE header version not recognized: 0x{version:02X}")


class _BitReader:
    def __init__(self, data: bytes, pos: int):
        self.data = data
        self.pos = pos
        self.saved = 0
        self.have = 0

    def get_block(self) -> int:
        if self.have == 0:
            if self.pos + 2 > len(self.data):
                if self.pos < len(self.data):
                    raise TerseError("truncated 12-bit TERSE code")
                return 0
            b1 = self.data[self.pos]
            b2 = self.data[self.pos + 1]
            self.pos += 2
            self.saved = b2 & 0x0F
            self.have = 4
            return (b1 << 4) | (b2 >> 4)
        if self.pos >= len(self.data):
            return 0
        b2 = self.data[self.pos]
        self.pos += 1
        result = (self.saved << 8) | b2
        self.have = 0
        self.saved = 0
        return result


class _Writer:
    def __init__(self, out: BinaryIO, header: TerseHeader, text: bool):
        self.out = out
        self.header = header
        self.text = text
        self.record = bytearray()
        self.bytes_written = 0

    def put_char(self, x: int) -> None:
        host = self.header.host
        variable = self.header.recfm_v
        if x == 0:
            if host and self.text and variable:
                self.end_record()
            return
        if host and self.text:
            if variable:
                if x == RECORDMARK:
                    self.end_record()
                else:
                    self.record.append(EBC_TO_ASC[x - 1])
            else:
                self.record.append(EBC_TO_ASC[x - 1])
                if len(self.record) == self.header.record_length:
                    self.end_record()
            return
        if x == RECORDMARK:
            if variable:
                self.end_record()
            return
        self.record.append((x - 1) & 0xFF)
        if not variable and len(self.record) == self.header.record_length:
            self.end_record()

    def end_record(self) -> None:
        if self.header.recfm_v and not self.text:
            total = len(self.record) + 4
            self.out.write(total.to_bytes(2, "big") + b"\x00\x00")
            self.bytes_written += 4
        if self.record:
            self.out.write(self.record)
            self.bytes_written += len(self.record)
            self.record.clear()
        if self.text:
            self.out.write(b"\n")
            self.bytes_written += 1

    def close(self) -> None:
        if self.record or (self.text and self.header.recfm_v):
            self.end_record()
        self.out.flush()


def _decode_pack(
    reader: _BitReader,
    writer: _Writer,
    *,
    progress: Optional[ProgressFn] = None,
    total: int = 0,
) -> None:
    father = [0] * TREESIZE
    char_ext = [0] * TREESIZE
    backward = [0] * TREESIZE
    forward = [0] * TREESIZE
    h2 = 65
    for h1 in range(258, TREESIZE):
        father[h1] = h2
        char_ext[h1] = 65
        h2 = h1
    for h1 in range(258, TREESIZE - 1):
        backward[h1 + 1] = h1
        forward[h1] = h1 + 1
    backward[0] = TREESIZE - 1
    forward[0] = 258
    backward[258] = 0
    forward[TREESIZE - 1] = 0
    x = 0
    last = [-PROGRESS_EVERY_BYTES]
    d = reader.get_block()
    while d != 0:
        y = backward[0]
        q = backward[y]
        backward[0] = q
        forward[q] = 0
        h = y
        p = 0
        while d > 257:
            q = forward[d]
            r = backward[d]
            forward[r] = q
            backward[q] = r
            forward[d] = h
            backward[h] = d
            h = d
            e = father[d]
            father[d] = p
            p = d
            d = e
        q = forward[0]
        forward[y] = q
        backward[q] = y
        forward[0] = h
        backward[h] = 0
        char_ext[x] = d
        writer.put_char(d)
        x = y
        while p != 0:
            e = father[p]
            writer.put_char(char_ext[p])
            father[p] = d
            d = p
            p = e
        father[y] = d
        d = reader.get_block()
        _progressive_tick(progress, reader, writer, total, last)
    writer.close()
    _progressive_tick(progress, reader, writer, total, last, force=True)


class _TreeRec:
    __slots__ = ("left", "right", "back", "next_count")

    def __init__(self) -> None:
        self.left = 0
        self.right = 0
        self.back = 0
        self.next_count = 0


def _decode_spack(
    reader: _BitReader,
    writer: _Writer,
    *,
    progress: Optional[ProgressFn] = None,
    total: int = 0,
) -> None:
    tree: List[_TreeRec] = [_TreeRec() for _ in range(TREESIZE + 1)]
    stack = [0] * (STACKSIZE + 1)

    def tree_init() -> int:
        for rec in tree:
            rec.left = NONE
            rec.right = NONE
            rec.back = 0
            rec.next_count = 0
        for i in range(BASE, CODESIZE + 1):
            tree[i].left = NONE
            tree[i].right = i
        for i in range(CODESIZE + 1, TREESIZE):
            tree[i].next_count = i + 1
            tree[i].left = NONE
            tree[i].right = NONE
        tree[TREESIZE].next_count = NONE
        tree[BASE].next_count = BASE
        tree[BASE].back = BASE
        for i in range(1, CODESIZE + 1):
            tree[i].next_count = NONE
        return CODESIZE + 1

    def lru_add(lru_next: int) -> None:
        lru_back = tree[BASE].back
        tree[lru_next].next_count = BASE
        tree[BASE].back = lru_next
        tree[lru_next].back = lru_back
        tree[lru_back].next_count = lru_next

    def delete_ref(dref: int) -> None:
        if dref == NONE:
            return
        if dref < 0 or dref >= len(tree):
            raise TerseError("SPACK: invalid ref in deleteRef")
        if tree[dref].next_count == -1:
            lru_add(dref)
        else:
            tree[dref].next_count += 1

    def bump_ref(bref: int) -> None:
        if tree[bref].next_count < 0:
            tree[bref].next_count -= 1
            return
        forwards = tree[bref].next_count
        prev = tree[bref].back
        tree[prev].next_count = forwards
        tree[forwards].back = prev
        tree[bref].next_count = -1

    def lru_kill() -> None:
        nonlocal tree_avail
        lru_p = tree[0].next_count
        lru_q = tree[lru_p].next_count
        lru_r = tree[lru_p].back
        tree[lru_q].back = lru_r
        tree[lru_r].next_count = lru_q
        delete_ref(tree[lru_p].left)
        delete_ref(tree[lru_p].right)
        tree[lru_p].next_count = tree_avail
        tree_avail = lru_p

    def put_chars(x: int) -> None:
        head = 0
        while True:
            while x > CODESIZE:
                head += 1
                stack[head] = tree[x].right
                x = tree[x].left
            if x < 0:
                raise TerseError("SPACK decode error: negative code")
            writer.put_char(x)
            if head > 0:
                x = stack[head]
                head -= 1
            else:
                break

    tree_avail = tree_init()
    tree[TREESIZE - 1].next_count = NONE
    last = [-PROGRESS_EVERY_BYTES]
    h = reader.get_block()
    if h == 0:
        writer.close()
        _progressive_tick(progress, reader, writer, total, last, force=True)
        return
    put_chars(h)
    g = reader.get_block()
    while g != 0:
        if tree_avail == NONE:
            lru_kill()
        put_chars(g)
        n = tree_avail
        tree_avail = tree[n].next_count
        tree[n].left = h
        tree[n].right = g
        bump_ref(h)
        bump_ref(g)
        lru_add(n)
        h = g
        g = reader.get_block()
        _progressive_tick(progress, reader, writer, total, last)
    writer.close()
    _progressive_tick(progress, reader, writer, total, last, force=True)


def decompress_stream(
    data: bytes,
    out: BinaryIO,
    *,
    text: bool = False,
    progress: Optional[ProgressFn] = None,
) -> TerseHeader:
    header, pos = parse_header(data)
    reader = _BitReader(data, pos)
    writer = _Writer(out, header, text)
    total = len(data)
    if progress:
        progress(pos, total, 0)
    if header.spack:
        _decode_spack(reader, writer, progress=progress, total=total)
    else:
        _decode_pack(reader, writer, progress=progress, total=total)
    return header


def decompress(data: bytes, *, text: bool = False) -> bytes:
    from io import BytesIO

    buf = BytesIO()
    decompress_stream(data, buf, text=text)
    return buf.getvalue()


def decompress_file(
    src: Path | str,
    dest: Path | str,
    *,
    text: bool = False,
    progress: Optional[ProgressFn] = None,
) -> TerseHeader:
    source = Path(src)
    target = Path(dest)
    payload = source.read_bytes()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as fh:
        return decompress_stream(payload, fh, text=text, progress=progress)


def pack_12bit_codes(codes: List[int]) -> bytes:
    """Test helper: pack 12-bit TERSE codes the way the reader consumes them."""
    bits = 0
    nbits = 0
    out = bytearray()
    for code in codes:
        bits = (bits << 12) | (code & 0xFFF)
        nbits += 12
        while nbits >= 8:
            nbits -= 8
            out.append((bits >> nbits) & 0xFF)
            bits &= (1 << nbits) - 1
    if nbits:
        out.append((bits << (8 - nbits)) & 0xFF)
    return bytes(out)


def build_host_header(*, spack: bool, recfm_v: bool, record_length: int) -> bytes:
    version = 0x05 if spack else 0x02
    rec1 = record_length.to_bytes(2, "big")
    return bytes((version, 0x01 if recfm_v else 0x00)) + rec1 + bytes(8)


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="unterse",
        description="Decompress an AMATERSE / TRSMAIN TERSE file (PACK or SPACK).",
    )
    p.add_argument("input", help="Tersed file (.trs / AMATERSE PACK)")
    p.add_argument(
        "-o",
        "--output",
        help="Output path (default: input name + .raw.dump beside the source)",
    )
    p.add_argument(
        "--text",
        action="store_true",
        help="Host text mode (EBCDIC→ASCII + newlines). Default is binary with RDW for VB.",
    )
    p.add_argument(
        "--no-progress",
        action="store_true",
        help="Do not draw the stderr progress bar",
    )
    args = p.parse_args(argv)
    src = Path(args.input)
    if not src.is_file():
        print(f"ERROR: file not found: {src}", file=sys.stderr)
        return 2
    dest = Path(args.output) if args.output else default_output_path(src)
    src_size = src.stat().st_size
    show_bar = not args.no_progress
    bar = CliProgress(enabled=show_bar, label=src.name)

    print(f"INFO: reading {src.name} ({fmt_bytes(src_size)})...", file=sys.stderr)
    try:
        payload = src.read_bytes()
    except OSError as exc:
        print(f"ERROR: read failed: {exc}", file=sys.stderr)
        return 1

    try:
        header, _pos = parse_header(payload)
    except TerseError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    recfm = "VB" if header.recfm_v else "FB"
    print(
        f"INFO: decompressing {header.method} recfm={recfm} lrecl={header.record_length}...",
        file=sys.stderr,
    )
    bar.stage = header.method

    def on_progress(pos: int, total: int, written: int) -> None:
        bar.update_bytes(pos, total, written=written, stage=header.method)

    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as fh:
            decompress_stream(payload, fh, text=args.text, progress=on_progress)
    except TerseError as exc:
        bar.close()
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        bar.close()
        print(f"ERROR: write failed: {exc}", file=sys.stderr)
        return 1

    bar.close()
    size = dest.stat().st_size
    print(
        f"Wrote {dest} ({size:,} bytes)  method={header.method} recfm={recfm} "
        f"lrecl={header.record_length}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
