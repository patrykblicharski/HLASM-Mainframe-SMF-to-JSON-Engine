"""Layouts for SMF 119 subtype 38 (SMC-D link statistics)."""
from __future__ import annotations

from ..layout import BYTES, CHAR, RES, U8, U16, U32, U64, build_layout
from ..registry import SectionSlot

DM_LS = build_layout(
    "SMF119DM_LS",
    [
        CHAR("SMF119DM_LSLclName", 16, "Local SMC-D link name"),
        CHAR("SMF119DM_LSRmtName", 16, "Remote SMC-D link name"),
        U16("SMF119DM_LSFlags", "Link statistics flags"),
        U8("SMF119DM_LSSMCVersion", "SMC version"),
        RES("SMF119DM_LSPad", 1),
        U64("SMF119DM_LSInBytes", "Inbound byte count"),
        U64("SMF119DM_LSOutBytes", "Outbound byte count"),
        U64("SMF119DM_LSInPkts", "Inbound packet count"),
        U64("SMF119DM_LSOutPkts", "Outbound packet count"),
        U64("SMF119DM_LSInRMB", "Inbound RMB bytes"),
        U64("SMF119DM_LSOutRMB", "Outbound RMB bytes"),
        U32("SMF119DM_LSConnCnt", "Active connection count"),
        U32("SMF119DM_LSEid", "Enterprise ID"),
        CHAR("SMF119DM_LSRmtHostName", 32, "Remote host name"),
        U8("SMF119DM_LSRmtOSType", "Remote OS type"),
        RES("SMF119DM_LSRsv", 3),
    ],
    description="SMF119DM_LS",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=DM_LS),
]

__all__ = ["DM_LS", "SECTION_SLOTS"]
