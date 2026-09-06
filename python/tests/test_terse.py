"""Tests for the AMATERSE/TERSE unpacker."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from smf2json.terse import (
    TerseError,
    build_host_header,
    default_output_path,
    decompress,
    decompress_file,
    decompress_stream,
    main,
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

    def test_decompress_stream_reports_progress(self) -> None:
        blob = _vb_pack(b"ABCDEFGH" * 32)
        ticks: list[tuple[int, int, int]] = []

        def on_progress(pos: int, total: int, written: int) -> None:
            ticks.append((pos, total, written))

        out = io.BytesIO()
        decompress_stream(blob, out, progress=on_progress)
        self.assertGreaterEqual(len(ticks), 2)
        self.assertEqual(ticks[0][1], len(blob))
        self.assertEqual(ticks[-1][0], ticks[-1][1])
        self.assertGreater(ticks[-1][2], 0)

    def test_cli_progress_stages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "sample.trs"
            dest = Path(tmp) / "out.dump"
            src.write_bytes(_vb_pack(b"ZZ"))
            err = io.StringIO()
            with redirect_stderr(err):
                rc = main([str(src), "-o", str(dest)])
            self.assertEqual(rc, 0)
            text = err.getvalue()
            self.assertIn("INFO: reading", text)
            self.assertIn("INFO: decompressing PACK", text)
            self.assertTrue(dest.is_file())


if __name__ == "__main__":
    unittest.main()
