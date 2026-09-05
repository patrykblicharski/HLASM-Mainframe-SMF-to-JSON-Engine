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
    build_smf14,
    build_smf15,
    build_smf17,
    build_smf30,
    build_smf30_st01,
    build_smf30_st05,
    build_smf42_st20,
    build_smf42_st21,
    build_smf42_st24,
    build_smf61,
    build_smf65,
    build_smf66,
    build_smf80,
    build_smf119_st01,
    build_smf119_st02,
    build_smf119_st03,
    build_smf119_st04,
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
        self.assertEqual(r30["smf_subtype"], "4")
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
        self.assertEqual(r80["group_name"], "SYS1")
        self.assertEqual(r80["event_code"], "2")
        self.assertEqual(r80["event_qualifier"], "0")
        self.assertEqual(r80["terminal_id"], "TSO001")
        self.assertEqual(r80["job_name"], "IBMUSER")
        self.assertEqual(r80["racf_fmid"], "77E0")
        self.assertEqual(r80["security_label"], "SYSLOW")
        self.assertEqual(r80["authorities_used"], "80")
        self.assertEqual(r80["class_name"], "DATASET")
        self.assertEqual(r80["old_resource"], "IBMUSER.REXX")
        self.assertEqual(r80["volser"], "SYS001")
        self.assertEqual(r80["access_requested"], "02")
        self.assertEqual(r80["access_allowed"], "08")
        self.assertEqual(r80["mfa_factor_name"], "AZFTOTP1")
        # Type 80 stays on MAPS_BY_TYPE; bytes 22–23 are USR, not STY.
        self.assertFalse(any(rty == 80 for rty, _sty in MAPS_BY_SUBTYPE))
        self.assertEqual(len(fields_for(80)), len(fields_for(80, subtype=2)))

    def test_convert_type80_jobinit(self) -> None:
        from smf2json.sample_dump import build_smf80_jobinit

        path = Path(self.tmp.name) / "smf80-evt1.smf"
        path.write_bytes(build_smf80_jobinit())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_record_type"], "80")
        self.assertEqual(row["event_code"], "1")
        self.assertEqual(row["user_id"], "WITADM4")
        self.assertEqual(row["group_name"], "WITADMGP")
        self.assertEqual(row["job_name"], "XH4AMGS")
        self.assertEqual(row["application_name"], "TSO")
        self.assertEqual(row["racf_fmid"], "77E0")

    def test_convert_type30_st01(self) -> None:
        path = Path(self.tmp.name) / "smf30-1.smf"
        path.write_bytes(build_smf30_st01())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_record_type"], "30")
        self.assertEqual(row["smf_subtype"], "1")
        self.assertEqual(row["job_name"], "INITJOB1")
        self.assertEqual(row["product_name"], "SMF")
        self.assertNotIn("cpu_step_time", row)
        self.assertNotIn("step_comp_code", row)

    def test_convert_type30_st05(self) -> None:
        path = Path(self.tmp.name) / "smf30-5.smf"
        path.write_bytes(build_smf30_st05())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_record_type"], "30")
        self.assertEqual(row["smf_subtype"], "5")
        self.assertEqual(row["job_name"], "TERMJOB1")
        self.assertEqual(row["step_comp_code"], "0")
        self.assertEqual(row["cpu_step_time"], "2500")
        self.assertEqual(row["srb_time"], "100")

    def test_smf30_subtype_registry(self) -> None:
        for sty in (1, 2, 3, 4, 5, 6):
            self.assertTrue(fields_for(30, sty), f"missing map for 30-{sty}")
        self.assertEqual(fields_for(30, 7), ())
        mapped = {sty for rty, sty in MAPS_BY_SUBTYPE if rty == 30}
        self.assertEqual(mapped, {1, 2, 3, 4, 5, 6})
        keys1 = {f.json_key for f in fields_for(30, 1)}
        keys4 = {f.json_key for f in fields_for(30, 4)}
        self.assertIn("job_name", keys1)
        self.assertNotIn("cpu_step_time", keys1)
        self.assertIn("cpu_step_time", keys4)
        self.assertIn("step_comp_code", keys4)

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

    def test_convert_type17(self) -> None:
        path = Path(self.tmp.name) / "smf17.smf"
        path.write_bytes(build_smf17())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_record_type"], "17")
        self.assertEqual(row["smf_system_id"], "PROD")
        self.assertEqual(row["time"], "15:30:00")
        self.assertEqual(row["date"], "2026-03-25")
        self.assertEqual(row["job_name"], "SCRJOB01")
        self.assertEqual(row["reader_start_t"], "09:00:00")
        self.assertEqual(row["reader_start_d"], "2026-03-25")
        self.assertEqual(row["user_id_field"], "IBMUSER")
        self.assertEqual(row["dsname"], "IBMUSER.TEMP.DATA")
        self.assertEqual(row["volume_count"], "1")
        self.assertEqual(row["volume_serial"], "SCR001")
        self.assertTrue(fields_for(17))

    def test_convert_type15(self) -> None:
        path = Path(self.tmp.name) / "smf15.smf"
        path.write_bytes(build_smf15())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_record_type"], "15")
        self.assertEqual(row["smf_system_id"], "PROD")
        self.assertEqual(row["job_name"], "PAYROLL")
        self.assertEqual(row["time"], "15:30:45")
        self.assertEqual(row["date"], "2026-03-25")
        self.assertEqual(row["ddname"], "SYSOUT")
        self.assertEqual(row["dsname"], "SYS1.PAYROLL.OUT")
        self.assertEqual(row["member_name"], "MEMBER1")
        self.assertEqual(row["volser_1"], "WORK01")
        self.assertEqual(row["blksize"], "32760")
        self.assertEqual(row["lrecl"], "80")
        self.assertEqual(row["device_number"], "1A2B")
        self.assertEqual(row["ucb_volser"], "WORK01")
        self.assertEqual(row["excp_count"], "1234")
        self.assertEqual(row["tracks_allocated"], "150")
        self.assertEqual(row["extent_count"], "3")
        self.assertEqual(row["open_time"], "15:00:00")
        self.assertEqual(row["open_date"], "2026-03-25")

    def test_convert_type14(self) -> None:
        path = Path(self.tmp.name) / "smf14.smf"
        path.write_bytes(build_smf14())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_record_type"], "14")
        self.assertEqual(row["smf_system_id"], "PROD")
        self.assertEqual(row["time"], "09:15:30")
        self.assertEqual(row["date"], "2026-03-25")
        self.assertEqual(row["job_name"], "PAYROLL")
        self.assertEqual(row["ddname"], "INFILE")
        self.assertEqual(row["dsname"], "SYS1.PAYROLL.MASTER")
        self.assertEqual(row["blksize"], "27998")
        self.assertEqual(row["lrecl"], "80")
        self.assertEqual(row["volser_1"], "SCR001")
        self.assertEqual(row["excp_count"], "4200")
        self.assertEqual(row["device_number"], "1234")
        self.assertEqual(row["ucb_volser"], "SCR001")
        self.assertEqual(row["open_date"], "2026-03-25")

    def test_convert_type61(self) -> None:
        path = Path(self.tmp.name) / "smf61.smf"
        path.write_bytes(build_smf61())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_record_type"], "61")
        self.assertEqual(row["smf_system_id"], "PROD")
        self.assertEqual(row["time"], "11:31:13")
        self.assertEqual(row["date"], "2026-03-25")
        self.assertEqual(row["catalog_action"], "IN")
        self.assertEqual(row["job_name"], "DEFJOB01")
        self.assertEqual(row["reader_start_t"], "08:00:00")
        self.assertEqual(row["reader_start_d"], "2026-03-25")
        self.assertEqual(row["user_id_field"], "IBMUSER")
        self.assertEqual(row["catalog_name"], "CATALOG.USER.ICF")
        self.assertEqual(row["entry_type"], "A")
        self.assertEqual(row["entry_name"], "IBMUSER.NEW.DATASET")
        self.assertEqual(row["product_name"], "IGG0CLX0")
        self.assertTrue(fields_for(61))

    def test_convert_type65(self) -> None:
        path = Path(self.tmp.name) / "smf65.smf"
        path.write_bytes(build_smf65())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_record_type"], "65")
        self.assertEqual(row["smf_system_id"], "PROD")
        self.assertEqual(row["time"], "11:41:07")
        self.assertEqual(row["catalog_action"], "DE")
        self.assertEqual(row["function_indicator"], "S")
        self.assertEqual(row["job_name"], "DELJOB01")
        self.assertEqual(row["catalog_name"], "CATALOG.USER.ICF")
        self.assertEqual(row["entry_type"], "A")
        self.assertEqual(row["entry_name"], "IBMUSER.OLD.DATASET")
        self.assertTrue(fields_for(65))

    def test_convert_type66(self) -> None:
        path = Path(self.tmp.name) / "smf66.smf"
        path.write_bytes(build_smf66())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_record_type"], "66")
        self.assertEqual(row["smf_system_id"], "PROD")
        self.assertEqual(row["time"], "11:45:00")
        self.assertEqual(row["catalog_action"], "UP")
        self.assertEqual(row["function_indicator"], "R")
        self.assertEqual(row["job_name"], "ALTJOB01")
        self.assertEqual(row["catalog_name"], "CATALOG.USER.ICF")
        self.assertEqual(row["entry_name"], "IBMUSER.OLD.NAME")
        self.assertEqual(row["new_entry_name"], "IBMUSER.NEW.NAME")
        self.assertTrue(fields_for(66))

    def test_convert_type42_st20(self) -> None:
        path = Path(self.tmp.name) / "smf42-20.smf"
        path.write_bytes(build_smf42_st20())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_record_type"], "42")
        self.assertEqual(row["smf_subtype"], "20")
        self.assertEqual(row["smf_system_id"], "PROD")
        self.assertEqual(row["smf_subsystem_id"], "SMS")
        self.assertEqual(row["product_name"], "DFSMS")
        self.assertEqual(row["job_name"], "STOWJOB1")
        self.assertEqual(row["step_name"], "STEP1")
        self.assertEqual(row["dsname"], "SYS1.PROCLIB")
        self.assertEqual(row["volser"], "SYSRES")

    def test_convert_type42_st21(self) -> None:
        path = Path(self.tmp.name) / "smf42-21.smf"
        path.write_bytes(build_smf42_st21())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_record_type"], "42")
        self.assertEqual(row["smf_subtype"], "21")
        self.assertEqual(row["job_name"], "DELJOB01")
        self.assertEqual(row["dsname"], "IBMUSER.SOURCE.PDS")
        self.assertEqual(row["volser"], "TSO001")
        self.assertEqual(row["member_name"], "MEMBER1")
        self.assertEqual(row["member_name_len"], "7")
        self.assertEqual(row["alias_count"], "0")

    def test_convert_type42_st24(self) -> None:
        path = Path(self.tmp.name) / "smf42-24.smf"
        path.write_bytes(build_smf42_st24())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_record_type"], "42")
        self.assertEqual(row["smf_subtype"], "24")
        self.assertEqual(row["job_name"], "ADDJOB01")
        self.assertEqual(row["dsname"], "IBMUSER.SOURCE.PDSE")
        self.assertEqual(row["volser"], "WORK01")
        self.assertEqual(row["member_name"], "NEWMEM")
        self.assertEqual(row["member_flags"], "40")

    def test_smf42_subtype_registry(self) -> None:
        for sty in (20, 21, 22, 23, 24, 25):
            self.assertTrue(fields_for(42, sty), f"missing map for 42-{sty}")
        self.assertEqual(fields_for(42, 1), ())
        mapped = {sty for rty, sty in MAPS_BY_SUBTYPE if rty == 42}
        self.assertEqual(mapped, {20, 21, 22, 23, 24, 25})

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

    def test_convert_type119_st04_nmtp_partial(self) -> None:
        path = Path(self.tmp.name) / "smf119-4.smf"
        path.write_bytes(build_smf119_st04())
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["smf_subtype"], "4")
        self.assertEqual(row["tcp_component"], "STACK")
        self.assertEqual(row["change_rsn"], "1")
        self.assertEqual(row["pico_flags"], "80")
        self.assertEqual(row["console"], "CONS01")
        self.assertEqual(row["sysplex_grp"], "PLEXGRP")
        self.assertEqual(row["pico_change_date"], "2026-03-25")
        self.assertEqual(row["somaxconn"], "1024")
        self.assertEqual(row["tcp_rcvbuf"], "65535")
        self.assertEqual(row["tcp_sndbuf"], "65535")
        self.assertEqual(row["tcp_ephem_beg"], "1024")
        self.assertEqual(row["tcp_ephem_end"], "65535")

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
        rec[22:24] = (94).to_bytes(2, "big")
        path = Path(self.tmp.name) / "smf119-94.smf"
        path.write_bytes(bytes(rec))
        rows = convert_dump(read_dump(str(path)))
        self.assertEqual(rows, [])

    def test_smf119_subtype_registry(self) -> None:
        self.assertTrue(fields_for(119, 1))
        self.assertTrue(fields_for(119, 2))
        self.assertTrue(fields_for(119, 4))
        self.assertTrue(fields_for(119, 70))
        self.assertEqual(fields_for(119, 94), ())
        mapped = {sty for rty, sty in MAPS_BY_SUBTYPE if rty == 119}
        self.assertGreaterEqual(len(mapped), 47)
        self.assertIn(4, mapped)


if __name__ == "__main__":
    unittest.main()
