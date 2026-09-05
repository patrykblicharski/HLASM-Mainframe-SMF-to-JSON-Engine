"""Auto-generated layouts for SMF 119 subtype 7 (from PACSYS offset tables)."""
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

SP_TC_S1 = build_layout(
    "SMF119SP_TC_S1",
    [
        U64("SMF119SP_TCDuration", "Duration of recording interval in microseconds, where bit 51 is equivalent to one microsecond"),
        CHAR("SMF119SP_TCRName", 8, "Server socket resource name (the name specified on the PORT reservation statement)"),
        IPV6MAPPED("SMF119SP_TCBindIP", "For bind-specific port reservations: the local IP address"),
        U16("SMF119SP_TCPort", "Port number"),
        RES("_rsv_34", 2),
        U32("SMF119SP_TCConn", "Number of successful connection establishments"),
        U32("SMF119SP_TCBinds", "Number of socket binds to this port reservation"),
        U32("SMF119SP_TCBusySrv", "Number of connection requests rejected due to server Busy conditions"),
        U32("SMF119SP_TCSynAttack", "Number of connection requests rejected due to SYN Attack detect conditions"),
        U32("SMF119SP_TCHighwater", "Highest number of active TCP connections"),
        U32("SMF119SP_TCNumConns", "Number of active TCP connections"),
    ],
    description="SMF119SP_TC_S1",
)

SP_UD_S2 = build_layout(
    "SMF119SP_UD_S2",
    [
        U64("SMF119SP_UDDuration", "Duration of recording interval"),
        CHAR("SMF119SP_UDRName", 8, "Server socket resource name (the name specified on the PORT reservation statement)"),
        IPV6MAPPED("SMF119SP_UDBindIP", "For bind-specific port reservations: the local IP address"),
        U16("SMF119SP_UDPort", "Port number"),
        RES("_rsv_34", 2),
        U64("SMF119SP_UDIDgrams", "Number of inbound UDP datagrams to server port"),
        U64("SMF119SP_UDODgrams", "Number of outbound UDP datagrams from server port"),
        U64("SMF119SP_UDIBytes", "Number of inbound bytes"),
        U64("SMF119SP_UDOBytes", "Number of outbound bytes"),
    ],
    description="SMF119SP_UD_S2",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key='S1', layout=SP_TC_S1),
    SectionSlot(triplet_index=2, key='S2', layout=SP_UD_S2),
]

__all__ = ['SP_TC_S1', 'SP_UD_S2', "SECTION_SLOTS"]
