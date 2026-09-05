"""Layouts for SMF 119 subtype 35 (DVIPA target removed)."""
from __future__ import annotations

from ..layout import CHAR, IPUNION, RES, U8, U16, build_layout
from ..registry import SectionSlot

DV_TR = build_layout(
    "SMF119DV_TR",
    [
        U16("SMF119DV_TRFlags", "DVIPA target-remove flags"),
        RES("SMF119DV_TRPad", 2),
        IPUNION("SMF119DV_TRDvipa", "Distributed DVIPA address"),
        IPUNION("SMF119DV_TRTarget", "Target stack address"),
        U16("SMF119DV_TRPort", "Port number"),
        U16("SMF119DV_TRPortEnd", "Port range end (or 0)"),
        U8("SMF119DV_TRProt", "Protocol (TCP/UDP)"),
        RES("SMF119DV_TRRsv", 3),
        CHAR("SMF119DV_TRJob", 8, "Target job / AS name"),
    ],
    description="SMF119DV_TR",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=DV_TR),
]

__all__ = ["DV_TR", "SECTION_SLOTS"]
