"""NMTP profile section layouts from ezbnmmpc.h (SMF 119 subtype 4).

Field names and packed sizes follow IBM z/OS Communications Server
mapping header EZBNMMPC (ZCSV2R5). Layouts are independent re-expressions
for offline decoding — not a redistributed IBM header.
"""
from __future__ import annotations

from .layout import (
    BYTES,
    CHAR,
    EYE,
    IPUNION,
    IPV4,
    IPV6,
    I16,
    I32,
    RES,
    U8,
    U16,
    U32,
    StructLayout,
    build_layout,
)

# Eyecatcher constants (EBCDIC four-character ids as big-endian u32)
EYE_PICO = 0xD7C9C3D6
EYE_PIDS = 0xD7C9C4E2
EYE_ALPR = 0xC1D3D7D9
EYE_V4CF = 0xE5F4C3C6
EYE_V6CF = 0xE5F6C3C6
EYE_TCCF = 0xE3C3C3C6
EYE_UDCF = 0xE4C4C3C6
EYE_GBCF = 0xC7C2C3C6
EYE_PORT = 0xD7D6D9E3
EYE_INTF = 0xC9D5E3C6
EYE_IPA6 = 0xC9D7C1F6
EYE_ROUT = 0xD9D6E4E3
EYE_SRCI = 0xE2D9C3C9
EYE_MGMT = 0xD4C7D4E3
EYE_IPSC = 0xC9D7E2C3
EYE_IPSR = 0xC9D7E2D9
EYE_NETA = 0xD5C5E3C1
EYE_DVCF = 0xC4E5C3C6
EYE_DVRT = 0xC4E5D9E3
EYE_DDVS = 0xC4C4E5E2
EYE_DASP = 0xC4C1E2D7
EYE_FLTP = 0xC6D3E3D7
EYE_FLTE = 0xC6D3E3C5

NMTP_PICommon = build_layout(
    "NMTP_PICommon",
    [
        EYE("NMTP_PICOEye"),
        BYTES("NMTP_PICOStartTime", 8, "Stack start time", decode="tod_hex"),
        BYTES("NMTP_PICOStartDate", 4, "Stack start date", decode="date_hex"),
        BYTES("NMTP_PICOChangeTime", 8, "Last change time", decode="tod_hex"),
        BYTES("NMTP_PICOChangeDate", 4, "Last change date", decode="date_hex"),
        U8(
            "NMTP_PICOChangeRsn",
            "Change reason",
            enum={0: "none/NMI", 1: "OBEYFILE"},
        ),
        U8(
            "NMTP_PICOFlags",
            "Miscellaneous flags",
            flags={0x80: "PROFCOMPLETE"},
        ),
        RES("NMTP_PICOResv1", 2),
        U16(
            "NMTP_PICODepStmts",
            "Deprecated statements in initial profile",
            flags={
                0x8000: "INTF",
                0x4000: "HOME",
                0x2000: "ROUTE",
                0x1000: "SMF",
                0x0800: "TRANSLATE",
                0x0400: "VIPASMPARMS",
            },
        ),
        U16(
            "NMTP_PICODepChanged",
            "Deprecated statements in last change",
            flags={
                0x8000: "INTF",
                0x4000: "HOME",
                0x2000: "ROUTE",
                0x1000: "SMF",
                0x0800: "TRANSLATE",
                0x0400: "VIPASMPARMS",
            },
        ),
        U32(
            "NMTP_PICOSecChanged",
            "Sections changed",
            flags={
                0x80000000: "AUTOLOG",
                0x40000000: "V4CFG",
                0x20000000: "V6CFG",
                0x10000000: "TCPCFG",
                0x08000000: "UDPCFG",
                0x04000000: "GBLCFG",
                0x02000000: "PORT",
                0x01000000: "INTF",
                0x00800000: "IPA6",
                0x00400000: "ROUTE",
                0x00200000: "SRCIP",
                0x00100000: "MGMT",
                0x00080000: "IPSECCM",
                0x00040000: "IPSECRULES",
                0x00020000: "NETACC",
                0x00010000: "DASP",
                0x00008000: "DVCFG",
                0x00004000: "DVROUTE",
                0x00002000: "DISTDV",
                0x00001000: "FLTP",
                0x00000800: "FLTE",
            },
        ),
        CHAR("NMTP_PICOConsName", 8, "Console name"),
        CHAR("NMTP_PICOSysplexGrpName", 8, "Sysplex group name"),
        BYTES("NMTP_PICOUserToken", 80, "Security user token", decode="hex"),
    ],
    description="Profile Information Common",
    eyecatcher=EYE_PICO,
)

NMTP_PIDS = build_layout(
    "NMTP_PIDS",
    [
        EYE("NMTP_PIDSEye"),
        U8(
            "NMTP_PIDSFlag",
            "Data set flags",
            flags={0x80: "CHANGE", 0x40: "INCLUDE"},
        ),
        RES("NMTP_PIDSResv1", 1),
        CHAR("NMTP_PIDSName", 54, "Data set name"),
    ],
    description="Profile Information Data Set Name",
    eyecatcher=EYE_PIDS,
)

NMTP_ALPROC = build_layout(
    "NMTP_ALPROC",
    [
        EYE("NMTP_ALPREye"),
        CHAR("NMTP_ALPRName", 8, "Procedure name"),
        CHAR("NMTP_ALPRJobName", 8, "Job name"),
        U16(
            "NMTP_ALPROptions",
            "Options",
            flags={0x8000: "DELAYDVIPA", 0x4000: "DELAYTTLS"},
        ),
        RES("NMTP_ALPRResv1", 2),
        CHAR("NMTP_ALPRParmStr", 115, "Parameter string"),
        U8("NMTP_ALPRWaitTime", "Wait time"),
    ],
    description="Autolog Procedure",
    eyecatcher=EYE_ALPR,
)

NMTP_V4CFG = build_layout(
    "NMTP_V4CFG",
    [
        EYE("NMTP_V4CFEye"),
        U32(
            "NMTP_V4CFFlags",
            "IPv4 config flags",
            flags={
                0x80000000: "CLAWUSEDOUBLENOP",
                0x40000000: "DATAGRAMFWD",
                0x20000000: "FWDMULTIPPKT",
                0x10000000: "DYNAMICXCF",
                0x08000000: "FORMATLONG",
                0x04000000: "IGNREDIRECTCFG",
                0x02000000: "IGNREDIRECTACT",
                0x01000000: "IPSECURITY",
                0x00800000: "IQDIOROUTING",
                0x00400000: "MULTIPPERCONN",
                0x00200000: "MULTIPPERPKT",
                0x00100000: "PATHMTUDISC",
                0x00080000: "SOURCEVIPA",
                0x00040000: "STOPCLAWERR",
                0x00020000: "SYSPLEXROUTING",
                0x00010000: "TCPSOURCEVIPA",
                0x00008000: "QDIOACC",
                0x00004000: "CHKOFFLOAD",
                0x00002000: "SEGOFFLOAD",
                0x00001000: "DYNXCFSRCVIPAIFNAME",
                0x00000800: "DYNXCFSMCD",
            },
        ),
        I32("NMTP_V4CFArpTimeout", "ARP cache timeout (seconds)"),
        U32("NMTP_V4CFDevRetry", "Device retry duration (seconds)"),
        IPV4("NMTP_V4CFTcpSrcVipaAddr", "TCP source VIPA"),
        IPV4("NMTP_V4CFDynXcfAddr", "Dynamic XCF IP"),
        U8("NMTP_V4CFDynXcfCostMetric", "Dynamic XCF cost metric"),
        U8("NMTP_V4CFDynXcfMask", "Dynamic XCF mask bits"),
        U8("NMTP_V4CFDynXcfSecClass", "Dynamic XCF security class"),
        U8("NMTP_V4CFQDIOPriority", "QDIO priority"),
        U8(
            "NMTP_V4CFIgnRedirectRsn",
            "Ignore redirect reason",
            enum={1: "CFG", 2: "OMP", 3: "IDS"},
        ),
        U8("NMTP_V4CFReasmTimeout", "Reassembly timeout (seconds)"),
        U8("NMTP_V4CFTTL", "Time to live"),
        RES("NMTP_V4CFResv", 1),
        CHAR("NMTP_V4CFPrimaryIntfName", 16, "Primary interface name"),
        CHAR("NMTP_V4CFDynXcfSrcVipaIntfName", 16, "Dyn XCF src VIPA intf"),
    ],
    description="IPv4 Configuration",
    eyecatcher=EYE_V4CF,
)

NMTP_V6CFG = build_layout(
    "NMTP_V6CFG",
    [
        EYE("NMTP_V6CFEye"),
        U32(
            "NMTP_V6CFFlags",
            "IPv6 config flags",
            flags={
                0x80000000: "DATAGRAMFWD",
                0x40000000: "FWDMULTIPPKT",
                0x20000000: "DYNAMICXCF",
                0x10000000: "DYNXCFIFID",
                0x08000000: "DYNXCFSRCVIPAIFNAME",
                0x04000000: "IGNREDIRECTCFG",
                0x02000000: "IGNREDIRECTACT",
                0x01000000: "IGNORERTRHOPLIMIT",
                0x00800000: "IPSECURITY",
                0x00400000: "MULTIPPERCONN",
                0x00200000: "MULTIPPERPKT",
                0x00100000: "SOURCEVIPA",
                0x00080000: "TCPSOURCEVIPA",
                0x00040000: "TEMPADDRS",
                0x00020000: "CHKOFFLOAD",
                0x00010000: "SEGOFFLOAD",
                0x00008000: "DYNXCFSMCD",
            },
        ),
        BYTES("NMTP_V6CFDynXcfIntfID", 8, "Dynamic XCF interface ID"),
        IPV6("NMTP_V6CFDynXcfAddr", "Dynamic XCF IPv6 address"),
        CHAR("NMTP_V6CFDynXcfSrcVipaIntfName", 16, "Dyn XCF src VIPA intf"),
        CHAR("NMTP_V6CFTcpSrcVipaIntfName", 16, "TCP source VIPA intf"),
        U8("NMTP_V6CFDynXcfPfxRteLen", "Dyn XCF prefix route len"),
        U8("NMTP_V6CFDynXcfSecClass", "Dyn XCF security class"),
        U8("NMTP_V6CFHopLimit", "Hop limit"),
        U8("NMTP_V6CFIcmpErrLimit", "ICMPv6 errors per second"),
        U8(
            "NMTP_V6CFIgnRedirectRsn",
            "Ignore redirect reason",
            enum={1: "CFG", 2: "OMP"},
        ),
        U8("NMTP_V6CFOSMSecClass", "OSM security class"),
        RES("NMTP_V6CFResv", 2),
        I16("NMTP_V6CFTempAddrsPrefLifeTime", "Temp addr preferred lifetime (hours)"),
        I16("NMTP_V6CFTempAddrsValidLifeTime", "Temp addr valid lifetime (hours)"),
    ],
    description="IPv6 Configuration",
    eyecatcher=EYE_V6CF,
)

NMTP_TCPCFG = build_layout(
    "NMTP_TCPCFG",
    [
        EYE("NMTP_TCCFEye"),
        U16(
            "NMTP_TCCFFlags",
            "TCP config flags",
            flags={
                0x8000: "DELAYACKS",
                0x4000: "RESTRICTLOWPORTS",
                0x2000: "SENDGARBAGE",
                0x1000: "TCPTIMESTAMP",
                0x0800: "TTLS",
                0x0400: "SELECTIVEACK",
                0x0200: "NAGLE",
                0x0100: "AUTODELAYACKS",
            },
        ),
        I16("NMTP_TCCFFinWait2Time", "FINWAIT2TIME (seconds)"),
        U16("NMTP_TCCFInterval", "Keepalive interval (minutes)"),
        RES("NMTP_TCCFResv", 2),
        I32("NMTP_TCCFSoMaxConn", "SOMAXCONN"),
        I32("NMTP_TCCFMaxRcvBufSize", "Max receive buffer"),
        I32("NMTP_TCCFRcvBufSize", "Receive buffer"),
        I32("NMTP_TCCFSendBufSize", "Send buffer"),
        U16("NMTP_TCCFEphemPortBegNum", "Ephemeral port begin"),
        U16("NMTP_TCCFEphemPortEndNum", "Ephemeral port end"),
        U16("NMTP_TCCFTimeWaitInterval", "TIMEWAIT interval (seconds)"),
        U16("NMTP_TCCFRetranAttempts", "Retransmit attempts"),
        U16("NMTP_TCCFConnectTimeOut", "Connect timeout (seconds)"),
        U16("NMTP_TCCFConnectInterval", "Connect interval (ms)"),
        U16("NMTP_TCCFKeepAliveProbes", "Keepalive probes"),
        U16("NMTP_TCCFKAProbeInterval", "Keepalive probe interval (s)"),
        U16("NMTP_TCCFQueuedRTT", "Queued RTT threshold (ms)"),
        U16("NMTP_TCCFFRRThreshold", "FRR threshold"),
        I32("NMTP_TCCFMaxSndBufSize", "Max send buffer"),
        I32("NMTP_TCCFMaxRetransmit", "Max retransmit time (ms)"),
    ],
    description="TCP Configuration",
    eyecatcher=EYE_TCCF,
)

NMTP_UDPCFG = build_layout(
    "NMTP_UDPCFG",
    [
        EYE("NMTP_UDCFEye"),
        U8(
            "NMTP_UDCFFlags",
            "UDP config flags",
            flags={0x80: "RESTRICTLOWPORTS", 0x40: "UDPCHKSUM", 0x20: "UDPQUEUELIMIT"},
        ),
        RES("NMTP_UDCFResv", 3),
        U16("NMTP_UDCFRcvBufSize", "Receive buffer"),
        U16("NMTP_UDCFSendBufSize", "Send buffer"),
        U16("NMTP_UDCFEphemPortBegNum", "Ephemeral port begin"),
        U16("NMTP_UDCFEphemPortEndNum", "Ephemeral port end"),
    ],
    description="UDP Configuration",
    eyecatcher=EYE_UDCF,
)

# Nested PFID entry is 6 bytes packed; 16 entries = 96 bytes inside GBLCFG
_GBCF_PF_SIZE = 6
_GBCF_PF_COUNT = 16
_GBCF_EID_LEN = 32
_GBCF_UEID_COUNT = 4

NMTP_GBLCFG = build_layout(
    "NMTP_GBLCFG",
    [
        EYE("NMTP_GBCFEye"),
        U16(
            "NMTP_GBCFFlags",
            "Global flags",
            flags={
                0x8000: "EXPBINDPORTRANGE",
                0x4000: "IQDMULTIWRITE",
                0x2000: "MLSCHECKTERMINATE",
                0x1000: "SEGOFFLOAD",
                0x0800: "TCPIPSTATS",
                0x0400: "ZIIP",
                0x0200: "WLMPRIORITYQ",
                0x0100: "SMCR",
                0x0080: "SMCD",
                0x0040: "ZERT",
                0x0020: "SYSTEMEID",
            },
        ),
        U16(
            "NMTP_GBCFSysMonOptions",
            "SYSPLEXMONITOR options",
            flags={
                0x8000: "AUTOREJOIN",
                0x4000: "DELAYJOIN",
                0x2000: "DYNROUTE",
                0x1000: "MONINTERFACE",
                0x0800: "RECOVERY",
                0x0400: "NOJOIN",
                0x0200: "DELAYJOINIPSEC",
                0x0100: "MONIPSEC",
            },
        ),
        I16("NMTP_GBCFIqdVlanID", "IQDVLANID"),
        U8("NMTP_GBCFSysWlmPoll", "SYSPLEXWLMPOLL (seconds)"),
        U8(
            "NMTP_GBCFZiipOptions",
            "ZIIP options",
            flags={0x80: "IPSECURITY", 0x40: "IQDIOMULTIWRITE"},
        ),
        U16("NMTP_GBCFSysMonTimerSecs", "SYSPLEXMONITOR timer (seconds)"),
        CHAR("NMTP_GBCFXcfGroupID", 2, "XCFGRPID"),
        U16("NMTP_GBCFExpBindPortRangeBegNum", "Explicit bind port begin"),
        U16("NMTP_GBCFExpBindPortRangeEndNum", "Explicit bind port end"),
        I32("NMTP_GBCFMaxRecs", "MAXRECS"),
        I32("NMTP_GBCFEcsaLimit", "ECSA limit"),
        I32("NMTP_GBCFPoolLimit", "POOL limit"),
        U8("NMTP_GBCFWPQCV0Pri", "WLM pri CV0"),
        U8("NMTP_GBCFWPQCV1Pri", "WLM pri CV1"),
        U8("NMTP_GBCFWPQCV2Pri", "WLM pri CV2"),
        U8("NMTP_GBCFWPQCV3Pri", "WLM pri CV3"),
        U8("NMTP_GBCFWPQCV4Pri", "WLM pri CV4"),
        U8("NMTP_GBCFWPQCV5Pri", "WLM pri CV5"),
        U8("NMTP_GBCFWPQCV6Pri", "WLM pri CV6"),
        U8("NMTP_GBCFWPQFwdPri", "WLM pri forwarded"),
        U8("NMTP_GBCFAUTOIQDX", "AUTOIQDX settings"),
        U8("NMTP_GBCFPFidCnt", "SMCR PFID count"),
        U8(
            "NMTP_GBCFSMCGFlags",
            "SMC global flags",
            flags={0x80: "AUTOCACHE", 0x40: "AUTOSMC", 0x20: "SMCEID"},
        ),
        U8(
            "NMTP_GBCFAdjDVMSS",
            "ADJUSTDVIPAMSS",
            flags={0x80: "AUTO", 0x40: "ALL", 0x20: "NONE"},
        ),
        U32("NMTP_GBCFFixedMemory", "SMCR FIXEDM (MB)"),
        U32("NMTP_GBCFTcpKeepMinInt", "SMCR TCP keep min interval"),
        BYTES(
            "NMTP_GBCFPFs",
            _GBCF_PF_SIZE * _GBCF_PF_COUNT,
            "SMCR PFID array (16 x 6 bytes)",
        ),
        U8(
            "NMTP_GBCFZertParms",
            "ZERT subparameters",
            flags={0x80: "ZERTAGG", 0x40: "ZERTINTV", 0x20: "ZERTSYNC"},
        ),
        U8("NMTP_GBCFAUTOIQDC", "AUTOIQDC settings"),
        U8(
            "NMTP_GBCFPolicyReq",
            "POLICYREQUIRED",
            flags={0x80: "YESIFTTLS", 0x40: "YES", 0x20: "NO"},
        ),
        U8(
            "NMTP_GBCFIkedReq",
            "IKEDREQUIRED",
            flags={0x80: "YESIFDYNIPSEC", 0x40: "NO"},
        ),
        U32("NMTP_GBCFFixedMemoryD", "SMCD FIXEDM (MB)"),
        U32("NMTP_GBCFTcpKeepMinIntD", "SMCD TCP keep min interval"),
        U8("NMTP_GBCFzAGGtim_INTVAL", "zAGG INTVAL"),
        U8("NMTP_GBCFzAGGtim_SYNCVAL_HH", "zAGG SYNCVAL hour"),
        U8("NMTP_GBCFzAGGtim_SYNCVAL_MM", "zAGG SYNCVAL minute"),
        U8("NMTP_GBCFSMCEIDCount", "Number of UEIDs"),
        BYTES(
            "NMTP_GBCFUEIDList",
            _GBCF_EID_LEN * _GBCF_UEID_COUNT,
            "Configured UEIDs (4 x 32)",
        ),
        CHAR("NMTP_GBCFSYSTEMEIDSTR", _GBCF_EID_LEN, "System-generated EID"),
        RES("NMTP_GBCFrsvd", 12),
    ],
    description="Global Configuration",
    eyecatcher=EYE_GBCF,
)

NMTP_PORT = build_layout(
    "NMTP_PORT",
    [
        EYE("NMTP_PORTEye"),
        U8(
            "NMTP_PORTFlags",
            "Port flags",
            flags={0x80: "IPV6", 0x40: "PORTRANGE", 0x20: "UNRSV", 0x10: "TCP"},
        ),
        U8(
            "NMTP_PORTUseType",
            "Port use type",
            enum={1: "RESERVED", 2: "AUTHPORT", 3: "JOBNAME"},
        ),
        U16(
            "NMTP_PORTRsvOptions",
            "Reserved port options",
            flags={
                0x8000: "AUTOLOG",
                0x4000: "DELAYACKS",
                0x2000: "SHAREPORT",
                0x1000: "SHAREPORTWLM",
                0x0800: "BIND",
                0x0400: "SAF",
                0x0200: "NOSMC",
                0x0100: "SMC",
            },
        ),
        U16("NMTP_PORTBegNum", "Beginning / only port"),
        U16("NMTP_PORTEndNum", "Ending port (PORTRANGE)"),
        U8(
            "NMTP_PORTUnrsvOptions",
            "UNRSV options",
            flags={0x80: "DENY", 0x40: "SAF", 0x20: "WHENLISTEN", 0x10: "WHENBIND"},
        ),
        RES("NMTP_PORTResv", 3),
        CHAR("NMTP_PORTJobName", 8, "Job name"),
        CHAR("NMTP_PORTSafName", 8, "SAF resource name"),
        IPUNION("NMTP_PORTBindAddr", "BIND IP address"),
    ],
    description="Port / PORTRANGE / UNRSV",
    eyecatcher=EYE_PORT,
)

NMTP_INTF = build_layout(
    "NMTP_INTF",
    [
        EYE("NMTP_INTFEye"),
        U32(
            "NMTP_INTFFlags",
            "Interface flags",
            flags={
                0x80000000: "IPV6",
                0x40000000: "DEFINTF",
                0x20000000: "INTFID",
                0x10000000: "AUTORESTART",
                0x08000000: "IPBCAST",
                0x04000000: "VLANID",
                0x02000000: "MONSYSPLEX",
                0x01000000: "DYNVLANREG",
                0x00800000: "VMAC",
                0x00400000: "VMACADDR",
                0x00200000: "VMACRTLCL",
                0x00100000: "CHECKSUM",
                0x00080000: "SRCVIPAIFNAME",
                0x00040000: "TEMPPREFIX",
                0x00020000: "ISOLATE",
                0x00010000: "OLM",
                0x00008000: "CHPID",
                0x00004000: "TEMPIP",
                0x00002000: "SMCR",
                0x00001000: "SMCD",
                0x00000800: "EQEAUTOMIGRATED",
            },
        ),
        U8(
            "NMTP_INTFType",
            "Interface type",
            enum={
                1: "LOOPBACK",
                2: "OSAETH",
                3: "HIPERSOCK",
                4: "PTP",
                5: "VIRTUAL",
                6: "NETEXPOSA",
            },
        ),
        U8(
            "NMTP_INTFRtrType",
            "Router type",
            enum={1: "NONROUTER", 2: "PRIROUTER", 3: "SECROUTER"},
        ),
        U8(
            "NMTP_INTFReadStorType",
            "READSTORAGE",
            enum={1: "GLOBAL", 2: "MAX", 3: "AVG", 4: "MIN"},
        ),
        U8(
            "NMTP_INTFInbPerfType",
            "INBPERF",
            enum={1: "BALANCED", 2: "DYNAMIC", 3: "MINCPU", 4: "MINLATENCY"},
        ),
        U8("NMTP_INTFSecClass", "SECCLASS"),
        U8("NMTP_INTFChpID", "CHPID"),
        U8("NMTP_INTFDupAddrDet", "DUPADDRDET"),
        U8("NMTP_INTFIPv4Mask", "IPv4 mask bits"),
        U8(
            "NMTP_INTFTempPfxType",
            "TEMPPREFIX type",
            enum={1: "ALL", 2: "PFX", 3: "NONE", 4: "DISABLED"},
        ),
        U8("NMTP_INTFDynTypes", "Dynamic inbound types", flags={0x80: "WORKLOADQ"}),
        U8(
            "NMTP_INTFChpIDType",
            "CHPID type",
            enum={1: "OSD", 2: "OSX", 3: "OSH"},
        ),
        RES("NMTP_INTFResv1", 1),
        I16("NMTP_INTFVlanID", "VLAN ID"),
        U16("NMTP_INTFMtu", "Configured MTU"),
        IPV4("NMTP_INTFIPv4Addr", "IPv4 address"),
        U32("NMTP_INTFIfIndex", "Interface index"),
        BYTES("NMTP_INTFVmacAddr", 6, "VMAC address"),
        RES("NMTP_INTFResv2", 2),
        BYTES("NMTP_INTFIntfID", 8, "Interface ID"),
        CHAR("NMTP_INTFName", 16, "Interface name"),
        CHAR("NMTP_INTFAssocName", 16, "Associated device/TRLE name"),
        CHAR("NMTP_INTFSrcVipaIntfName", 16, "SOURCEVIPAINTERFACE"),
        U16("NMTP_INTFSmcrV2Pfid", "SMC-Rv2 PFID"),
        U16("NMTP_INTFSmcrV2MTU", "SMC-Rv2 MTU"),
        IPV4("NMTP_INTFSmcrV2Ipaddr4", "SMC-Rv2 IPv4"),
    ],
    description="Interfaces and IPv4 addresses",
    eyecatcher=EYE_INTF,
)

NMTP_IPA6 = build_layout(
    "NMTP_IPA6",
    [
        EYE("NMTP_IPA6Eye"),
        U8("NMTP_IPA6Flags", "Flags", flags={0x80: "DEPRECATED"}),
        U8(
            "NMTP_IPA6Type",
            "Address type",
            enum={1: "ADDR", 2: "PFX", 3: "TEMPPFX"},
        ),
        U8("NMTP_IPA6PfxLen", "Prefix length"),
        RES("NMTP_IPA6Resv1", 1),
        U32("NMTP_IPA6IfIndex", "Interface index"),
        RES("NMTP_IPA6Resv2", 4),
        CHAR("NMTP_IPA6IntfName", 16, "Interface name"),
        IPV6("NMTP_IPA6Addr", "IPv6 address or prefix"),
    ],
    description="IPv6 addresses",
    eyecatcher=EYE_IPA6,
)

NMTP_ROUT = build_layout(
    "NMTP_ROUT",
    [
        EYE("NMTP_ROUTEye"),
        U16(
            "NMTP_ROUTFlags",
            "Route flags",
            flags={
                0x8000: "IPV6",
                0x4000: "DEFAULT",
                0x2000: "NEXTHOP",
                0x1000: "DELAYACKS",
                0x0800: "REPLACEABLE",
                0x0400: "REPLACED",
            },
        ),
        U16("NMTP_ROUTMtu", "MTU"),
        U8("NMTP_ROUTDestPfxLen", "Destination prefix length"),
        RES("NMTP_ROUTResv", 3),
        U32("NMTP_ROUTIfIndex", "Interface index"),
        U32("NMTP_ROUTMaxRetranTime", "MAXRETRANSMITTIME (ms)"),
        U32("NMTP_ROUTMinRetranTime", "MINRETRANSMITTIME (ms)"),
        U16("NMTP_ROUTRoundTripGain", "ROUNDTRIPGAIN (thousandths)"),
        U16("NMTP_ROUTVarGain", "VARIANCEGAIN (thousandths)"),
        U32("NMTP_ROUTVarMultiplier", "VARIANCEMULTIPLIER (thousandths)"),
        CHAR("NMTP_ROUTIntfName", 16, "Interface name"),
        IPUNION("NMTP_ROUTDestAddr", "Destination address"),
        IPUNION("NMTP_ROUTNextHopAddr", "Next hop address"),
    ],
    description="Routes",
    eyecatcher=EYE_ROUT,
)

NMTP_SRCIP = build_layout(
    "NMTP_SRCIP",
    [
        EYE("NMTP_SRCIEye"),
        U8("NMTP_SRCIType", "Entry type", enum={1: "DEST", 2: "JOB"}),
        U8(
            "NMTP_SRCIFlags",
            "Flags",
            flags={
                0x80: "IPV6",
                0x40: "SRCIFNAME",
                0x30: "BOTH",
                0x20: "CLIENTS",
                0x10: "SERVERS",
                0x08: "TEMPADDRS",
                0x04: "PUBADDRS",
            },
        ),
        RES("NMTP_SRCIResv1", 1),
        U8("NMTP_SRCIDestPfxLen", "Destination prefix length"),
        CHAR("NMTP_SRCIJobName", 8, "Job name"),
        IPUNION("NMTP_SRCIDestAddr", "Destination address"),
        IPUNION("NMTP_SRCISrc", "Source address or interface name"),
    ],
    description="Source IP",
    eyecatcher=EYE_SRCI,
)

NMTP_MGMT = build_layout(
    "NMTP_MGMT",
    [
        EYE("NMTP_MGMTEye"),
        U32(
            "NMTP_MGMTSmf119Types",
            "SMF 119 types requested",
            flags={
                0x80000000: "FTPCLIENT",
                0x40000000: "IFSTATS",
                0x20000000: "IPSEC",
                0x10000000: "PORTSTATS",
                0x08000000: "PROFILE",
                0x04000000: "TCPINIT",
                0x02000000: "TCPIPSTATS",
                0x01000000: "TCPSTACK",
                0x00800000: "TCPTERM",
                0x00400000: "TN3270CLIENT",
                0x00200000: "UDPTERM",
                0x00100000: "DVIPA",
                0x00080000: "SMCRGRPSTATS",
                0x00040000: "SMCRLNKEVENT",
                0x00020000: "SMCDLNKSTATS",
                0x00010000: "SMCDLNKEVENT",
                0x00008000: "ZERTDETAIL",
                0x00004000: "ZERTSUMMARY",
                0x00002000: "ZERTDETAILPOLICY",
            },
        ),
        U8(
            "NMTP_MGMTNetMonServices",
            "NETMONITOR services",
            flags={
                0x80: "PKTTRACE",
                0x40: "TCPCONN",
                0x20: "SMF",
                0x10: "NTATRACE",
                0x08: "ZERT",
                0x04: "ZERTSUMM",
                0x02: "ZERTSERVP",
            },
        ),
        U8(
            "NMTP_MGMTNetMonSmfRecs",
            "SMFSERVICE records",
            flags={
                0x80: "IPSEC",
                0x40: "PROFILE",
                0x20: "CSSMTP",
                0x10: "CSMAIL",
                0x08: "DVIPA",
            },
        ),
        U8("NMTP_MGMTNetMonMinLife", "TCPCONNSERVICE MINLIFETIME"),
        U8(
            "NMTP_MGMTSAFlags",
            "SACONFIG flags",
            flags={
                0x80: "ENABLED",
                0x40: "OSAENABLED",
                0x20: "SETSENABLED",
                0x10: "COMMUNITY",
            },
        ),
        U16("NMTP_MGMTSAAgent", "SACONFIG agent port"),
        U16("NMTP_MGMTSAOsasf", "SACONFIG OSASF port"),
        I16("NMTP_MGMTSACacheTime", "SACONFIG cache time"),
        RES("NMTP_MGMTResv", 2),
        CHAR("NMTP_MGMTSACommName", 32, "SACONFIG community name"),
    ],
    description="Management (SMFCONFIG / NETMONITOR / SACONFIG)",
    eyecatcher=EYE_MGMT,
)

NMTP_IPSecCm = build_layout(
    "NMTP_IPSecCm",
    [
        EYE("NMTP_IPSCEye"),
        U8(
            "NMTP_IPSCFlags",
            "IPSec common flags",
            flags={
                0x80: "DVIPSEC",
                0x40: "LOGENABLE",
                0x20: "LOGIMPLICIT",
                0x10: "DVLOCALFLTR",
            },
        ),
        RES("NMTP_IPSCResv", 3),
    ],
    description="IPSec Common",
    eyecatcher=EYE_IPSC,
)

NMTP_IPSecRule = build_layout(
    "NMTP_IPSecRule",
    [
        EYE("NMTP_IPSREye"),
        U16(
            "NMTP_IPSRFlags",
            "IPSec rule flags",
            flags={
                0x8000: "IPV6",
                0x4000: "SRCADDRDEF",
                0x2000: "DESTADDRDEF",
                0x1000: "LOG",
                0x0800: "PROTODEF",
                0x0400: "SRCPORTDEF",
                0x0200: "DESTPORTDEF",
                0x0100: "TYPEDEF",
                0x0080: "CODEDEF",
                0x0040: "SRCADDRRANGE",
                0x0020: "DESTADDRRANGE",
                0x0010: "PROTOOPAQUE",
                0x0008: "SRCPORTRANGE",
                0x0004: "DESTPORTRANGE",
                0x0002: "TYPERANGE",
                0x0001: "CODERANGE",
            },
        ),
        U8("NMTP_IPSRSrcPfxLen", "Source prefix length"),
        U8("NMTP_IPSRDestPfxLen", "Dest prefix length"),
        U8("NMTP_IPSRProto", "Protocol"),
        U8("NMTP_IPSRType", "TYPE"),
        U8("NMTP_IPSRCode", "CODE"),
        U8(
            "NMTP_IPSRRoutingType",
            "ROUTING",
            enum={1: "LOCAL", 2: "ROUTED", 3: "EITHER", 4: "ROUTEDFRAG"},
        ),
        U8("NMTP_IPSRSecClass", "SECCLASS"),
        U8("NMTP_IPSRTypeEnd", "TYPE range end"),
        U8("NMTP_IPSRCodeEnd", "CODE range end"),
        U8(
            "NMTP_IPSRDirection",
            "DIRECTION",
            enum={
                1: "BIDIR",
                2: "BIDIR_INBCON",
                3: "BIDIR_OUTBCON",
                4: "INBOUND",
                5: "OUTBOUND",
            },
        ),
        U16("NMTP_IPSRSrcPort", "Source port"),
        U16("NMTP_IPSRDestPort", "Destination port"),
        IPUNION("NMTP_IPSRSrcAddr", "Source address"),
        IPUNION("NMTP_IPSRDestAddr", "Destination address"),
        IPUNION("NMTP_IPSRSrcAddrEnd", "Source address range end"),
        IPUNION("NMTP_IPSRDestAddrEnd", "Dest address range end"),
        U16("NMTP_IPSRSrcPortEnd", "Source port range end"),
        U16("NMTP_IPSRDestPortEnd", "Dest port range end"),
    ],
    description="IPSec Default Rules",
    eyecatcher=EYE_IPSR,
)

NMTP_NETACC = build_layout(
    "NMTP_NETACC",
    [
        EYE("NMTP_NETAEye"),
        U8(
            "NMTP_NETAFlags",
            "Network access flags",
            flags={
                0x80: "IPV6",
                0x40: "INBOUND",
                0x20: "OUTBOUND",
                0x10: "DEFAULT",
                0x08: "DEFAULTHOME",
            },
        ),
        U8("NMTP_NETANetwPfxLen", "Network prefix length"),
        U8(
            "NMTP_NETACache",
            "Cache level",
            enum={1: "CACHEALL", 2: "CACHEPERMIT", 3: "CACHESAME"},
        ),
        RES("NMTP_NETAResv1", 1),
        CHAR("NMTP_NETASafName", 8, "SAF resource name"),
        IPUNION("NMTP_NETANetwAddr", "Network address"),
    ],
    description="Network Access",
    eyecatcher=EYE_NETA,
)

NMTP_DVCFG = build_layout(
    "NMTP_DVCFG",
    [
        EYE("NMTP_DVCFEye"),
        U16(
            "NMTP_DVCFFlags",
            "DVIPA flags",
            flags={
                0x8000: "CHGCANCELLED",
                0x4000: "IPV6",
                0x2000: "MOVEIMMED",
                0x1000: "MOVENONDISRUPT",
                0x0800: "CPCSCOPE",
                0x0400: "TIER1",
                0x0200: "TIER2",
                0x0100: "SERVMGR",
                0x0080: "DEACTIVATED",
                0x0040: "SAFNAME",
                0x0020: "ZCX",
                0x0010: "ZCONT",
                0x0008: "ZCPA",
            },
        ),
        U8(
            "NMTP_DVCFType",
            "DVIPA type",
            enum={1: "BACKUP", 2: "DEFINE", 3: "RANGE"},
        ),
        U8("NMTP_DVCFBackupRank", "Backup RANK"),
        U8("NMTP_DVCFPfxLen", "Prefix / mask bits"),
        RES("NMTP_DVCFResv1", 7),
        IPUNION("NMTP_DVCFAddr", "DVIPA address"),
        CHAR("NMTP_DVCFIntfName", 16, "IPv6 interface name"),
        CHAR("NMTP_DVCFSAFName", 8, "SAF name"),
    ],
    description="Dynamic VIPA Addresses",
    eyecatcher=EYE_DVCF,
)

NMTP_DVRT = build_layout(
    "NMTP_DVRT",
    [
        EYE("NMTP_DVRTEye"),
        U8(
            "NMTP_DVRTFlags",
            "DVIPA route flags",
            flags={0x80: "CHGCANCELLED", 0x40: "IPV6"},
        ),
        RES("NMTP_DVRTResv", 3),
        IPUNION("NMTP_DVRTDynXcfAddr", "Dynamic XCF address"),
        IPUNION("NMTP_DVRTTargetAddr", "Target address"),
    ],
    description="DVIPA Routes",
    eyecatcher=EYE_DVRT,
)

NMTP_DISTDV = build_layout(
    "NMTP_DISTDV",
    [
        EYE("NMTP_DDVSEye"),
        U16(
            "NMTP_DDVSFlags",
            "Distributed DVIPA flags",
            flags={
                0x8000: "CHGCANCELLED",
                0x4000: "IPV6",
                0x2000: "PORT",
                0x1000: "DESTIPALL",
                0x0800: "OPTLOCAL",
                0x0400: "SYSPLEXPORTS",
                0x0200: "TIER1",
                0x0100: "TIER1GRE",
                0x0080: "TIER2",
                0x0040: "DEACTIVATED",
                0x0020: "PREFERRED",
                0x0010: "BACKUP",
                0x0008: "AUTOSWITCHBACK",
                0x0004: "HEALTHSWITCH",
                0x0002: "EXTTARG",
                0x0001: "PAUSE",
            },
        ),
        U8(
            "NMTP_DDVSDistMethod",
            "Distribution method",
            enum={
                1: "BASEWLM",
                2: "ROUNDROBIN",
                3: "SERVERWLM",
                4: "WEIGHTEDACT",
                5: "TARGCONTROL",
                6: "HOTSTANDBY",
            },
        ),
        U8("NMTP_DDVSBWProcTypeCp", "BaseWlm PROCTYPE CP"),
        U8("NMTP_DDVSBWProcTypeZaap", "BaseWlm PROCTYPE zAAP"),
        U8("NMTP_DDVSBWProcTypeZiip", "BaseWlm PROCTYPE zIIP"),
        U8("NMTP_DDVSSWProcXcostZaap", "ServerWlm PROCXCOST zAAP"),
        U8("NMTP_DDVSSWProcXcostZiip", "ServerWlm PROCXCOST zIIP"),
        U8("NMTP_DDVSSWIlWeighting", "ServerWlm ILWEIGHTING"),
        U8("NMTP_DDVSWADestipWeight", "WeightedActive WEIGHT"),
        U8("NMTP_DDVSOptLocalValue", "OPTLOCAL value"),
        U8("NMTP_DDVSBackupRank", "Backup rank"),
        RES("NMTP_DDVSResv1", 2),
        U16("NMTP_DDVSTimedAffinity", "TIMEDAFFINITY"),
        U16("NMTP_DDVSControlPortNum", "CONTROLPORT (deprecated)"),
        U16("NMTP_DDVSDistPortNum", "Distributed port"),
        CHAR("NMTP_DDVSTierGroupName", 16, "Tier group name"),
        IPUNION("NMTP_DDVSDist", "Distributed DVIPA / IPv6 intf name"),
        IPUNION("NMTP_DDVSDestip", "Destination / target address"),
    ],
    description="Distributed DVIPA",
    eyecatcher=EYE_DDVS,
)

NMTP_DASP = build_layout(
    "NMTP_DASP",
    [
        EYE("NMTP_DASPEye"),
        IPV6("NMTP_DASPPrefix", "IPv6 address prefix"),
        U8("NMTP_DASPPfxLen", "Prefix length"),
        RES("NMTP_DASPResv1", 3),
        U16("NMTP_DASPPrecedence", "Policy precedence"),
        U16("NMTP_DASPLabel", "Policy label"),
    ],
    description="Default Address Selection Policy",
    eyecatcher=EYE_DASP,
)

NMTP_FLTP = build_layout(
    "NMTP_FLTP",
    [
        EYE("NMTP_FLTPEye"),
        IPUNION("NMTP_FLTPIPaddr", "Permit filter address"),
        U8("NMTP_FLTPPrefix", "Prefix length"),
        U8("NMTP_FLTPFLG", "Flags", flags={0x80: "IPV6"}),
        RES("NMTP_FLTPResv", 2),
    ],
    description="SMC Filter Permit",
    eyecatcher=EYE_FLTP,
)

NMTP_FLTE = build_layout(
    "NMTP_FLTE",
    [
        EYE("NMTP_FLTEEye"),
        IPUNION("NMTP_FLTEIPaddr", "Exclude filter address"),
        U8("NMTP_FLTEPrefix", "Prefix length"),
        U8("NMTP_FLTEFLG", "Flags", flags={0x80: "IPV6"}),
        RES("NMTP_FLTEResv", 2),
    ],
    description="SMC Filter Exclude",
    eyecatcher=EYE_FLTE,
)

# Triplet index after Ident for subtype 4 (ezasmf: 24 triplets total)
PROFILE_SECTIONS: list[tuple[str, StructLayout, int]] = [
    ("PICommon", NMTP_PICommon, EYE_PICO),
    ("PIDS", NMTP_PIDS, EYE_PIDS),
    ("ALPROC", NMTP_ALPROC, EYE_ALPR),
    ("V4CFG", NMTP_V4CFG, EYE_V4CF),
    ("V6CFG", NMTP_V6CFG, EYE_V6CF),
    ("TCPCFG", NMTP_TCPCFG, EYE_TCCF),
    ("UDPCFG", NMTP_UDPCFG, EYE_UDCF),
    ("GBLCFG", NMTP_GBLCFG, EYE_GBCF),
    ("PORT", NMTP_PORT, EYE_PORT),
    ("INTF", NMTP_INTF, EYE_INTF),
    ("IPA6", NMTP_IPA6, EYE_IPA6),
    ("ROUT", NMTP_ROUT, EYE_ROUT),
    ("SRCIP", NMTP_SRCIP, EYE_SRCI),
    ("MGMT", NMTP_MGMT, EYE_MGMT),
    ("IPSecCm", NMTP_IPSecCm, EYE_IPSC),
    ("IPSecRule", NMTP_IPSecRule, EYE_IPSR),
    ("NETACC", NMTP_NETACC, EYE_NETA),
    ("DVCFG", NMTP_DVCFG, EYE_DVCF),
    ("DVRT", NMTP_DVRT, EYE_DVRT),
    ("DISTDV", NMTP_DISTDV, EYE_DDVS),
    ("DASP", NMTP_DASP, EYE_DASP),
    ("FLTP", NMTP_FLTP, EYE_FLTP),
    ("FLTE", NMTP_FLTE, EYE_FLTE),
]

LAYOUT_BY_EYE: dict[int, StructLayout] = {eye: layout for _, layout, eye in PROFILE_SECTIONS}
LAYOUT_BY_NAME: dict[str, StructLayout] = {name: layout for name, layout, _ in PROFILE_SECTIONS}
