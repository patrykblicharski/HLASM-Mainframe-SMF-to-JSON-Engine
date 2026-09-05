"""Layouts for SMF 119 subtype 34 (DVIPA target added)."""
from __future__ import annotations

from ..layout import CHAR, IPUNION, RES, U8, U16, build_layout
from ..registry import SectionSlot

DV_TA = build_layout(
    "SMF119DV_TA",
    [
        U16("SMF119DV_TAFlags", "DVIPA target-add flags"),
        RES("SMF119DV_TAPad", 2),
        IPUNION("SMF119DV_TADvipa", "Distributed DVIPA address"),
        IPUNION("SMF119DV_TATarget", "Target stack address"),
        U16("SMF119DV_TAPort", "Port number"),
        U16("SMF119DV_TAPortEnd", "Port range end (or 0)"),
        U8("SMF119DV_TAProt", "Protocol (TCP/UDP)"),
        RES("SMF119DV_TARsv", 3),
        CHAR("SMF119DV_TAJob", 8, "Target job / AS name"),
    ],
    description="SMF119DV_TA",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=DV_TA),
]

__all__ = ["DV_TA", "SECTION_SLOTS"]
