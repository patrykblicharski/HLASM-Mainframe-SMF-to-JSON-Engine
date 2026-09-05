"""Layouts for SMF 119 subtype 42 (SMC-R link start)."""
from __future__ import annotations

from ..layout import BYTES, CHAR, RES, U16, U32, U64, build_layout
from ..registry import SectionSlot

SM_LI = build_layout(
    "SMF119SM_LI",
    [
        CHAR("SMF119SM_LILclGID", 16, "Local link group ID"),
        CHAR("SMF119SM_LIRmtGID", 16, "Remote link group ID"),
        BYTES("SMF119SM_LILclMAC", 6, "Local MAC address"),
        BYTES("SMF119SM_LIRmtMAC", 6, "Remote MAC address"),
        U16("SMF119SM_LIVlanID", "VLAN ID"),
        U16("SMF119SM_LIFlags", "Link start flags"),
        U32("SMF119SM_LILclLnkID", "Local link ID"),
        U32("SMF119SM_LIRmtLnkID", "Remote link ID"),
        BYTES("SMF119SM_LILclQP", 3, "Local queue pair"),
        BYTES("SMF119SM_LIRmtQP", 3, "Remote queue pair"),
        BYTES("SMF119SM_LILnkGrpID", 3, "Link group ID (short)"),
        RES("SMF119SM_LIPad", 1),
        U32("SMF119SM_LISTime", "Link start time of day"),
        U64("SMF119SM_LISSTCK", "Link start STCK"),
    ],
    description="SMF119SM_LI",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=SM_LI),
]

__all__ = ["SM_LI", "SECTION_SLOTS"]
