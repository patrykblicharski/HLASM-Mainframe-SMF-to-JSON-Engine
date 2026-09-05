"""Layouts for SMF 119 subtype 44 (RNIC interface statistics)."""
from __future__ import annotations

from ..layout import BYTES, CHAR, RES, U16, U32, U64, build_layout
from ..registry import SectionSlot

SM_RS = build_layout(
    "SMF119SM_RS",
    [
        CHAR("SMF119SM_RSName", 16, "RNIC interface name"),
        BYTES("SMF119SM_RSMAC", 6, "RNIC MAC address"),
        U16("SMF119SM_RSFlags", "RNIC statistics flags"),
        U32("SMF119SM_RSPCI", "PCI function ID"),
        U64("SMF119SM_RSInBytes", "Inbound bytes"),
        U64("SMF119SM_RSOutBytes", "Outbound bytes"),
        U64("SMF119SM_RSInPkts", "Inbound packets"),
        U64("SMF119SM_RSOutPkts", "Outbound packets"),
        U64("SMF119SM_RSInErr", "Inbound error count"),
        U64("SMF119SM_RSOutErr", "Outbound error count"),
        U32("SMF119SM_RSQPCnt", "Active queue pairs"),
        U32("SMF119SM_RSLinkCnt", "Active SMC-R links"),
        RES("SMF119SM_RSRsv", 8),
    ],
    description="SMF119SM_RS",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=SM_RS),
]

__all__ = ["SM_RS", "SECTION_SLOTS"]
