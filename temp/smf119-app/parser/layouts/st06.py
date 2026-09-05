"""Auto-generated layouts for SMF 119 subtype 6 (from PACSYS offset tables)."""
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

IS_IF_S1 = build_layout(
    "SMF119IS_IF_S1",
    [
        U64("SMF119SP_IFDuration", "Duration of recording interval in microseconds, where bit 51 is equivalent to one microsecond"),
        BYTES("SMF119IS_IFLnkHome", 16, "Interface HOME address. For IPv6 interfaces, additional addresses might be specified in subsequent HOME IP address sections."),
        CHAR("SMF119IS_IFName", 16, "Link or interface name"),
        CHAR("SMF119IS_IFDevName", 16, "Device name"),
        CHAR("SMF119IS_IFDesc", 18, "Interface Description (TCPIP PROFILE keyword for LINK or INTERFACE type.) Possible values include: ATM, CDLC, CTC, ETHERnet, ETHEROR802.3, FDDI, HCH, IBMTR, IP, IPAQENET, IPAQIDIO, IPAQTR, MPCPTP, OSAENET, OSAFDDI, SAMEHOST, Unknown, 802.3,"),
        RES("_rsv_74", 2),
        U32("SMF119IS_IFActualMtu", "MTU size"),
        U32("SMF119IS_IFSPeed", "Speed Guideline: If the interface speed exceeds x'FFFFFFFF', then this field contains x'FFFFFFFF'. If this field contains x'FFFFFFFF', then use the SMF119IS_IFHSpeed field to determine the interface speed."),
        U32("SMF119IS_IFHSpeed", "HSpeed"),
        U64("SMF119IS_IFInBytes", "Number of inbound bytes"),
        U64("SMF119IS_IFInUniC", "Number of inbound Unicast packets"),
        U64("SMF119IS_IFInBroadC", "Number of inbound broadcast packets"),
        U64("SMF119IS_IFInMultiC", "Number of inbound multicast packets"),
        U32("SMF119IS_IFInDisc", "Number of inbound discarded packets"),
        U32("SMF119IS_IFInError", "Number of inbound packets in error"),
        U32("SMF119IS_IFInUProt", "Number of inbound packets with unknown protocol."),
        U64("SMF119IS_IFOutBytes", "Number of outbound bytes"),
        U64("SMF119IS_IFOutUniC", "Number of outbound Unicast packets"),
        U64("SMF119IS_IFOutBroadC", "Number of outbound broadcast packets"),
        U64("SMF119IS_IFOutMultiC", "Number of outbound multicast packets"),
        U32("SMF119IS_IFOutDisc", "Number of outbound discarded packets"),
        U32("SMF119IS_IFOutError", "Number of outbound packets in error"),
        U32("SMF119IS_IFOQL", "Current output queue length"),
        CHAR("SMF119IS_IFIQDXName", 16, "For IPAQENET and IPAQENET6 interfaces that are defined with CHPIDTYPE OSX and with an associated IQDX interface, this field is the associated IQDX interface name. Otherwise, this field is blank and the following four counters are not valid."),
        U64("SMF119IS_IFInIQDXBytes", "Number of inbound bytes that were received over the associated IQDX interface. This field is valid only if the SMF119IS_IFIQDXName field is not blank."),
        U64("SMF119IS_IFInIQDXUniC", "Number of inbound unicast packets that were received over the associated IQDX interface. This field is valid only if the SMF119IS_IFIQDXName field is not blank."),
        U64("SMF119IS_IFOutIQDXBytes", "Number of outbound bytes that were sent over the associated IQDX interface. This field is valid only if the SMF119IS_IFIQDXName field is not blank."),
        U64("SMF119IS_IFOutIQDXUniC", "Number of outbound unicast packets that were sent over the associated IQDX interface. This field is valid only if the SMF119IS_IFIQDXName field is not blank."),
        CHAR("SMF119IS_IFPNetID", 16, "Physical network ID. This field is valid for only IPAQENET and IPAQENET6 interfaces that are active for Shared Memory Communications over RDMA (SMC-R)."),
    ],
    description="SMF119IS_IF_S1",
)

IS_IF_S2 = build_layout(
    "SMF119IS_IF_S2",
    [
        CHAR("SMF119IS_IFAddIntfName", 16, "Interface name, used to correlate this additional address to the interface statistics record in Table 169"),
        BYTES("SMF119IS_IFAddIntfHome", 16, "Additional interface HOME address"),
    ],
    description="SMF119IS_IF_S2",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key='S1', layout=IS_IF_S1),
    SectionSlot(triplet_index=2, key='S2', layout=IS_IF_S2),
]

__all__ = ['IS_IF_S1', 'IS_IF_S2', "SECTION_SLOTS"]
