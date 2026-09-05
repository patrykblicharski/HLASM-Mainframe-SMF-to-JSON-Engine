"""Layouts from ezasmf.h: header, self-defining triplets, stack Ident."""
from __future__ import annotations

from .layout import BYTES, CHAR, IPV6MAPPED, RES, U8, U16, U32, build_layout

HEADER = build_layout(
    "Smf119Header",
    [
        U16("SMF119HDLength", "Length of record"),
        U16("SMF119HDSegDesc", "Segment descriptor"),
        U8(
            "SMF119HDFlags",
            "System indicator",
            flags={0x40: "SUBTYPES", 0x10: "SP4", 0x08: "SP3", 0x04: "SP2", 0x02: "VS2"},
        ),
        U8("SMF119HDType", "Record type (119)"),
        U32("SMF119HDTime", "TOD hundredths since midnight"),
        BYTES("SMF119HDDate", 4, "Date CCYYDDDS (packed)", decode="date_hex"),
        CHAR("SMF119HDSID", 4, "System ID"),
        CHAR("SMF119HDSSI", 4, "Subsystem ID"),
        U16("SMF119HDSubType", "Subtype"),
    ],
    description="Common SMF Type 119 record header",
)

TRIPLET = build_layout(
    "SMF119Triplet",
    [
        U32("Off", "Offset to section from start of record"),
        U16("Len", "Length of one section instance"),
        U16("Num", "Number of section instances"),
    ],
    description="Self-defining section triplet",
)

SDEF_PROLOGUE = build_layout(
    "SMF119SDefPrologue",
    [
        U16("SMF119SD_TRN", "Number of triplets present"),
        U16("SMF119SD_rsvd1", "Reserved"),
    ],
    description="Self-defining section prologue",
)

IDENT = build_layout(
    "SMF119Ident",
    [
        CHAR("SMF119TI_SYSName", 8, "System name"),
        CHAR("SMF119TI_SysplexName", 8, "Sysplex name"),
        CHAR("SMF119TI_Stack", 8, "TCP/IP stack name"),
        CHAR("SMF119TI_ReleaseID", 8, "CS/390 release id"),
        CHAR("SMF119TI_Comp", 8, "TCP/IP subcomponent"),
        CHAR("SMF119TI_ASName", 8, "Writer address space name"),
        CHAR("SMF119TI_UserID", 8, "User ID of security context"),
        RES("SMF119TI_rsvd1", 2),
        U16("SMF119TI_ASID", "ASID of writer"),
        U8(
            "SMF119TI_Reason",
            "Reason for writing record",
            flags={
                0xC0: "IntervalInc",
                0x80: "Interval",
                0x60: "IntervalEndInc",
                0x20: "IntervalEnd",
                0x50: "IntervalShutdownInc",
                0x10: "IntervalShutdown",
                0x48: "EventInc",
                0x08: "Event",
            },
        ),
        U8("SMF119TI_RecordID", "Correlation record ID"),
        RES("SMF119TI_rsvd2", 2),
    ],
    description="TCP/IP common stack identification section",
)

TCP_INIT = build_layout(
    "SMF119AP_TI",
    [
        CHAR("SMF119AP_TIRName", 8, "TCP socket resource name"),
        U32("SMF119AP_TIConnID", "TCP socket resource ID (ConnID)"),
        RES("SMF119AP_TIRSV1", 4),
        CHAR("SMF119AP_TISubTask", 4, "Subtask name"),
        IPV6MAPPED("SMF119AP_TIRIP", "Remote IP"),
        IPV6MAPPED("SMF119AP_TILIP", "Local IP"),
        U16("SMF119AP_TIRPort", "Remote port"),
        U16("SMF119AP_TILPort", "Local port"),
        U32("SMF119AP_TITime", "Connection start time (UTC hundredths)"),
        U32("SMF119AP_TIDate", "Connection start date"),
        BYTES("SMF119AP_TISTCK", 8, "STCK of connection start", decode="tod_hex"),
    ],
    description="TCP connection initiation section (subtype 1)",
)

assert HEADER.size == 24
assert IDENT.size == 64
assert TRIPLET.size == 8
assert SDEF_PROLOGUE.size == 4
