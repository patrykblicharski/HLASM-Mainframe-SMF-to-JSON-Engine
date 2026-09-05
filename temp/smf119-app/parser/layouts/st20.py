"""Auto-generated layouts for SMF 119 subtype 20 (from PACSYS offset tables)."""
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

TN_NI_S1 = build_layout(
    "SMF119TN_NI_S1",
    [
        CHAR("SMF119TN_NILU", 8, "Telnet LU name"),
        CHAR("SMF119TN_NIAppl", 8, "Host application name"),
        U32("SMF119TN_NILdev", "Telnet server internal logical device number"),
        IPV6MAPPED("SMF119TN_NIRIP", "Remote IP address"),
        IPV6MAPPED("SMF119TN_NILIP", "Local IP address"),
        U16("SMF119TN_NIRPort", "Remote (client) port number"),
        U16("SMF119TN_NILPort", "Local port number"),
        U32("SMF119TN_NITime", "Time of day of session initiation"),
        BYTES("SMF119TN_NIDate", 4, "Date of session initiation", decode="date_hex"),
    ],
    description="SMF119TN_NI_S1",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key='S1', layout=TN_NI_S1),
]

__all__ = ['TN_NI_S1', "SECTION_SLOTS"]
