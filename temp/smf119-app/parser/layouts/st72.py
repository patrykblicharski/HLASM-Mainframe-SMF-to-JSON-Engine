"""Auto-generated layouts for SMF 119 subtype 72 (from PACSYS offset tables)."""
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

FT_FF_S1 = build_layout(
    "SMF119FT_FF_S1",
    [
        IPV6MAPPED("SMF119FT_FFRIP", "Remote IP address"),
        IPV6MAPPED("SMF119FT_FFLIP", "Local IP address"),
        U16("SMF119FT_FFRPort", "Remote port number (Client)"),
        U16("SMF119FT_FFLPort", "Local port number (Server)"),
        CHAR("SMF119FT_FFUserID", 8, "Client User ID received by server"),
        U8("SMF119FT_FFReason", "Login failure reason: '01'X Password is not valid. '02'X Password has expired. '03'X User ID has been revoked. '04'X User does not have server access. '05'X FTCHKPWD User exit reject login. '06'X Excessive bad passwords. '07'X Group ID proc"),
        RES("_rsv_45", 3),
        U32("SMF119FT_FFCConnID", "TCP connection ID of FTP control connection"),
        CHAR("SMF119FT_FFSessionID", 15, "FTP activity logging session ID. The activity logging session ID uniquely identifies the FTP session between a client and a server. The identifier is created by combining the job name of the FTP daemon with a 5-digit number in the range 000"),
    ],
    description="SMF119FT_FF_S1",
)

FT_FF_S2 = build_layout(
    "SMF119FT_FF_S2",
    [
        CHAR("SMF119FT_FFMechanism", 1, "Protection Mechanism N None T TLS G GSSAPI A AT-TLS"),
        CHAR("SMF119FT_FFCProtect", 1, "Control Connection Protection Level N None C Clear S Safe P Private"),
        CHAR("SMF119FT_FFDProtect", 1, "Data connection protection level N None C Clear S Safe P Private"),
        CHAR("SMF119FT_FFLoginMech", 1, "Login Method P Password C Certificate - Login failure occurred before login method was determined. T Kerberos ticket"),
        CHAR("SMF119FT_FFProtoLevel", 8, "Protocol level (present only if Protocol Mechanism is TLS or AT-TLS) Possible values are: * SSLV2 * SSLV3 * TLSV1"),
        CHAR("SMF119FT_FFCipherSpec", 20, "Cipher specification (only present if protocol mechanism is TLS or AT-TLS) Possible values when protocol level is SSLV2: * RC4 US * RC4 Export * RC2 US * RC2 Export * DES 56-Bit * Triple DES US Possible values when protocol level is SSLV3 o"),
        U32("SMF119FT_FFProtBuffSize", "Negotiated protection buffer size"),
        CHAR("SMF119FT_FFCipher", 2, "Hexadecimal value of cipher specification ( present only if protocol mechanism is TLS or AT-TLS."),
    ],
    description="SMF119FT_FF_S2",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key='S1', layout=FT_FF_S1),
    SectionSlot(triplet_index=2, key='S2', layout=FT_FF_S2),
]

__all__ = ['FT_FF_S1', 'FT_FF_S2', "SECTION_SLOTS"]
