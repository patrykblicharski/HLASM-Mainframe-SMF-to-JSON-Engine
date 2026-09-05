"""Layouts for SMF 119 subtype 37 (DVIPA target server ended)."""
from __future__ import annotations

from ..layout import CHAR, IPUNION, RES, U8, U16, U32, build_layout
from ..registry import SectionSlot

DV_TSE = build_layout(
    "SMF119DV_TSE",
    [
        U16("SMF119DV_TSEFlags", "DVIPA target server-end flags"),
        RES("SMF119DV_TSEPad", 2),
        IPUNION("SMF119DV_TSEDvipa", "Distributed DVIPA address"),
        IPUNION("SMF119DV_TSETarget", "Target stack address"),
        U16("SMF119DV_TSEPort", "Server port"),
        U16("SMF119DV_TSEPortEnd", "Port range end (or 0)"),
        U8("SMF119DV_TSEProt", "Protocol (TCP/UDP)"),
        RES("SMF119DV_TSERsv", 3),
        CHAR("SMF119DV_TSEJob", 8, "Server job / AS name"),
        U32("SMF119DV_TSEConnID", "TCP connection / resource ID"),
    ],
    description="SMF119DV_TSE",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=DV_TSE),
]

__all__ = ["DV_TSE", "SECTION_SLOTS"]
