"""SMF Type 119 subtype catalog (from ezasmf.h SMF119HDST_*)."""
from __future__ import annotations

# subtype -> short title
SUBTYPES: dict[int, str] = {
    1: "TCP connection initiation",
    2: "TCP connection termination",
    3: "FTP client transfer completion",
    4: "TCP/IP profile event",
    5: "TCP/IP statistics",
    6: "Interface statistics",
    7: "Server port statistics",
    8: "TCP/IP stack start/stop",
    10: "UDP endpoint close",
    11: "zERT connection detail",
    12: "zERT summary",
    20: "TN3270E server session initiation",
    21: "TN3270E server session termination",
    22: "TSO Telnet client initiation",
    23: "TSO Telnet client termination",
    24: "TN3270E Telnet profile",
    32: "DVIPA status change",
    33: "DVIPA removed",
    34: "DVIPA target added",
    35: "DVIPA target removed",
    36: "DVIPA target server started",
    37: "DVIPA target server ended",
    38: "SMC-D link statistics",
    39: "SMC-D link start",
    40: "SMC-D link end",
    41: "SMC-R link group statistics",
    42: "SMC-R link start",
    43: "SMC-R link end",
    44: "RNIC statistics",
    45: "ISM statistics",
    48: "CSSMTP configuration",
    49: "CSSMTP connection",
    50: "CSSMTP mail message",
    51: "CSSMTP JES spool",
    52: "CSSMTP statistics",
    70: "FTP server transfer completion",
    71: "FTPD configuration",
    72: "FTP server logon failure",
    73: "IKE tunnel activation / refresh",
    74: "IKE tunnel deactivation / expire",
    75: "Dynamic tunnel activation / refresh",
    76: "Dynamic tunnel deactivation",
    77: "Dynamic tunnel added",
    78: "Dynamic tunnel removed",
    79: "Manual tunnel activation",
    80: "Manual tunnel deactivation",
    81: "VTAM 3270 IDS",
    94: "OpenSSH (x'5E')",
    95: "OpenSSH (x'5F')",
    96: "OpenSSH (x'60')",
    97: "OpenSSH (x'61')",
    98: "OpenSSH (x'62')",
}

SMF_TYPE_119 = 119

# Standard SMF header flag: subtypes are valid (ezasmf SMF119HDSub)
FLAG_SUBTYPES_USED = 0x40

# Subtype 4: max triplets including Ident (ezasmf SMF119SD_TRN_TP)
PROFILE_TRIPLET_COUNT = 24


def title_for(subtype: int) -> str:
    return SUBTYPES.get(subtype, f"SMF 119 subtype {subtype}")
