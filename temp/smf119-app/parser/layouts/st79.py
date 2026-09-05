"""Layouts for SMF 119 subtype 79 (Manual tunnel activation)."""
from __future__ import annotations

from ..layout import BYTES, CHAR, IPUNION, RES, U8, U16, U32, VAR_EBCDIC, build_layout
from ..registry import SectionSlot

IP_TN = build_layout(
    "SMF119IP_TN",
    [
        U16("SMF119IP_TNFlags", "IP tunnel flags"),
        U8("SMF119IP_TNType", "Tunnel type"),
        U8("SMF119IP_TNMode", "Tunnel mode (transport/tunnel)"),
        IPUNION("SMF119IP_TNLclIP", "Local tunnel endpoint"),
        IPUNION("SMF119IP_TNRmtIP", "Remote tunnel endpoint"),
        CHAR("SMF119IP_TNTunID", 48, "IP tunnel ID"),
        U8("SMF119IP_TNEncAlg", "Encryption algorithm"),
        U8("SMF119IP_TNIntAlg", "Integrity / auth algorithm"),
        U8("SMF119IP_TNProto", "Encapsulating protocol (ESP/AH)"),
        RES("SMF119IP_TNPad", 1),
        U32("SMF119IP_TNSpiIn", "Inbound SPI"),
        U32("SMF119IP_TNSpiOut", "Outbound SPI"),
        U32("SMF119IP_TNSTime", "Event time of day"),
        BYTES("SMF119IP_TNSDate", 4, "Event date", decode="date_hex"),
    ],
    description="SMF119IP_TN (IPTunnel)",
)

IP_MT = build_layout(
    "SMF119IP_MT",
    [
        U16("SMF119IP_MTFlags", "Manual tunnel flags"),
        RES("SMF119IP_MTPad", 2),
        CHAR("SMF119IP_MTTunID", 48, "Manual tunnel ID"),
        IPUNION("SMF119IP_MTLclIP", "Local endpoint"),
        IPUNION("SMF119IP_MTRmtIP", "Remote endpoint"),
        U32("SMF119IP_MTSpiIn", "Inbound SPI"),
        U32("SMF119IP_MTSpiOut", "Outbound SPI"),
        U8("SMF119IP_MTEncAlg", "Encryption algorithm"),
        U8("SMF119IP_MTIntAlg", "Integrity algorithm"),
        RES("SMF119IP_MTRsv", 2),
        U32("SMF119IP_MTSTime", "Event time of day"),
        BYTES("SMF119IP_MTSDate", 4, "Event date", decode="date_hex"),
    ],
    description="SMF119IP_MT (Manual tunnel)",
)

IP_ID = build_layout(
    "SMF119IP_ID",
    [
        VAR_EBCDIC("SMF119IP_IDStr", "Tunnel / identity string"),
    ],
    description="SMF119IP_ID (variable length)",
    variable=True,
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=IP_TN),
    SectionSlot(triplet_index=2, key="S2", layout=IP_MT),
    SectionSlot(triplet_index=3, key="S3", layout=IP_ID, optional=True),
]

__all__ = ["IP_TN", "IP_MT", "IP_ID", "SECTION_SLOTS"]
