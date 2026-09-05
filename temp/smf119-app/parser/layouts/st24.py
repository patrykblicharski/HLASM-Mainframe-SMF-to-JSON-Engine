"""Layouts for SMF 119 subtype 24 (TN3270E Telnet profile)."""
from __future__ import annotations

from ..layout import BYTES, CHAR, EYE, IPUNION, RES, U8, U16, U32, build_layout
from ..registry import SectionSlot, register_eye

# Eyecatchers (EBCDIC): TNPI, TNDS, TNTG, TNLU
EYE_TNPI = 0xE3D5D7C9
EYE_TNDS = 0xE3D5C4E2
EYE_TNTG = 0xE3D5E3C7
EYE_TNLU = 0xE3D5D3E4

TN_PI = build_layout(
    "SMF119TN_PI",
    [
        EYE("SMF119TN_PIEye", "TNPI eyecatcher"),
        U16("SMF119TN_PIFlags", "Profile information flags"),
        U8("SMF119TN_PIEvent", "Profile event type"),
        RES("SMF119TN_PIPad", 1),
        CHAR("SMF119TN_PIJob", 8, "Telnet server job name"),
        CHAR("SMF119TN_PIStack", 8, "TCP/IP stack name"),
        U32("SMF119TN_PIProfID", "Profile instance / record ID"),
        U16("SMF119TN_PIPort", "Telnet port number"),
        RES("SMF119TN_PIRsv", 2),
    ],
    description="SMF119TN_PI",
    eyecatcher=EYE_TNPI,
)

TN_DS = build_layout(
    "SMF119TN_DS",
    [
        EYE("SMF119TN_DSEye", "TNDS eyecatcher"),
        U16("SMF119TN_DSFlags", "DestIP / dataset section flags"),
        RES("SMF119TN_DSPad", 2),
        IPUNION("SMF119TN_DSAddr", "Destination / client IP"),
        U8("SMF119TN_DSPfxLen", "Prefix length"),
        RES("SMF119TN_DSRsv", 3),
        CHAR("SMF119TN_DSGroup", 8, "Parms / DestIP group name"),
        CHAR("SMF119TN_DSDsName", 44, "Profile data set name"),
    ],
    description="SMF119TN_DS",
    eyecatcher=EYE_TNDS,
)

TN_TG = build_layout(
    "SMF119TN_TG",
    [
        EYE("SMF119TN_TGEye", "TNTG eyecatcher"),
        U8("SMF119TN_TGFlag1", "TelnetGlobals flag byte 1"),
        U8("SMF119TN_TGFlag2", "TelnetGlobals flag byte 2"),
        U8("SMF119TN_TGFlag3", "TelnetGlobals flag byte 3"),
        U8("SMF119TN_TGFlag4", "TelnetGlobals flag byte 4"),
        CHAR("SMF119TN_TGTCPName", 8, "TCPIP job name"),
        U32("SMF119TN_TGSACacheTime", "TNSACONFIG CacheTime"),
        CHAR("SMF119TN_TGXCFSubplex", 8, "XCF Subplex name"),
        U32("SMF119TN_TGXCFMon", "XCFMonitor"),
        U32("SMF119TN_TGXCFConnTO", "XCF ConnectionTimeout"),
        U32("SMF119TN_TGXCFRcvyTO", "XCF RecoveryTimeout"),
        U16("SMF119TN_TGLUPort", "LUNS port"),
        RES("SMF119TN_TGPad", 2),
        IPUNION("SMF119TN_TGLUIpAddr", "LUNS IP address"),
    ],
    description="SMF119TN_TG",
    eyecatcher=EYE_TNTG,
)

TN_LU = build_layout(
    "SMF119TN_LU",
    [
        EYE("SMF119TN_LUEye", "TNLU eyecatcher"),
        U16("SMF119TN_LUFlags", "LU mapping flags"),
        RES("SMF119TN_LUPad", 2),
        CHAR("SMF119TN_LUName", 8, "LU name"),
        CHAR("SMF119TN_LUAppl", 8, "Application name"),
        CHAR("SMF119TN_LULogmode", 8, "Logmode"),
        CHAR("SMF119TN_LUGroup", 8, "LU group name"),
        IPUNION("SMF119TN_LUClientIP", "Client IP for LU mapping"),
        CHAR("SMF119TN_LUUser", 8, "Mapped user ID"),
    ],
    description="SMF119TN_LU",
    eyecatcher=EYE_TNLU,
)

register_eye(EYE_TNPI, TN_PI)
register_eye(EYE_TNDS, TN_DS)
register_eye(EYE_TNTG, TN_TG)
register_eye(EYE_TNLU, TN_LU)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=TN_PI),
    SectionSlot(triplet_index=2, key="S2", layout=TN_DS),
    SectionSlot(triplet_index=3, key="S3", layout=TN_TG),
    SectionSlot(triplet_index=4, key="S4", layout=TN_LU),
]

__all__ = ["TN_PI", "TN_DS", "TN_TG", "TN_LU", "SECTION_SLOTS"]
