"""Tests for progress / timing helpers and CLI convert."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from smf2json.__main__ import main
from smf2json.progress import fmt_elapsed, format_bar, format_byte_bar, format_timing
from smf2json.sample_dump import build_smf30, build_smf80


class ProgressFormatTests(unittest.TestCase):
    def test_fmt_elapsed(self) -> None:
        self.assertEqual(fmt_elapsed(0.012), "12 ms")
        self.assertEqual(fmt_elapsed(2.5), "2.50 s")
        self.assertIn("m", fmt_elapsed(65))

    def test_format_timing(self) -> None:
        text = format_timing(0.02, 1.5)
        self.assertIn("records", text)
        self.assertIn("dump", text)
        self.assertIn("20 ms", text)
        self.assertIn("1.50 s", text)

    def test_format_bar_percent(self) -> None:
        line = format_bar(50, 100, 10, 8, "dump.smf")
        self.assertIn("50.0%", line)
        self.assertIn("8 mapped", line)

    def test_format_byte_bar(self) -> None:
        line = format_byte_bar(512 * 1024, 1024 * 1024, "file.trs", written=2_000_000, stage="PACK")
        self.assertIn("50.0%", line)
        self.assertIn("PACK", line)
        self.assertIn("file.trs", line)
        self.assertIn("→", line)


class CliTimingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "sample.smf"
        self.path.write_bytes(build_smf30() + build_smf80())

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_cli_json_prints_timing(self) -> None:
        out = Path(self.tmp.name) / "out.json"
        err = io.StringIO()
        with redirect_stderr(err):
            rc = main([str(self.path), "-o", str(out), "--no-progress"])
        self.assertEqual(rc, 0)
        self.assertIn("records", err.getvalue())
        self.assertIn("dump", err.getvalue())
        rows = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["job_name"], "PAYROLL")

    def test_cli_csv_prints_timing(self) -> None:
        out = Path(self.tmp.name) / "out.csv"
        err = io.StringIO()
        with redirect_stderr(err):
            rc = main([str(self.path), "-f", "csv", "-o", str(out), "--no-progress"])
        self.assertEqual(rc, 0)
        self.assertIn("records", err.getvalue())
        self.assertIn("dump", err.getvalue())
        text = out.read_text(encoding="utf-8")
        self.assertIn("PAYROLL", text)
        self.assertIn("IBMUSER", text)


if __name__ == "__main__":
    unittest.main()
