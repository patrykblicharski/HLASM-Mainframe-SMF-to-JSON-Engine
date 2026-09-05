"""Auto-generated layouts for SMF 119 subtype 3 (from PACSYS offset tables)."""
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

FT_FC_S1 = build_layout(
    "SMF119FT_FC_S1",
    [
        CHAR("SMF119FT_FCCmd", 4, "FTP subcommand (according to RFC 959)"),
        CHAR("SMF119FT_FCFType", 4, "Local file type (SEQ, JES, or SQL)"),
        IPV6MAPPED("SMF119FT_FCDRIP", "Remote IP address (data connection)"),
        IPV6MAPPED("SMF119FT_FCDLIP", "Local IP address (data connection)"),
        U16("SMF119FT_FCDRPort", "Remote port number (data connection)"),
        U16("SMF119FT_FCDLPort", "Local port number (data connection)"),
        IPV6MAPPED("SMF119FT_FCCRIP", "Remote IP address (control connection)"),
        IPV6MAPPED("SMF119FT_FCCLIP", "Local IP address (control connection)"),
        U16("SMF119FT_FCCRPort", "Remote port number (control connection)"),
        U16("SMF119FT_FCCLPort", "Local port number (control connection)"),
        CHAR("SMF119FT_FCRUser", 8, "User ID (login name) on server"),
        CHAR("SMF119FT_FCLUser", 8, "Local User ID"),
        CHAR("SMF119FT_FCType", 1, "Data format A: ASCII E: EBCDIC I: Image B: Double-byte U: UCS-2"),
        CHAR("SMF119FT_FCMode", 1, "Transfer mode B: Block C: Compressed S: Stream"),
        CHAR("SMF119FT_FCStruct", 1, "Structure F: File R: Record"),
        CHAR("SMF119FT_FCDSType", 1, "Data set type S: SEQ P: PDS H: HFS"),
        U32("SMF119FT_FCSTime", "Transmission start time of day"),
        BYTES("SMF119FT_FCSDate", 4, "Transmission start date", decode="date_hex"),
        U32("SMF119FT_FCETime", "Transmission end time of day"),
        BYTES("SMF119FT_FCEDate", 4, "Transmission end date", decode="date_hex"),
        U32("SMF119FT_FCDur", "File transmission duration in units of 1/100 seconds"),
        U64("SMF119FT_FCBytes", "Transmission byte count; 64-bit integer"),
        CHAR("SMF119FT_FCLReply", 4, "Last server reply (3-digit RFC 959 code, left justified)"),
        CHAR("SMF119FT_FCM1", 8, "PDS member name"),
        CHAR("SMF119FT_FCHostname", 8, "Host name"),
        CHAR("SMF119FT_FCRS", 8, "Reserved for abnormal end info"),
        BYTES("SMF119FT_FCBytesFloat", 8, "point hex z/OS floating point format for transmission byte count", decode="hex"),
        U32("SMF119FT_FCCConnID", "TCP connection ID of FTP control connection"),
        U32("SMF119FT_FCDConnID", "TCP connection ID of FTP data connection, or 0 if no data connection is active"),
    ],
    description="SMF119FT_FC_S1",
)

FT_FCFileName_S2 = build_layout(
    "SMF119FT_FCFileName_S2",
    [
        VAR_EBCDIC("SMF119FT_FCFileName", "MVS or z/OS UNIX Data Set Name associated with the Rename file transfer operation. Use the \"Data Set Type\" field informa"),
    ],
    description="SMF119FT_FCFileName_S2 (variable length)",
    variable=True,
)

FT_FC_S3 = build_layout(
    "SMF119FT_FC_S3",
    [
        IPV6MAPPED("SMF119FT_FCCIP", "IP address of SOCKS server for control connection"),
        U16("SMF119FT_FCCPort", "SOCKS port number (control connection)"),
        U8("SMF119FT_FCCProt", "SOCKS protocol version (control connection) X'01' SOCKS Version 4 X'02' SOCKS Version 5"),
    ],
    description="SMF119FT_FC_S3",
)

FT_FC_S4 = build_layout(
    "SMF119FT_FC_S4",
    [
        CHAR("SMF119FT_FCMechanism", 1, "Protection Mechanism: N None T TLS G GSSAPI A AT-TLS"),
        CHAR("SMF119FT_FCCProtect", 1, "Control connection Protection Level: N None C Clear S Safe P Private"),
        CHAR("SMF119FT_FCDProtect", 1, "Data connection Protection Level: N None C Clear S Safe P Private"),
        CHAR("SMF119FT_FCLoginMech", 1, "Login Method: U Login method is not defined for the FTP client"),
        CHAR("SMF119FT_FCProtoLevel", 8, "Protocol level (only present if protocol mechanism is TLS or AT-TLS). Possible values are: * SSLV2 * SSLV3 * TLSV1"),
        CHAR("SMF119FT_FCCipherSpec", 20, "Cipher specification (only present if protocol mechanism is TLS or AT-TLS). Possible values when protocol level is SSLV2: * RC4 US * RC4 Export * RC2 US * RC2 Export * DES 56-Bit * Triple DES US Possible values when protocol level is SSLV3 "),
        U32("SMF119FT_FCProtBuffSize", "Negotiated protection buffer size"),
        CHAR("SMF119FT_FCCipher", 2, "Hexadecimal value of cipher specification (present only if protocol mechanism is TLS or AT-TLS)."),
    ],
    description="SMF119FT_FC_S4",
)

FT_FCUserID_S5 = build_layout(
    "SMF119FT_FCUserID_S5",
    [
        VAR_EBCDIC("SMF119FT_FCUserID", "User name or user ID used to log into the FTP server."),
    ],
    description="SMF119FT_FCUserID_S5 (variable length)",
    variable=True,
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key='S1', layout=FT_FC_S1),
    SectionSlot(triplet_index=2, key='S2', layout=FT_FCFileName_S2),
    SectionSlot(triplet_index=3, key='S3', layout=FT_FC_S3),
    SectionSlot(triplet_index=4, key='S4', layout=FT_FC_S4),
    SectionSlot(triplet_index=5, key='S5', layout=FT_FCUserID_S5),
]

__all__ = ['FT_FC_S1', 'FT_FCFileName_S2', 'FT_FC_S3', 'FT_FC_S4', 'FT_FCUserID_S5', "SECTION_SLOTS"]
