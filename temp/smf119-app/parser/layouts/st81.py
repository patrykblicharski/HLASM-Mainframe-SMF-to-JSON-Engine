"""Layouts for SMF 119 subtype 81 (VTAM 3270 IDS)."""
from __future__ import annotations

from ..layout import BYTES, CHAR, IPV6MAPPED, RES, U8, U16, U32, U64, build_layout
from ..registry import SectionSlot

DS_CM = build_layout(
    "IST119DS_32",
    [
        U64("IST119DS_Time", "STCK time of the incident (UTC)"),
        CHAR("IST119DS_PLUName", 17, "PLU NetId.name"),
        CHAR("IST119DS_SLUName", 17, "SLU NetId.name"),
        BYTES("IST119DS_SID", 10, "Session ID"),
        U64("IST119DS_IncTk", "Incident token"),
        CHAR("IST119DS_ECode", 4, "Event code"),
        U8("IST119DS_DSCOUNT", "Data-stream buffer count"),
        U8("IST119DS_ACTION", "Action flags"),
        RES("IST119DS_ActPad", 6),
        IPV6MAPPED("IST119DS_RIPV6", "Remote IP address"),
        U16("IST119DS_RPort", "Remote port"),
        U8("IST119DS_Row", "Cursor row"),
        U8("IST119DS_Column", "Cursor column"),
        U16("IST119DS_Offset", "Field offset in buffer"),
        U16("IST119DS_OBufO", "Outbound buffer offset"),
        U16("IST119DS_IBufO", "Inbound buffer offset"),
        U16("IST119DS_OBufL", "Outbound buffer length"),
        U16("IST119DS_IBufL", "Inbound buffer length"),
        U16("IST119DS_OSEQ", "Outbound PIU sequence"),
        U16("IST119DS_ISEQ", "Inbound PIU sequence"),
    ],
    description="IST119DS_32",
)

DS_OB = build_layout(
    "IST119DS_OB",
    [
        BYTES("IST119DS_DORU", 64, "RU data (truncated preview)"),
    ],
    description="Outbound RU data (truncated preview)",
)

DS_IB = build_layout(
    "IST119DS_IB",
    [
        BYTES("IST119DS_DIRU", 64, "RU data (truncated preview)"),
    ],
    description="Inbound RU data (truncated preview)",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=DS_CM),
    SectionSlot(triplet_index=2, key="S2", layout=DS_OB),
    SectionSlot(triplet_index=3, key="S3", layout=DS_IB),
]

__all__ = ["DS_CM", "DS_OB", "DS_IB", "SECTION_SLOTS"]
