"""Layouts for SMF 119 subtype 71 (FTP daemon configuration)."""
from __future__ import annotations

from ..layout import CHAR, EYE, RES, U8, U16, U32, VAR_EBCDIC, build_layout
from ..registry import SectionSlot, register_eye

# Eyecatchers (EBCDIC): FDID, FDCF
EYE_FDID = 0xC6C4C9C4
EYE_FDCF = 0xC6C4C3C6

FD_ID = build_layout(
    "SMF119FD_ID",
    [
        EYE("SMF119FD_IDEye", "FDID eyecatcher"),
        U16("SMF119FD_IDFlags", "FTPD identity flags"),
        RES("SMF119FD_IDPad", 2),
        CHAR("SMF119FD_IDJob", 8, "FTP daemon job name"),
        CHAR("SMF119FD_IDStack", 8, "TCP/IP stack name"),
        U32("SMF119FD_IDASID", "Address space ID"),
        CHAR("SMF119FD_IDUser", 8, "FTP daemon user ID"),
    ],
    description="SMF119FD_ID",
    eyecatcher=EYE_FDID,
)

FD_CF = build_layout(
    "SMF119FD_CF",
    [
        EYE("SMF119FD_CFEye", "FDCF eyecatcher"),
        U16("SMF119FD_CFFlags", "FTPD configuration flags"),
        U8("SMF119FD_CFEvent", "Configuration event type"),
        RES("SMF119FD_CFPad", 1),
        U16("SMF119FD_CFPort", "FTP control port"),
        U16("SMF119FD_CFItems", "Number of configuration items"),
        CHAR("SMF119FD_CFDsName", 44, "FTP.DATA data set name"),
    ],
    description="SMF119FD_CF",
    eyecatcher=EYE_FDCF,
)

FD_CI = build_layout(
    "SMF119FD_CI",
    [
        VAR_EBCDIC("SMF119FD_CIText", "FTP.DATA configuration item text"),
    ],
    description="SMF119FD_CI (variable length)",
    variable=True,
)

register_eye(EYE_FDID, FD_ID)
register_eye(EYE_FDCF, FD_CF)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=FD_ID),
    SectionSlot(triplet_index=2, key="S2", layout=FD_CF),
    SectionSlot(triplet_index=3, key="S3", layout=FD_CI),
]

__all__ = ["FD_ID", "FD_CF", "FD_CI", "SECTION_SLOTS"]
