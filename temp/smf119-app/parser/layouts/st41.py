"""Layouts for SMF 119 subtype 41 (SMC-R link group statistics)."""
from __future__ import annotations

from ..layout import BYTES, CHAR, RES, U8, U16, U32, U64, build_layout
from ..registry import SectionSlot

SM_GS = build_layout(
    "SMF119SM_GS",
    [
        CHAR("SMF119SM_GSLclGID", 16, "Local link group ID"),
        CHAR("SMF119SM_GSRmtGID", 16, "Remote link group ID"),
        U16("SMF119SM_GSFlags", "Group statistics flags"),
        U8("SMF119SM_GSVersion", "SMC-R version"),
        RES("SMF119SM_GSPad", 1),
        U32("SMF119SM_GSLinkCnt", "Links in group"),
        U64("SMF119SM_GSInBytes", "Group inbound bytes"),
        U64("SMF119SM_GSOutBytes", "Group outbound bytes"),
        U64("SMF119SM_GSInPkts", "Group inbound packets"),
        U64("SMF119SM_GSOutPkts", "Group outbound packets"),
        U32("SMF119SM_GSConnCnt", "Active connections"),
        RES("SMF119SM_GSRsv", 4),
    ],
    description="SMF119SM_GS",
)

SM_LS = build_layout(
    "SMF119SM_LS",
    [
        CHAR("SMF119SM_LSLclLnkID", 8, "Local link ID"),
        CHAR("SMF119SM_LSRmtLnkID", 8, "Remote link ID"),
        BYTES("SMF119SM_LSLclMAC", 6, "Local MAC address"),
        BYTES("SMF119SM_LSRmtMAC", 6, "Remote MAC address"),
        U16("SMF119SM_LSVlanID", "VLAN ID"),
        U16("SMF119SM_LSFlags", "Link statistics flags"),
        U64("SMF119SM_LSInBytes", "Link inbound bytes"),
        U64("SMF119SM_LSOutBytes", "Link outbound bytes"),
        U64("SMF119SM_LSInPkts", "Link inbound packets"),
        U64("SMF119SM_LSOutPkts", "Link outbound packets"),
        U32("SMF119SM_LSQP", "Queue pair number"),
        RES("SMF119SM_LSRsv", 4),
    ],
    description="SMF119SM_LS",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=SM_GS),
    SectionSlot(triplet_index=2, key="S2", layout=SM_LS),
]

__all__ = ["SM_GS", "SM_LS", "SECTION_SLOTS"]
