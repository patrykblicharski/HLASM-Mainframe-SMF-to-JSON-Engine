"""Layouts for SMF 119 subtype 32 (DVIPA status change)."""
from __future__ import annotations

from ..layout import CHAR, IPUNION, RES, U8, U16, build_layout
from ..registry import SectionSlot

DV_SC = build_layout(
    "SMF119DV_SC",
    [
        U16("SMF119DV_SCFlags", "DVIPA status-change flags"),
        U8("SMF119DV_SCType", "DVIPA type"),
        U8("SMF119DV_SCRank", "Backup rank"),
        U8("SMF119DV_SCPfxLen", "Prefix / mask length"),
        RES("SMF119DV_SCPad", 3),
        IPUNION("SMF119DV_SCAddr", "DVIPA address"),
        CHAR("SMF119DV_SCIntf", 16, "IPv6 interface name"),
        CHAR("SMF119DV_SCSaf", 8, "SAF name"),
    ],
    description="SMF119DV_SC",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=DV_SC),
]

__all__ = ["DV_SC", "SECTION_SLOTS"]
