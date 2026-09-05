"""Layouts for SMF 119 subtype 73 (IKE tunnel activation / refresh)."""
from __future__ import annotations

from ..layout import BYTES, CHAR, IPUNION, RES, U8, U16, U32, VAR_EBCDIC, build_layout
from ..registry import SectionSlot

IK_TN = build_layout(
    "SMF119IK_TN",
    [
        U16("SMF119IK_TNFlags", "IKE tunnel flags"),
        U8("SMF119IK_TNVersion", "IKE version"),
        U8("SMF119IK_TNAuth", "Authentication method"),
        U32("SMF119IK_TNLifeSec", "IKE lifetime (seconds)"),
        IPUNION("SMF119IK_TNLclIP", "Local tunnel endpoint"),
        IPUNION("SMF119IK_TNRmtIP", "Remote tunnel endpoint"),
        CHAR("SMF119IK_TNTunID", 48, "IKE tunnel ID"),
        CHAR("SMF119IK_TNVpn", 48, "VPN / policy name"),
        U8("SMF119IK_TNEncAlg", "Encryption algorithm"),
        U8("SMF119IK_TNIntAlg", "Integrity algorithm"),
        U8("SMF119IK_TNDhGrp", "DH group"),
        RES("SMF119IK_TNPad", 1),
        U32("SMF119IK_TNSTime", "Activation / refresh time of day"),
        BYTES("SMF119IK_TNSDate", 4, "Activation / refresh date", decode="date_hex"),
    ],
    description="SMF119IK_TN (IKETunnel)",
)

IK_ID = build_layout(
    "SMF119IK_ID",
    [
        VAR_EBCDIC("SMF119IK_IDStr", "IKE identity string"),
    ],
    description="SMF119IK_ID (variable length)",
    variable=True,
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=IK_TN),
    SectionSlot(triplet_index=2, key="S2", layout=IK_ID, optional=True),
]

__all__ = ["IK_TN", "IK_ID", "SECTION_SLOTS"]
