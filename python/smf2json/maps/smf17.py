"""SMF type 17 field map — Scratch Data Set Status (IBM IFASMFR / PACSYS).

Fixed header through SMF17NVL; first volume serial at absolute offset 94
(volume entries are 8 bytes each starting at 92 — no section triplets).
"""

from __future__ import annotations

from ..types import FieldSpec as F

FIELDS = [
    F("smf_record_type", "SMF17RTY", "DEC1", 5, description="Record type 17 (X'11')"),
    F("smf_system_id", "SMF17SID", "CHR4", 14, description="System identification (SID)"),
    F("time", "SMF17TME", "TME", 6, description="Time moved to SMF buffer"),
    F("date", "SMF17DTE", "DTE", 10, description="Date moved to SMF buffer"),
    F("job_name", "SMF17JBN", "CHR8", 18, description="Job name (job log identification)"),
    F("reader_start_t", "SMF17RST", "TME", 26, description="Reader recognized JOB card — time"),
    F("reader_start_d", "SMF17RSD", "DTE", 30, description="Reader recognized JOB card — date"),
    F(
        "user_id_field",
        "SMF17UID",
        "CHR8",
        34,
        description="User-defined identification (common exit area)",
    ),
    F(
        "record_indicator",
        "SMF17RIN",
        "HEX2",
        42,
        description="Record indicator (reserved in current IBM mapping)",
    ),
    F(
        "dsname",
        "SMF17DSN",
        "CHR",
        44,
        length=44,
        description="Data set name scratched",
    ),
    F(
        "volume_count",
        "SMF17NVL",
        "DEC1",
        91,
        description="Number of volume entries that follow",
    ),
    # First volume information section @92: SMF17RV2(2) + SMF17FVL(6)
    F(
        "volume_serial",
        "SMF17FVL",
        "CHR",
        94,
        length=6,
        description="Volume serial number (first volume entry)",
    ),
]
