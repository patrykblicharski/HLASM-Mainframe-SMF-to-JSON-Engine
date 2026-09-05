"""Unit tests for SMF reader/engine (stdlib unittest)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from smf2json.engine import convert_dump, ordered_columns
from smf2json.reader import read_dump
from smf2json.sample_dump import build_smf30, build_smf80
from smf2json.types import FieldSpec, convert_value, parse_smf_date, parse_smf_time


class TypeTests(unittest.TestCase):
    def test_time(self) -> None:
        raw = ((12 * 3600 + 13 * 60 + 59) * 100).to_bytes(4, "big")
        self.assertEqual(parse_smf_time(raw), "12:13:59")

    def test_date(self) -> None:
        # 2026-03-25 → julian day 84 → packed 0c yy ddd F
        raw = bytes.fromhex("0126084f")
        self.assertEqual(parse_smf_date(raw), "2026-03-25")

    def test_ebcdic_chr(self) -> None:
        spec = FieldSpec("sid", "SMF30SID", "CHR4", 14)
        raw = "PROD".encode("cp037")
        self.assertEqual(convert_value(spec, raw), "PROD")


class DumpTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "sample.smf"
        self.path.write_bytes(build_smf30() + build_smf80())

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_read_two_records(self) -> None:
        logs: list[str] = []
        recs = read_dump(str(self.path), log=logs.append)
        self.assertEqual(len(recs), 2)
        self.assertEqual(recs[0].record_type, 30)
        self.assertEqual(recs[1].record_type, 80)

    def test_convert_type30(self) -> None:
        rows = convert_dump(read_dump(str(self.path)))
        self.assertEqual(len(rows), 2)
        r30 = rows[0]
        self.assertEqual(r30["smf_record_type"], "30")
        self.assertEqual(r30["smf_system_id"], "PROD")
        self.assertEqual(r30["time"], "12:13:59")
        self.assertEqual(r30["date"], "2026-03-25")
        self.assertEqual(r30["job_name"], "PAYROLL")
        self.assertEqual(r30["program_name"], "IFASMFDP")
        self.assertEqual(r30["product_name"], "SMF")
        self.assertEqual(r30["cpu_step_time"], "1906")
        self.assertEqual(r30["srb_time"], "679")

        r80 = rows[1]
        self.assertEqual(r80["smf_record_type"], "80")
        self.assertEqual(r80["user_id"], "IBMUSER")
        self.assertEqual(r80["class_name"], "DATASET")
        self.assertEqual(r80["old_resource"], "IBMUSER.REXX")

    def test_json_roundtrip(self) -> None:
        rows = convert_dump(read_dump(str(self.path)))
        text = json.dumps(rows)
        self.assertIn("PAYROLL", text)
        cols = ordered_columns(rows)
        self.assertIn("job_name", cols)


if __name__ == "__main__":
    unittest.main()
