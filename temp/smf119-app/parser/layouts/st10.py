"""Auto-generated layouts for SMF 119 subtype 10 (from PACSYS offset tables)."""
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

UD_UC_S1 = build_layout(
    "SMF119UD_UC_S1",
    [
        CHAR("SMF119UD_UCRname", 8, "UDP socket resource name (address space name of address space that opens this socket)"),
        U32("SMF119UD_UCConnID", "UDP socket resource ID (connection ID)"),
        U32("SMF119UD_UCSubTask", "Subtask ID. This is the task TCB for the task owning the socket."),
        U32("SMF119UD_UCOTime", "Time of day of socket open"),
        BYTES("SMF119UD_UCODate", 4, "Date of socket open", decode="date_hex"),
        U32("SMF119UD_UCCTime", "Time of day of socket close"),
        BYTES("SMF119UD_UCCDate", 4, "Date of socket close", decode="date_hex"),
        IPV6MAPPED("SMF119UD_UCRIP", "Remote IP of last datagram received on socket"),
        IPV6MAPPED("SMF119UD_UCLIP", "Local IP address at time of socket close"),
        U16("SMF119UD_UCRPort", "Remote port of last datagram received on socket"),
        U16("SMF119UD_UCLPort", "Local port number at time of socket close"),
        U8("SMF119UD_UCType", "UDP Socket Type x'01': Standard x'02': Enterprise Extender"),
        U8("SMF119UD_UCReason", "Reason for socket close x'01': Normal x'02': Abnormal: application error or stack termination"),
        RES("_rsv_70", 2),
        U64("SMF119UD_UCInDgrams", "Number of inbound UDP datagrams"),
        U64("SMF119UD_UCOutDgrams", "Number of outbound UDP datagrams"),
        U64("SMF119UD_UCInBytes", "Number of inbound bytes"),
        U64("SMF119UD_UCOutBytes", "Number of outbound bytes"),
    ],
    description="SMF119UD_UC_S1",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key='S1', layout=UD_UC_S1),
]

__all__ = ['UD_UC_S1', "SECTION_SLOTS"]
