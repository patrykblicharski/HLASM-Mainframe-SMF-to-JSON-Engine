"""Layouts for SMF 119 subtype 40 (SMC-D link end)."""
from __future__ import annotations

from ..layout import CHAR, RES, U8, U16, U32, U64, build_layout
from ..registry import SectionSlot

DM_LT = build_layout(
    "SMF119DM_LT",
    [
        CHAR("SMF119DM_LTLclName", 16, "Local SMC-D link name"),
        CHAR("SMF119DM_LTRmtName", 16, "Remote SMC-D link name"),
        U16("SMF119DM_LTFlags", "Link end flags"),
        U8("SMF119DM_LTSMCVersion", "SMC version"),
        U8("SMF119DM_LTTermCode", "Link termination reason"),
        U32("SMF119DM_LTEid", "Enterprise ID"),
        U32("SMF119DM_LTETime", "Link end time of day"),
        U64("SMF119DM_LTESTCK", "Link end STCK"),
        U64("SMF119DM_LTInBytes", "Inbound byte count"),
        U64("SMF119DM_LTOutBytes", "Outbound byte count"),
        CHAR("SMF119DM_LTRmtHostName", 32, "Remote host name"),
        U8("SMF119DM_LTRmtOSType", "Remote OS type"),
        RES("SMF119DM_LTRsv", 3),
    ],
    description="SMF119DM_LT",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=DM_LT),
]

__all__ = ["DM_LT", "SECTION_SLOTS"]
