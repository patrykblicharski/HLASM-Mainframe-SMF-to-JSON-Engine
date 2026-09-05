"""Tests for the AMATERSE/TERSE unpacker."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from smf2json.terse import (
    TerseError,
    build_host_header,
    default_output_path,
    decompress,
    decompress_file,
    pack_12bit_codes,
    parse_header,
)


def _vb_pack(payload: bytes, *, spack: bool = False, lrecl: int = 80) -> bytes:
    codes = [b + 1 for b in payload] + [257]
    return build_host_header(spack=spack, recfm_v=True, record_length=lrecl) + pack_12bit_codes(
        codes
    )


class TerseTests(unittest.TestCase):
    def test_default_output_path(self) -> None:
        src = Path(r"C:\tmp\A910826.SMF30.ONEDAY.TRS")
        self.assertEqual(default_output_path(src).name, "A910826.SMF30.ONEDAY.TRS.raw.dump")

    def test_header_pack_vb(self) -> None:
        raw = build_host_header(spack=False, recfm_v=True, record_length=80)
        header, pos = parse_header(raw)
        self.assertEqual(header.method, "PACK")
        self.assertTrue(header.recfm_v)
        self.assertEqual(header.record_length, 80)
        self.assertEqual(pos, 12)

    def test_header_rejects_unknown(self) -> None:
        with self.assertRaises(TerseError):
            parse_header(b"\x81\x00")

    def test_pack_vb_binary_rdw(self) -> None:
        blob = _vb_pack(b"AB")
        out = decompress(blob)
        self.assertEqual(out, b"\x00\x06\x00\x00AB")

    def test_spack_vb_binary_rdw(self) -> None:
        blob = _vb_pack(b"Hi", spack=True)
        out = decompress(blob)
        self.assertEqual(out, b"\x00\x06\x00\x00Hi")

    def test_decompress_file_writes_raw_dump(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "sample.trs"
            src.write_bytes(_vb_pack(b"XY"))
            dest = default_output_path(src)
            header = decompress_file(src, dest)
            self.assertEqual(header.method, "PACK")
            self.assertEqual(dest.read_bytes(), b"\x00\x06\x00\x00XY")
            self.assertTrue(str(dest).endswith(".raw.dump"))


if __name__ == "__main__":
    unittest.main()
