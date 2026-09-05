"""Auto-generated layouts for SMF 119 subtype 1 (from PACSYS offset tables)."""
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

AP_TI_S1 = build_layout(
    "SMF119AP_TI_S1",
    [
        CHAR("SMF119AP_TIRName", 8, "TCP socket resource name (Address space name of address space that established this TCP connection)"),
        U32("SMF119AP_TIConnID", "TCP socket resource ID (connection ID)"),
        U32("SMF119AP_TIRsv1", "Reserved"),
        U32("SMF119AP_TISubTask", "Subtask Name (Address of MVS™ TCB for the task that owns this connection. Note that this is not the subtask value specified on an INITAPI call.)"),
        IPV6MAPPED("SMF119AP_TIRIP", "Remote IP address at time of connection open"),
        IPV6MAPPED("SMF119AP_TILIP", "Local IP address at time of connection open"),
        U16("SMF119AP_TIRPort", "Remote port number at time of connection open"),
        U16("SMF119AP_TILPort", "Local port number at time of connection open"),
        U32("SMF119AP_TITime", "Time of day of connection establishment"),
        BYTES("SMF119AP_TIDate", 4, "Date of connection establishment", decode="date_hex"),
        U64("SMF119AP_TISTCK_T", "STCK of connection establishment - time"),
    ],
    description="SMF119AP_TI_S1",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key='S1', layout=AP_TI_S1),
]

__all__ = ['AP_TI_S1', "SECTION_SLOTS"]
