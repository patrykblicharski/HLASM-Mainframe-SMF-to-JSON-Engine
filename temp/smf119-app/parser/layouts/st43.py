"""Layouts for SMF 119 subtype 43 (SMC-R link end)."""
from __future__ import annotations

from ..layout import BYTES, CHAR, RES, U8, U16, U32, U64, build_layout
from ..registry import SectionSlot

SM_LT = build_layout(
    "SMF119SM_LT",
    [
        CHAR("SMF119SM_LTLclGID", 16, "Local link group ID"),
        CHAR("SMF119SM_LTRmtGID", 16, "Remote link group ID"),
        BYTES("SMF119SM_LTLclMAC", 6, "Local MAC address"),
        BYTES("SMF119SM_LTRmtMAC", 6, "Remote MAC address"),
        U16("SMF119SM_LTVlanID", "VLAN ID"),
        U8("SMF119SM_LTTermCode", "Link termination reason"),
        RES("SMF119SM_LTPad", 1),
        U32("SMF119SM_LTLclLnkID", "Local link ID"),
        U32("SMF119SM_LTRmtLnkID", "Remote link ID"),
        U64("SMF119SM_LTInBytes", "Inbound bytes"),
        U64("SMF119SM_LTOutBytes", "Outbound bytes"),
        U32("SMF119SM_LTETime", "Link end time of day"),
        U64("SMF119SM_LTESTCK", "Link end STCK"),
    ],
    description="SMF119SM_LT",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=SM_LT),
]

__all__ = ["SM_LT", "SECTION_SLOTS"]
