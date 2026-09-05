"""Tests for per-SMF-type column visibility config."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from smf2json.column_config import (
    group_config_key,
    group_label,
    group_rows,
    load_config,
    present_smf_groups,
    present_smf_types,
    save_config,
    store_group_selection,
    store_selection,
    visible_columns,
    visible_for_group,
)
from smf2json.engine import field_meta


class ColumnConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.meta = field_meta()

    def test_roundtrip_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "columns.json"
            save_config({"30": ["job_name", "time"]}, path)
            loaded = load_config(path)
            self.assertEqual(loaded["30"], ["job_name", "time"])

    def test_present_types(self) -> None:
        self.assertEqual(
            present_smf_types(
                [{"smf_record_type": "30"}, {"smf_record_type": "80"}, {"smf_record_type": "30"}]
            ),
            [30, 80],
        )

    def test_visible_defaults_to_all(self) -> None:
        available = ["time", "job_name", "user_id"]
        self.assertEqual(visible_columns(available, [30], {}, self.meta), available)

    def test_visible_uses_saved_type(self) -> None:
        available = ["time", "job_name", "user_id"]
        shown = visible_columns(available, [30], {"30": ["job_name"]}, self.meta)
        self.assertEqual(shown, ["job_name"])

    def test_store_selection_splits_by_type(self) -> None:
        cfg = store_selection(
            {},
            [30, 80],
            ["time", "job_name", "user_id"],
            self.meta,
        )
        self.assertIn("job_name", cfg["30"])
        self.assertNotIn("user_id", cfg["30"])
        self.assertIn("user_id", cfg["80"])
        self.assertIn("time", cfg["30"])
        self.assertIn("time", cfg["80"])

    def test_groups_split_type_and_subtype(self) -> None:
        rows = [
            {"smf_record_type": "30", "job_name": "A"},
            {"smf_record_type": "119", "smf_subtype": "1", "remote_ip": "10.0.0.1"},
            {"smf_record_type": "80", "user_id": "IBMUSER"},
            {"smf_record_type": "119", "smf_subtype": "1", "remote_ip": "10.0.0.2"},
        ]
        self.assertEqual(present_smf_groups(rows), [(30, None), (119, 1), (80, None)])
        grouped = group_rows(rows)
        self.assertEqual([key for key, _rows in grouped], [(30, None), (119, 1), (80, None)])
        self.assertEqual(len(grouped[1][1]), 2)
        self.assertEqual(group_label(119, 1, 2), "SMF 119-1  (2)")
        self.assertEqual(group_config_key(119, 1), "119-1")

    def test_visible_for_subtype_group(self) -> None:
        available = ["time", "remote_ip", "local_ip"]
        shown = visible_for_group(available, 119, 1, {"119-1": ["remote_ip"]})
        self.assertEqual(shown, ["remote_ip"])
        cfg = store_group_selection({}, 119, 1, ["local_ip"])
        self.assertEqual(cfg["119-1"], ["local_ip"])


if __name__ == "__main__":
    unittest.main()
