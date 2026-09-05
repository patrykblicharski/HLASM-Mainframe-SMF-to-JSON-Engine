"""Layouts for SMF 119 subtype 33 (DVIPA removed)."""
from __future__ import annotations

from ..layout import CHAR, IPUNION, RES, U8, U16, build_layout
from ..registry import SectionSlot

DV_RM = build_layout(
    "SMF119DV_RM",
    [
        U16("SMF119DV_RMFlags", "DVIPA removed flags"),
        U8("SMF119DV_RMType", "DVIPA type"),
        U8("SMF119DV_RMRank", "Backup rank"),
        U8("SMF119DV_RMPfxLen", "Prefix / mask length"),
        RES("SMF119DV_RMPad", 3),
        IPUNION("SMF119DV_RMAddr", "DVIPA address"),
        CHAR("SMF119DV_RMIntf", 16, "IPv6 interface name"),
        CHAR("SMF119DV_RMSaf", 8, "SAF name"),
    ],
    description="SMF119DV_RM",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=DV_RM),
]

__all__ = ["DV_RM", "SECTION_SLOTS"]
