"""Unit tests for SMF reader/engine (stdlib unittest)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from smf2json.engine import convert_dump, convert_path, ordered_columns
from smf2json.maps import MAPS_BY_SUBTYPE, fields_for
from smf2json.reader import iter_dump, read_dump
from smf2json.sample_dump import (
    build_smf30,
    build_smf80,
    build_smf119_st01,
    build_smf119_st02,
    build_smf119_st03,
    build_smf119_st10,
    build_smf119_st32,
)
from smf2json.types import FieldSpec, convert_value, parse_ip16, parse_ip4, parse_ipunion, parse_smf_date, parse_smf_time


class TypeTests(unittest.TestCase):
    def test_time(self) -> None:
        raw = ((12 * 3600 + 13 * 60 + 59) * 100).to_bytes(4, "big")
        self.assertEqual(parse_smf_time(raw), "12:13:59")

    def test_time_keeps_hundredths(self) -> None:
        raw = ((8 * 3600) * 100 + 46).to_bytes(4, "big")
        self.assertEqual(parse_smf_time(raw), "08:00:00.46")

    def test_time_packed(self) -> None:
        self.assertEqual(parse_smf_time(bytes.fromhex("0121359f")), "12:13:59")

    def test_date(self) -> None:
        # 2026-03-25 → julian day 84 → packed 0c yy ddd F
        raw = bytes.fromhex("0126084f")
        self.assertEqual(parse_smf_date(raw), "2026-03-25")

    def test_ebcdic_chr(self) -> None:
        spec = FieldSpec("sid", "SMF30SID", "CHR4", 14)
        raw = "PROD".encode("cp037")
        self.assertEqual(convert_value(spec, raw), "PROD")

    def test_ip16_mapped(self) -> None:
        raw = bytes(10) + b"\xff\xff" + bytes((10, 1, 2, 3))
        self.assertEqual(parse_ip16(raw), "10.1.2.3")

    def test_ip4(self) -> None:
        self.assertEqual(parse_ip4(bytes((10, 20, 30, 40))), "10.20.30.40")
        self.assertEqual(parse_ip4(bytes(4)), "")

    def test_ipunion_v4_in_prefix(self) -> None:
        raw = bytes((10, 20, 30, 40)) + bytes(12)
        self.assertEqual(parse_ipunion(raw), "10.20.30.40")


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

    def test_iter_progress_reaches_eof(self) -> None:
        ticks: list[tuple[int, int]] = []
        recs = list(iter_dump(str(self.path), progress=lambda pos, n: ticks.append((pos, n))))
        self.assertEqual(len(recs), 2)
        self.assertTrue(ticks)
        self.assertEqual(ticks[0][0], 0)
        self.assertEqual(ticks[-1][0], ticks[-1][1])
        self.assertEqual(ticks[-1][1], self.path.stat().st_size)

    def test_iter_dump_matches_read_dump(self) -> None:
        streamed = list(iter_dump(str(self.path)))
        listed = read_dump(str(self.path))
        self.assertEqual(len(streamed), len(listed))
        self.assertEqual(streamed[0].record_type, listed[0].record_type)

    def test_bdw_prefixed_type30_time(self) -> None:
        rec = build_smf30()
        block = (len(rec) + 4).to_bytes(2, "big") + b"\x00\x00" + rec
        path = Path(self.tmp.name) / "bdw.smf"
        path.write_bytes(block)
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["time"], "12:13:59")
        self.assertEqual(rows[0]["job_name"], "PAYROLL")

    def test_record_without_rdw_still_decodes_time(self) -> None:
        rec = build_smf30()[4:]
        path = Path(self.tmp.name) / "nordw.smf"
        path.write_bytes(rec)
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["time"], "12:13:59")
        self.assertEqual(rows[0]["smf_system_id"], "PROD")

    def test_convert_path_streams(self) -> None:
        rows = list(convert_path(str(self.path)))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["smf_record_type"], "30")
        self.assertEqual(rows[1]["smf_record_type"], "80")

    def test_convert_path_many_records(self) -> None:
        path = Path(self.tmp.name) / "many.smf"
        path.write_bytes(build_smf30() * 300)
        count = 0
        for row in convert_path(str(path)):
            count += 1
            self.assertEqual(row["smf_record_type"], "30")
        self.assertEqual(count, 300)

    def test_convert_type119_st01(self) -> None:
        path = Path(self.tmp.name) / "smf119.smf"
        path.write_bytes(build_smf119_st01())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_record_type"], "119")
        self.assertEqual(row["smf_subtype"], "1")
        self.assertEqual(row["smf_system_id"], "PROD")
        self.assertEqual(row["tcp_stack"], "TCPIP")
        self.assertEqual(row["tcp_component"], "TCP")
        self.assertEqual(row["resource_name"], "FTPTA5")
        self.assertEqual(row["remote_ip"], "10.1.2.3")
        self.assertEqual(row["local_ip"], "192.168.1.10")
        self.assertEqual(row["remote_port"], "443")
        self.assertEqual(row["local_port"], "21")
        self.assertEqual(row["record_reason"], "08")
        self.assertEqual(row["conn_time"], "14:04:06")
        self.assertEqual(row["conn_date"], "2026-03-25")
        self.assertEqual(row["subtask_tcb"], "00ABCDEF")
        self.assertEqual(row["conn_stck"], "00DECAFBAD010203")

    def test_convert_type119_st02(self) -> None:
        path = Path(self.tmp.name) / "smf119-2.smf"
        path.write_bytes(build_smf119_st02())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_subtype"], "2")
        self.assertEqual(row["resource_name"], "FTPTA5")
        self.assertEqual(row["remote_ip"], "10.1.2.3")
        self.assertEqual(row["local_ip"], "192.168.1.10")
        self.assertEqual(row["remote_port"], "443")
        self.assertEqual(row["local_port"], "21")
        self.assertEqual(row["in_bytes"], "4096")
        self.assertEqual(row["out_bytes"], "2048")
        self.assertEqual(row["term_code"], "21")
        self.assertEqual(row["conn_end_time"], "14:05:01")
        self.assertEqual(row["socket_status"], "01")

    def test_convert_type119_st03_var_chr(self) -> None:
        path = Path(self.tmp.name) / "smf119-3.smf"
        path.write_bytes(build_smf119_st03())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_subtype"], "3")
        self.assertEqual(row["ftp_cmd"], "RETR")
        self.assertEqual(row["remote_user"], "FTPUSER")
        self.assertEqual(row["local_user"], "IBMUSER")
        self.assertEqual(row["bytes_transferred"], "8192")
        self.assertEqual(row["file_name"], "USER.FTP.DATA")

    def test_convert_type119_st10(self) -> None:
        path = Path(self.tmp.name) / "smf119-10.smf"
        path.write_bytes(build_smf119_st10())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_subtype"], "10")
        self.assertEqual(row["resource_name"], "UDPSRV")
        self.assertEqual(row["remote_ip"], "10.9.8.7")
        self.assertEqual(row["local_port"], "5353")
        self.assertEqual(row["in_bytes"], "100")
        self.assertEqual(row["out_bytes"], "200")

    def test_convert_type119_st32_ipunion(self) -> None:
        path = Path(self.tmp.name) / "smf119-32.smf"
        path.write_bytes(build_smf119_st32())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_subtype"], "32")
        self.assertEqual(row["sc_addr"], "10.20.30.40")

    def test_smf119_unmapped_subtype_skipped(self) -> None:
        rec = bytearray(build_smf119_st01())
        rec[22:24] = (4).to_bytes(2, "big")
        path = Path(self.tmp.name) / "smf119-4.smf"
        path.write_bytes(bytes(rec))
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(rows, [])

    def test_smf119_subtype_registry(self) -> None:
        self.assertTrue(fields_for(119, 1))
        self.assertTrue(fields_for(119, 2))
        self.assertTrue(fields_for(119, 70))
        self.assertEqual(fields_for(119, 4), ())
        self.assertEqual(fields_for(119, 94), ())
        mapped = {sty for rty, sty in MAPS_BY_SUBTYPE if rty == 119}
        self.assertGreaterEqual(len(mapped), 46)
        self.assertNotIn(4, mapped)


if __name__ == "__main__":
    unittest.main()
