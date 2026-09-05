"""Layouts for SMF 119 subtype 49 (CSSMTP connection)."""
from __future__ import annotations

from ..layout import BYTES, CHAR, IPV6MAPPED, RES, U8, U16, U32, U64, build_layout
from ..registry import SectionSlot

ML_CI = build_layout(
    "SMF119ML_CI",
    [
        CHAR("SMF119ML_CI_JOB", 8, "CSSMTP job name"),
        U32("SMF119ML_CI_Entry", "JES reader entry time (1/100 s)"),
        BYTES("SMF119ML_CI_EDate", 4, "JES reader entry date", decode="date_hex"),
        CHAR("SMF119ML_CI_USEID", 8, "User-defined identification"),
        CHAR("SMF119ML_CI_EXTWRT", 8, "External writer name"),
        CHAR("SMF119ML_CI_Jes", 4, "JES subsystem name"),
    ],
    description="SMF119ML_CI",
)

ML_CN = build_layout(
    "SMF119ML_CN",
    [
        IPV6MAPPED("SMF119ML_CNRIP", "Remote (mail server) IP address"),
        IPV6MAPPED("SMF119ML_CNLIP", "Local IP address"),
        U16("SMF119ML_CNRPort", "Remote port"),
        U16("SMF119ML_CNLPort", "Local port"),
        U32("SMF119ML_CNConnID", "TCP connection ID"),
        U8("SMF119ML_CNEvent", "Connection event type"),
        RES("SMF119ML_CNPad", 3),
        CHAR("SMF119ML_CNHost", 64, "Mail server host name"),
    ],
    description="SMF119ML_CN",
)

ML_CS = build_layout(
    "SMF119ML_CS",
    [
        U8("SMF119ML_CSStatus", "Connection status"),
        U8("SMF119ML_CSSecure", "Security / TLS status"),
        RES("SMF119ML_CSPad", 2),
        U32("SMF119ML_CSSTime", "Status event time of day"),
        BYTES("SMF119ML_CSSDate", 4, "Status event date", decode="date_hex"),
        U64("SMF119ML_CSBytes", "Bytes transferred on connection"),
        CHAR("SMF119ML_CSReply", 4, "Last SMTP reply code"),
        CHAR("SMF119ML_CSReason", 32, "Status / failure reason text"),
    ],
    description="SMF119ML_CS",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=ML_CI),
    SectionSlot(triplet_index=2, key="S2", layout=ML_CN),
    SectionSlot(triplet_index=3, key="S3", layout=ML_CS),
]

__all__ = ["ML_CI", "ML_CN", "ML_CS", "SECTION_SLOTS"]
