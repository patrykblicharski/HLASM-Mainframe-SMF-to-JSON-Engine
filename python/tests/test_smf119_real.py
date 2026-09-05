"""Integration test: real SMF 119 dump packed as TERSE."""

from __future__ import annotations

import tempfile
import unittest
from collections import Counter
from pathlib import Path

from smf2json.engine import convert_record
from smf2json.reader import iter_dump
from smf2json.terse import decompress_file

SAMPLE_TRS = Path(__file__).resolve().parents[1] / "samples" / "119" / "A910826.SMF119.TRS"


@unittest.skipUnless(SAMPLE_TRS.is_file(), f"missing {SAMPLE_TRS.name}")
class RealSmf119DumpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        dest = Path(cls._tmp.name) / "A910826.SMF119.smf"
        header = decompress_file(SAMPLE_TRS, dest)
        cls.path = dest
        cls.header = header

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_terse_header(self) -> None:
        self.assertEqual(self.header.method, "PACK")
        self.assertTrue(self.header.recfm_v)

    def test_convert_all_records(self) -> None:
        counts: Counter[str] = Counter()
        first: dict[str, dict] = {}
        total = 0
        for rec in iter_dump(str(self.path)):
            self.assertEqual(rec.record_type, 119)
            row = convert_record(rec)
            self.assertIsNotNone(row, f"unmapped record index={rec.index} subtype={rec.subtype}")
            assert row is not None
            sty = row["smf_subtype"]
            counts[sty] += 1
            first.setdefault(sty, row)
            total += 1

        self.assertEqual(total, 8669)
        self.assertEqual(
            dict(counts),
            {"1": 1832, "2": 1827, "3": 20, "5": 384, "6": 384, "10": 4222},
        )

        r1 = first["1"]
        self.assertEqual(r1["smf_system_id"], "I011")
        self.assertEqual(r1["tcp_stack"], "IZTTCPI3")
        self.assertEqual(r1["tcp_component"], "TCP")
        self.assertEqual(r1["resource_name"], "IZPAAPP")
        self.assertEqual(r1["remote_ip"], "161.89.171.10")
        self.assertEqual(r1["local_ip"], "161.89.24.193")
        self.assertEqual(r1["remote_port"], "1358")
        self.assertEqual(r1["local_port"], "1358")

        r2 = first["2"]
        self.assertEqual(r2["resource_name"], "IZPAAPP")
        self.assertEqual(r2["in_bytes"], "66")
        self.assertEqual(r2["out_bytes"], "162")
        self.assertEqual(r2["term_code"], "52")

        r3 = first["3"]
        self.assertEqual(r3["tcp_component"], "FTPC")
        self.assertEqual(r3["ftp_cmd"], "RETR")
        self.assertEqual(r3["file_name"], "AZRP.SMFDE.RMFDAILY.OTEB.TRS.G2554V00")
        self.assertEqual(r3["bytes_transferred"], "39389184")

        r10 = first["10"]
        self.assertEqual(r10["tcp_component"], "UDP")
        self.assertEqual(r10["local_port"], "24570")
        self.assertEqual(r10["out_bytes"], "153")


if __name__ == "__main__":
    unittest.main()
