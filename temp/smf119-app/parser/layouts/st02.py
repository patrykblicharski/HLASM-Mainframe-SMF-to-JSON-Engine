"""Auto-generated layouts for SMF 119 subtype 2 (from PACSYS offset tables)."""
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

AP_TT_S1 = build_layout(
    "SMF119AP_TT_S1",
    [
        CHAR("SMF119AP_TTRName", 8, "TCP socket resource name (Address space name of address space that closed this TCP connection)"),
        U32("SMF119AP_TTConnID", "TCP socket resource ID (connection ID)"),
        U8("SMF119AP_TTTTLSCS", "AT-TLS connection status: * x'01': Connection is not secure * x'02': Connection handshake in progress * x'03': Connection is secure"),
        U8("SMF119AP_TTTTLSPS", "AT-TLS Policy Status: * x'00': Policy status is not known * x'01': AT-TLS function off * x'02': No policy defined for connection * x'03': Policy defined for connection; AT-TLS not enabled * x'04': Policy defined for connection; AT-TLS enabl"),
        U8("SMF119AP_TTTermCode", "Reason code for connection termination: * x'11': Error occurred during a send using FRCA(AFPA), possibly because the stack is terminating. * x'12': A persistent socket used by FRCA (AFPA) was closed by a FIN. * x'21': The connection was ter"),
        U8("SMF119AP_TTRsv2", "Reserved"),
        U32("SMF119AP_TTSubtask", "Subtask Name (Address of MVS™ TCB for the task that owns this connection. This is not the subtask value specified on an INITAPI call.)"),
        U32("SMF119AP_TTSTime", "Time of connection establishment"),
        BYTES("SMF119AP_TTSDate", 4, "Date of connection establishment", decode="date_hex"),
        U32("SMF119AP_TTETime", "Time connection entered TIMEWAIT or LASTACK state."),
        BYTES("SMF119AP_TTEDate", 4, "Date connection entered TIMEWAIT or LASTACK state.", decode="date_hex"),
        IPV6MAPPED("SMF119AP_TTRIP", "Remote IP address at time of connection close."),
        IPV6MAPPED("SMF119AP_TTLIP", "Local IP address at time of connection close."),
        U16("SMF119AP_TTRPort", "Remote port number at time of connection close."),
        U16("SMF119AP_TTLPort", "Local port number at time of connection close."),
        U64("SMF119AP_TTInBytes", "Inbound byte count."),
        U64("SMF119AP_TTOutBytes", "Outbound byte count."),
        U32("SMF119AP_TTSWS", "Send window size at time of connection close."),
        U32("SMF119AP_TTMSWS", "Maximum send window size."),
        U32("SMF119AP_TTCWS", "Congestion window size at time of connection close."),
        U32("SMF119AP_TTSMS", "Send segment size at time of connection close."),
        U32("SMF119AP_TTRTT", "Round trip time in milliseconds at time of connection close.`"),
        U32("SMF119AP_TTRVA", "Round trip time variance estimator at time of connection close, in milliseconds."),
        U8("SMF119AP_TTStatus", "Socket status: * x'00': Passive Open (this is a server socket) * x'01': Active Open (this is a client socket)"),
        U8("SMF119AP_TTTOS", "Type of Service (ToS) used by this connection."),
        U16("SMF119AP_TTXRT", "Number of times retransmission was required for this connection."),
        CHAR("SMF119AP_TTProf", 32, "Service profile name."),
        CHAR("SMF119AP_TTPol", 32, "Service Policy name at the time of connection close."),
        U64("SMF119AP_TTInSeg", "Inbound segment count."),
        U64("SMF119AP_TTOutSeg", "Outbound segment count."),
        U64("SMF119AP_TTSSTCK_D", "MVS TOD clock value at time of connection establishment."),
        U64("SMF119AP_TTESTCK_D", "MVS TOD clock value at time connection entered TIMEWAIT or LASTACK state."),
        U32("SMF119AP_TTDupAcksRcvd", "Total Number of DUP ACKs received on the connection."),
    ],
    description="SMF119AP_TT_S1",
)

AP_TTTel_S2 = build_layout(
    "SMF119AP_TTTel_S2",
    [
        CHAR("SMF119AP_TTTelLUName", 8, "LU name"),
        CHAR("SMF119AP_TTTelAppl", 8, "Target application name"),
        CHAR("SMF119AP_TTTelLogmode", 8, "Logmode name"),
        U32("SMF119AP_TTTelStatus", "Status word: * x80000000 Definite response mode * x40000000 The connection is being performance monitored * x00000004 TN3270E mode * x00000002 TN3270 mode * x00000001 Line mode"),
        U8("SMF119AP_TTTelTermCode", "Reason code for closing connection. The socket must be accessible to the TN3270 server to record a reason. (for example, SMF119AP_TTTermCode for this record is x'52'.) See the description of EZZ6034I for a list of reason codes and their des"),
        BYTES("SMF119AP_TTTelRsv", 3, "Reserved"),
    ],
    description="SMF119AP_TTTel_S2",
)

AP_TTTTLS_S3 = build_layout(
    "SMF119AP_TTTTLS_S3",
    [
        U16("SMF119AP_TTTTLSSP", "AT-TLS SSL Protocol: * x'0200': SSL Version 2 * x'0300': SSL Version 3 * x'0301': AT-TLS Version 1"),
        CHAR("SMF119AP_TTTTLSNC", 2, "AT-TLS Negotiated Cipher"),
        U8("SMF119AP_TTTTLSST", "AT-TLS Security Type: * x'01': Client * x'02': Server * x'03': Server with client authentication, ClientAuthType = PassThru * x'04': Server with client authentication, ClientAuthType = Full * x'05': Server with client authentication, Client"),
        BYTES("SMF119AP_TTTTLSRSV1", 3, "Reserved"),
        CHAR("SMF119AP_TTTTLSUID", 8, "AT-TLS Partner UserID"),
    ],
    description="SMF119AP_TTTTLS_S3",
)

AP_TTAPPL_S4 = build_layout(
    "SMF119AP_TTAPPL_S4",
    [
        CHAR("SMF119AP_TTAPPLDATA", 40, "For z/OS Communications Server applications, see Appendix E. Application data for an explanation of the layout, format, and meaning of"),
    ],
    description="SMF119AP_TTAPPL_S4",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key='S1', layout=AP_TT_S1),
    SectionSlot(triplet_index=2, key='S2', layout=AP_TTTel_S2, optional=True),
    SectionSlot(triplet_index=3, key='S3', layout=AP_TTTTLS_S3, optional=True),
    SectionSlot(triplet_index=4, key='S4', layout=AP_TTAPPL_S4, optional=True),
]

__all__ = ['AP_TT_S1', 'AP_TTTel_S2', 'AP_TTTTLS_S3', 'AP_TTAPPL_S4', "SECTION_SLOTS"]
