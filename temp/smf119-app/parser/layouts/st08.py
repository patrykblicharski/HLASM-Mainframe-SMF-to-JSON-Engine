"""Auto-generated layouts for SMF 119 subtype 8 (from PACSYS offset tables)."""
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

TC_ST_S1 = build_layout(
    "SMF119TC_ST_S1",
    [
        U8("SMF119TC_STType", "Event type: x'80' Stack start up x'40' Stack termination x'20' Stack unplanned termination"),
        U8("SMF119TC_STFlags", "Event flags: x'80' IPv6 supported on this stack"),
        RES("_rsv_2", 2),
        U32("SMF119TC_STTime", "Time of day stack startup or termination"),
        BYTES("SMF119TC_STDate", 4, "Date of stack startup or termination", decode="date_hex"),
    ],
    description="SMF119TC_ST_S1",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key='S1', layout=TC_ST_S1),
]

__all__ = ['TC_ST_S1', "SECTION_SLOTS"]
