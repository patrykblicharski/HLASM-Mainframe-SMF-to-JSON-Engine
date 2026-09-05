"""Layouts for SMF 119 subtype 48 (CSSMTP configuration)."""
from __future__ import annotations

from ..layout import BYTES, CHAR, RES, U8, U16, U32, build_layout
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

ML_CF = build_layout(
    "SMF119ML_CF",
    [
        U16("SMF119ML_CFFlags", "Configuration flags"),
        U8("SMF119ML_CFFlag2", "Configuration flags byte 2"),
        U8("SMF119ML_CFFlag3", "Configuration flags byte 3"),
        CHAR("SMF119ML_CFHost", 64, "Target mail server host name"),
        U16("SMF119ML_CFPort", "Target mail server port"),
        RES("SMF119ML_CFPad", 2),
        CHAR("SMF119ML_CFJob", 8, "CSSMTP configuration job name"),
        U32("SMF119ML_CFRetry", "Retry interval (seconds)"),
        U32("SMF119ML_CFMaxConn", "Maximum connections"),
        CHAR("SMF119ML_CFCharset", 16, "Character set name"),
    ],
    description="SMF119ML_CF",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=ML_CI),
    SectionSlot(triplet_index=2, key="S2", layout=ML_CF),
]

__all__ = ["ML_CI", "ML_CF", "SECTION_SLOTS"]
