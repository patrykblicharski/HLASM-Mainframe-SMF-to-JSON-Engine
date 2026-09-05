"""Auto-generated layouts for SMF 119 subtype 21 (from PACSYS offset tables)."""
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

TN_NT_S1 = build_layout(
    "SMF119TN_NT_S1",
    [
        CHAR("SMF119TN_NTLU", 8, "Telnet LU name"),
        CHAR("SMF119TN_NTAppl", 8, "Host application name"),
        U32("SMF119TN_NTLdev", "Telnet internal logical device number"),
        IPV6MAPPED("SMF119TN_NTRIP", "Remote (client) IP address"),
        IPV6MAPPED("SMF119TN_NTLIP", "Local (Telnet) IP address"),
        U16("SMF119TN_NTRPort", "Remote (client) port number"),
        U16("SMF119TN_NTLPort", "Local (Telnet) port number"),
        CHAR("SMF119TN_NTHostNm", 8, "TCP/IP Host name"),
        U64("SMF119TN_NTInByte", "Inbound byte count"),
        U64("SMF119TN_NTOutByte", "Outbound byte count"),
        U32("SMF119TN_NTiTime", "Time of session initiation"),
        BYTES("SMF119TN_NTiDate", 4, "Date of session initiation", decode="date_hex"),
        U32("SMF119TN_NTtTime", "Time of session termination"),
        BYTES("SMF119TN_NTtDate", 4, "Date of session termination", decode="date_hex"),
        U32("SMF119TN_NTDur", "Session duration in units of 1/100 seconds"),
        U8("SMF119TN_NTSType", "Telnet session type: 0 UNKNOWN 1 TN3270 2 TN3270E 3 LINEMODE 4 DBCSTRANSFORM 5 BINARY"),
        U8("SMF119TN_NTLUSel", "Telnet LU selection method: 0 LU chosen by server 1 LU requested by client"),
        U8("SMF119TN_NTSSL", "SSL status: 0 No SSL session 1 Server authentication only 2 Server and client authentication (REQUIRED/SSLCERT): * If AT-TLS policy (REQUIRED), then check SAF, and user ID is not required to be returned. * If TN profile control (SSLCERT), t"),
        RES("_rsv_103", 1),
        U8("SMF119TN_NTCopt", "Telnet connection options negotiated for this connection: * 1000 0000 TN3270E * 0100 0000 Terminal type * 0010 0000 End of Record * 0001 0000 Transmit binary * 0000 1000 Echos * 0000 0100 Suppress go ahead * 0000 0010 Timemark * 0000 0001 N"),
        RES("_rsv_105", 1),
        U16("SMF119TN_NT32opt", "TN3270E connection options negotiated for this connection. First Byte: * 1000 0000 Bind image * 0100 0000 SysRequest * 0010 0000 Responses * 0001 0000 SCS control codes * 0000 1000 DCS control codes * 0000 0100 Contention Resolution * 0000 "),
        CHAR("SMF119TN_NTRCode", 8, "Session termination reason code. The values in this field are the same as those displayed in message EZZ6034I as value for the object variable."),
        CHAR("SMF119TN_NTLMode", 8, "SNA logmode"),
        CHAR("SMF119TN_NTDevt", 20, "Telnet device type"),
    ],
    description="SMF119TN_NT_S1",
)

TN_NT_S2 = build_layout(
    "SMF119TN_NT_S2",
    [
        VAR_EBCDIC("SMF119TN_NTHostname", "Host name associated with this session"),
    ],
    description="SMF119TN_NT_S2 (variable length)",
    variable=True,
)

TN_NTR_S3 = build_layout(
    "SMF119TN_NTR_S3",
    [
        U32("SMF119TN_NTRRts", "Sum of round trip times for this session in milliseconds"),
        U32("SMF119TN_NTRIPRts", "Sum of IP portion of round trip times for this session in milliseconds"),
        U32("SMF119TN_NTRCountTrans", "Count of transactions used to measure round trip times for this session"),
        IPV4("SMF119TN_NTRCountIP", "Count of IP transactions used to measure the IP portion of the round trip time"),
        U64("SMF119TN_NTRElapsRndTrpSq", "The sum of the square of each round trip time"),
        U64("SMF119TN_NTRElapsIpRtSq", "The sum of the square of each IP portion of round trip time"),
        U64("SMF119TN_NTRElapsSnaRtSq", "The sum of the square of each SNA portion of round trip time"),
        U32("SMF119TN_NTRGrpIndex", "The index into the master MonitorGroup table this connection is using"),
        U8("SMF119TN_NTRDR", "Indicator how IP trip time is measured: '80'x Definite Response used '40'x Timemark used"),
        RES("_rsv_45", 3),
    ],
    description="SMF119TN_NTR_S3",
)

TN_NTB_S4 = build_layout(
    "SMF119TN_NTB_S4",
    [
        U32("SMF119TN_NTBucketBndry1", "Upper boundary for bucket 1 in milliseconds"),
        U32("SMF119TN_NTBucketBndry2", "Upper boundary for bucket 2 in milliseconds"),
        U32("SMF119TN_NTBucketBndry3", "Upper boundary for bucket 3 in milliseconds"),
        U32("SMF119TN_NTBucketBndry4", "Upper boundary for bucket 4 in milliseconds"),
        U32("SMF119TN_NTBucket1Rts", "Number of transactions with a round trip time meeting bucket 1 criteria"),
        U32("SMF119TN_NTBucket2Rts", "Number of transactions with a round trip time meeting bucket 2 criteria"),
        U32("SMF119TN_NTBucket3Rts", "Number of transactions with round trip time meeting bucket 3 criteria"),
        U32("SMF119TN_NTBucket4Rts", "Number of transactions with a round trip time meeting bucket 4 criteria"),
        U32("SMF119TN_NTBucket5Rts", "Number of transactions with a round trip time that exceeds bucket 4 time"),
    ],
    description="SMF119TN_NTB_S4",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key='S1', layout=TN_NT_S1),
    SectionSlot(triplet_index=2, key='S2', layout=TN_NT_S2, optional=True),
    SectionSlot(triplet_index=3, key='S3', layout=TN_NTR_S3, optional=True),
    SectionSlot(triplet_index=4, key='S4', layout=TN_NTB_S4, optional=True),
]

__all__ = ['TN_NT_S1', 'TN_NT_S2', 'TN_NTR_S3', 'TN_NTB_S4', "SECTION_SLOTS"]
