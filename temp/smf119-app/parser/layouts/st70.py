"""Auto-generated layouts for SMF 119 subtype 70 (from PACSYS offset tables)."""
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

FT_FS_S1 = build_layout(
    "SMF119FT_FS_S1",
    [
        U8("SMF119FT_FSOper", "FTP Operation according to SMF77 subtype classification: x'01': Append x'02': Delete x'03': Rename x'04': Retrieve x'05': Store x'06': Store Unique"),
        RES("_rsv_1", 3),
        CHAR("SMF119FT_FSCmd", 4, "FTP command (according to RFC 959+)"),
        CHAR("SMF119FT_FSFType", 4, "File type (SEQ, JES, or SQL)"),
        IPV6MAPPED("SMF119FT_FSDRIP", "Remote IP address (data connection)"),
        IPV6MAPPED("SMF119FT_FSDLIP", "Local IP address (data connection)"),
        U16("SMF119FT_FSDRPort", "Remote port number (data connection - client)"),
        U16("SMF119FT_FSDLPort", "Local port number (data connection - server)"),
        IPV6MAPPED("SMF119FT_FSCRIP", "Remote IP address (control connection)"),
        IPV6MAPPED("SMF119FT_FSCLIP", "Local IP address (control connection)"),
        U16("SMF119FT_FSCRPort", "Remote port number (control connection - client)"),
        U16("SMF119FT_FSCLPort", "Local port number (control connection - server)"),
        CHAR("SMF119FT_FSSUser", 8, "Client User ID on server"),
        CHAR("SMF119FT_FSType", 1, "Data type: A: ASCII E: EBCDIC I: Image B: Double-byte U: UCS-2"),
        CHAR("SMF119FT_FSMode", 1, "Transmission mode B: Block C: Compressed S: Stream"),
        CHAR("SMF119FT_FSStruct", 1, "Data structure F: File R: Record"),
        CHAR("SMF119FT_FSDsType", 1, "Data set type S: SEQ P: PDS H: HFS"),
        U32("SMF119FT_FSSTime", "Transmission start time of day"),
        BYTES("SMF119FT_FSSDate", 4, "Transmission start date", decode="date_hex"),
        U32("SMF119FT_FSETime", "Transmission end time of day"),
        BYTES("SMF119FT_FSEDate", 4, "Transmission end date", decode="date_hex"),
        U32("SMF119FT_FSDur", "File transmission duration in units of 1/100 seconds"),
        U64("SMF119FT_FSBytes", "Transmission byte count; 64-bit integer"),
        CHAR("SMF119FT_FSLReply", 4, "Last reply to client (3-digit RFC 959 code, right justified)"),
        CHAR("SMF119FT_FSM1", 8, "PDS Member name"),
        CHAR("SMF119FT_FSRS", 8, "Reserved for abnormal end information"),
        CHAR("SMF119FT_FSM2", 8, "Second PDS member name (if rename operation)"),
        BYTES("SMF119FT_FSBytesFloat", 8, "point hex z/OS floating point format for transmission byte count", decode="hex"),
        U32("SMF119FT_FSCConnID", "TCP connection ID of FTP control connection"),
        U32("SMF119FT_FSDConnID", "TCP connection ID of FTP data connection, or 0"),
        CHAR("SMF119FT_FSSessionID", 15, "FTP activity logging session ID. The activity logging session ID uniquely identifies the FTP session between a client and a server. The identifier is created by combining the job name of the FTP daemon with a 5-digit number in the range 000"),
        RES("_rsv_183", 1),
    ],
    description="SMF119FT_FS_S1",
)

FT_FSHostname_S2 = build_layout(
    "SMF119FT_FSHostname_S2",
    [
        VAR_EBCDIC("SMF119FT_FSHostname", "Host Name"),
    ],
    description="SMF119FT_FSHostname_S2 (variable length)",
    variable=True,
)

FT_FSFileName1_S3 = build_layout(
    "SMF119FT_FSFileName1_S3",
    [
        VAR_EBCDIC("SMF119FT_FSFileName1", "Server MVS or z/OS UNIX file name associated with the file transfer or rename operation. When the operation is a rename,"),
    ],
    description="SMF119FT_FSFileName1_S3 (variable length)",
    variable=True,
)

FT_FSFileName2_S4 = build_layout(
    "SMF119FT_FSFileName2_S4",
    [
        VAR_EBCDIC("SMF119FT_FSFileName2", "Second MVS or z/OS UNIX file name associated with a rename. This is the new file or data set name."),
    ],
    description="SMF119FT_FSFileName2_S4 (variable length)",
    variable=True,
)

FT_FS_S5 = build_layout(
    "SMF119FT_FS_S5",
    [
        CHAR("SMF119FT_FSMechanism", 1, "Protection Mechanism N None T TLS G GSSAPI A AT-TLS"),
        CHAR("SMF119FT_FSCProtect", 1, "Control connection protection level N None C Clear S Safe P Private"),
        CHAR("SMF119FT_FSDProtect", 1, "Data connection Protection Level N None C Clear S Safe P Private"),
        CHAR("SMF119FT_FSLoginMech", 1, "Login Method P Password C Certificate T Kerberos ticket"),
        CHAR("SMF119FT_FSProtoLevel", 8, "Protocol level (only present if Protocol Mechanism is TLS or AT-TLS) Possible values are: * SSLV2 * SSLV3 * TLSV1"),
        CHAR("SMF119FT_FSCipherSpec", 20, "Cipher Specification (only present if Protocol Mechanism is TLS or AT-TLS). Possible values when Protocol Level is SSLV2: * RC4 US * RC4 Export * RC2 US * RC2 Export * DES 56-Bit * Triple DES US Possible values when Protocol Level is SSLV3 "),
        U32("SMF119FT_FSProtoBufSize", "Negotiated protection buffer size"),
        CHAR("SMF119FT_FSCipher", 2, "Hexadecimal value of cipher specification (present only when Protocol Mechanism is TLS or AT-TLS)."),
    ],
    description="SMF119FT_FS_S5",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key='S1', layout=FT_FS_S1),
    SectionSlot(triplet_index=2, key='S2', layout=FT_FSHostname_S2),
    SectionSlot(triplet_index=3, key='S3', layout=FT_FSFileName1_S3),
    SectionSlot(triplet_index=4, key='S4', layout=FT_FSFileName2_S4),
    SectionSlot(triplet_index=5, key='S5', layout=FT_FS_S5),
]

__all__ = ['FT_FS_S1', 'FT_FSHostname_S2', 'FT_FSFileName1_S3', 'FT_FSFileName2_S4', 'FT_FS_S5', "SECTION_SLOTS"]
