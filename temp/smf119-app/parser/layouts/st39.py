"""Layouts for SMF 119 subtype 39 (SMC-D link start)."""
from __future__ import annotations

from ..layout import CHAR, RES, U8, U16, U32, U64, build_layout
from ..registry import SectionSlot

DM_LI = build_layout(
    "SMF119DM_LI",
    [
        CHAR("SMF119DM_LILclName", 16, "Local SMC-D link name"),
        CHAR("SMF119DM_LIRmtName", 16, "Remote SMC-D link name"),
        U16("SMF119DM_LIFlags", "Link start flags"),
        U8("SMF119DM_LISMCVersion", "SMC version"),
        RES("SMF119DM_LIPad", 1),
        U32("SMF119DM_LIEid", "Enterprise ID"),
        U32("SMF119DM_LISTime", "Link start time of day"),
        U64("SMF119DM_LISSTCK", "Link start STCK"),
        CHAR("SMF119DM_LIRmtHostName", 32, "Remote host name"),
        U8("SMF119DM_LIRmtOSType", "Remote OS type"),
        RES("SMF119DM_LIRsv", 3),
        CHAR("SMF119DM_LIIsmDev", 16, "ISM device name"),
    ],
    description="SMF119DM_LI",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=DM_LI),
]

__all__ = ["DM_LI", "SECTION_SLOTS"]
