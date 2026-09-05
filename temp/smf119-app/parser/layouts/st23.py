"""Auto-generated layouts for SMF 119 subtype 23 (from PACSYS offset tables)."""
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

TN_CT_S1 = build_layout(
    "SMF119TN_CT_S1",
    [
        IPV6MAPPED("SMF119TN_CTRIP", "Remote (server) IP address"),
        IPV6MAPPED("SMF119TN_CTLIP", "Local IP address"),
        U16("SMF119TN_CTRPort", "Remote (server) port number"),
        U16("SMF119TN_CTLPort", "Local port number"),
        CHAR("SMF119TN_CTNJENode", 8, "NJE Node Name"),
        U64("SMF119TN_CTInBytes", "Inbound byte count"),
        U64("SMF119TN_CTOutBytes", "Outbound byte count"),
        U32("SMF119TN_CTiTime", "Time of day of session initiation"),
        BYTES("SMF119TN_CTiDate", 4, "Date of session initiation", decode="date_hex"),
        U32("SMF119TN_CTtTime", "Time of day of session termination"),
        BYTES("SMF119TN_CTtDate", 4, "Date of session termination", decode="date_hex"),
        U32("SMF119TN_CTDur", "Telnet client session duration in 1/100 seconds"),
        U8("SMF119TN_CTCOpt", "Telnet connection options negotiated for this connection: x000 0000 Reserved 0100 0000 Terminal type 0010 0000 End of record 0001 0000 Transmit binary 0000 1000 Echos 0000 0100 Suppress go ahead 0000 00xx Reserved"),
        RES("_rsv_81", 3),
        CHAR("SMF119TN_CTDevt", 20, "Telnet device type"),
    ],
    description="SMF119TN_CT_S1",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key='S1', layout=TN_CT_S1),
]

__all__ = ['TN_CT_S1', "SECTION_SLOTS"]
