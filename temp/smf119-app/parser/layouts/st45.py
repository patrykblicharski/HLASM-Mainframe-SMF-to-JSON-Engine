"""Layouts for SMF 119 subtype 45 (ISM interface statistics)."""
from __future__ import annotations

from ..layout import CHAR, RES, U16, U32, U64, build_layout
from ..registry import SectionSlot

DM_IS = build_layout(
    "SMF119DM_IS",
    [
        CHAR("SMF119DM_ISName", 16, "ISM interface name"),
        U16("SMF119DM_ISFlags", "ISM statistics flags"),
        RES("SMF119DM_ISPad", 2),
        U32("SMF119DM_ISFID", "ISM function ID"),
        U64("SMF119DM_ISInBytes", "Inbound bytes"),
        U64("SMF119DM_ISOutBytes", "Outbound bytes"),
        U64("SMF119DM_ISInPkts", "Inbound packets"),
        U64("SMF119DM_ISOutPkts", "Outbound packets"),
        U64("SMF119DM_ISInErr", "Inbound error count"),
        U64("SMF119DM_ISOutErr", "Outbound error count"),
        U32("SMF119DM_ISDmbCnt", "Active DMB count"),
        U32("SMF119DM_ISLinkCnt", "Active SMC-D links"),
        RES("SMF119DM_ISRsv", 8),
    ],
    description="SMF119DM_IS",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=DM_IS),
]

__all__ = ["DM_IS", "SECTION_SLOTS"]
