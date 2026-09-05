"""Auto-generated layouts for SMF 119 subtype 22 (from PACSYS offset tables)."""
from __future__ import annotations

from ..layout import (
    BYTES,
    CHAR,
    IPV4,
    IPV6MAPPED,
    RES,
    U8,
    U16,
    U32,
    U64,
    VAR_EBCDIC,
    build_layout,
)
from ..registry import SectionSlot

TN_CI_S1 = build_layout(
    "SMF119TN_CI_S1",
    [
        IPV6MAPPED("SMF119TN_CIRIP", "Remote (server) IP address"),
        IPV6MAPPED("SMF119TN_CILIP", "Local IP address"),
        U16("SMF119TN_CIRPort", "Remote (server) port number"),
        U16("SMF119TN_CILPort", "Local port number"),
        U32("SMF119TN_CITime", "Time of day of session initiation"),
        BYTES("SMF119TN_CIDate", 4, "Date of session initiation", decode="date_hex"),
    ],
    description="SMF119TN_CI_S1",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key='S1', layout=TN_CI_S1),
]

__all__ = ['TN_CI_S1', "SECTION_SLOTS"]
