"""Layouts for SMF 119 subtype 36 (DVIPA target server started)."""
from __future__ import annotations

from ..layout import CHAR, IPUNION, RES, U8, U16, U32, build_layout
from ..registry import SectionSlot

DV_TSS = build_layout(
    "SMF119DV_TSS",
    [
        U16("SMF119DV_TSSFlags", "DVIPA target server-start flags"),
        RES("SMF119DV_TSSPad", 2),
        IPUNION("SMF119DV_TSSDvipa", "Distributed DVIPA address"),
        IPUNION("SMF119DV_TSSTarget", "Target stack address"),
        U16("SMF119DV_TSSPort", "Server port"),
        U16("SMF119DV_TSSPortEnd", "Port range end (or 0)"),
        U8("SMF119DV_TSSProt", "Protocol (TCP/UDP)"),
        RES("SMF119DV_TSSRsv", 3),
        CHAR("SMF119DV_TSSJob", 8, "Server job / AS name"),
        U32("SMF119DV_TSSConnID", "TCP connection / resource ID"),
    ],
    description="SMF119DV_TSS",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=DV_TSS),
]

__all__ = ["DV_TSS", "SECTION_SLOTS"]
