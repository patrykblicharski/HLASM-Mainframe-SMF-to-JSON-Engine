"""Layouts for SMF 119 subtype 52 (CSSMTP statistics)."""
from __future__ import annotations

from ..layout import BYTES, CHAR, RES, U32, U64, build_layout
from ..registry import SectionSlot

ML_CI = build_layout(
    "SMF119ML_CI",
    [
        CHAR("SMF119ML_CI_JOB", 8, "CSSMTP job name"),
        U32("SMF119ML_CI_Entry", "JES reader entry time (1/100 s)"),
        BYTES("SMF119ML_CI_EDate", 4, "JES reader entry date", decode="date_hex"),
        CHAR("SMF119ML_CI_USEID", 8, "User-defined identification"),
        CHAR("SMF119ML_CI_EXTWRT", 8, "External writer name"),
        CHAR("SMF119ML_CI_Jes", 4, "JES subsystem name"),
    ],
    description="SMF119ML_CI",
)

ML_ST = build_layout(
    "SMF119ML_ST",
    [
        U32("SMF119ML_STSTime", "Interval start time of day"),
        BYTES("SMF119ML_STSDate", 4, "Interval start date", decode="date_hex"),
        U32("SMF119ML_STETime", "Interval end time of day"),
        BYTES("SMF119ML_STEDate", 4, "Interval end date", decode="date_hex"),
        U64("SMF119ML_STMailSent", "Mail messages sent"),
        U64("SMF119ML_STMailFail", "Mail messages failed"),
        U64("SMF119ML_STBytesOut", "Outbound mail bytes"),
        U64("SMF119ML_STConnOk", "Successful connections"),
        U64("SMF119ML_STConnFail", "Failed connections"),
        U32("SMF119ML_STSpoolRead", "Spool files read"),
        U32("SMF119ML_STRetry", "Retry count"),
        RES("SMF119ML_STRsv", 8),
    ],
    description="SMF119ML_ST",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=ML_CI),
    SectionSlot(triplet_index=2, key="S2", layout=ML_ST),
]

__all__ = ["ML_CI", "ML_ST", "SECTION_SLOTS"]
