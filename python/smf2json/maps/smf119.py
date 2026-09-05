"""SMF type 119 subtype 1 — TCP connection initiation (PACSYS / IBM IFASMFR)."""

from __future__ import annotations

from ..types import FieldSpec as F

# Self-defining triplets (absolute offsets from RDW / SMF119LEN)
IDOFF, S1OFF = 28, 36


def _h(key, ibm, ftype, off, desc):
    return F(key, ibm, ftype, off, None, description=desc)


def _s(key, ibm, ftype, off, trip, desc):
    return F(key, ibm, ftype, off, trip, description=desc)


# Header + TCP/IP ident + subtype-1 connection initiation section.
# Other 119 subtypes are skipped by the registry (MAPS_BY_SUBTYPE).
FIELDS = [
    # Standard SMF header
    _h("smf_sys_flag", "SMF119FLG", "DEC1", 4, "System indicator flags"),
    _h("smf_record_type", "SMF119RTY", "DEC1", 5, "Record type (119)"),
    _h("time", "SMF119TME", "TME", 6, "Time record moved to SMF buffer"),
    _h("date", "SMF119DTE", "DTE", 10, "Date record moved to SMF buffer (0cyydddF)"),
    _h("smf_system_id", "SMF119SID", "CHR4", 14, "System identification (SID)"),
    _h("smf_subsystem_id", "SMF119SSI", "CHR4", 18, "Subsystem identification"),
    _h("smf_subtype", "SMF119STY", "DEC2", 22, "Record subtype (1 = TCP connection initiation)"),
    # TCP/IP identification section (SMF119IDOff)
    _s("sys_name", "SMF119TI_SYSName", "CHR8", 0, IDOFF, "System name from SYSNAME in IEASYSxx"),
    _s("sysplex_name", "SMF119TI_SysplexName", "CHR8", 8, IDOFF, "Sysplex name from SYSPLEX in COUPLExx"),
    _s("tcp_stack", "SMF119TI_Stack", "CHR8", 16, IDOFF, "TCP/IP stack name"),
    _s("tcp_release", "SMF119TI_ReleaseID", "CHR8", 24, IDOFF, "z/OS Communications Server TCP/IP release identifier"),
    _s(
        "tcp_component",
        "SMF119TI_Comp",
        "CHR8",
        32,
        IDOFF,
        "TCP/IP subcomponent (FTPC/FTPS/IP/STACK/TCP/TN3270C/TN3270S/UDP)",
    ),
    _s("as_name", "SMF119TI_ASName", "CHR8", 40, IDOFF, "Started task qualifier or address space name"),
    _s("user_id", "SMF119TI_UserID", "CHR8", 48, IDOFF, "User ID of the security context writing this record"),
    _s("asid", "SMF119TI_ASID", "DEC2", 58, IDOFF, "ASID of the address space that writes this record"),
    _s("record_reason", "SMF119TI_Reason", "HEX1", 60, IDOFF, "Reason for writing this record (08 = event)"),
    # Subtype 1 — TCP connection initiation (SMF119S1Off)
    _s(
        "resource_name",
        "SMF119AP_TIRName",
        "CHR8",
        0,
        S1OFF,
        "TCP socket resource name (address space that established the connection)",
    ),
    _s("connection_id", "SMF119AP_TIConnID", "DEC4", 8, S1OFF, "TCP socket resource ID (connection ID)"),
    _s("subtask_tcb", "SMF119AP_TISubTask", "HEX4", 16, S1OFF, "TCB address of the task that owns this connection"),
    _s("remote_ip", "SMF119AP_TIRIP", "IP16", 20, S1OFF, "Remote IP address at connection open"),
    _s("local_ip", "SMF119AP_TILIP", "IP16", 36, S1OFF, "Local IP address at connection open"),
    _s("remote_port", "SMF119AP_TIRPort", "DEC2", 52, S1OFF, "Remote port number at connection open"),
    _s("local_port", "SMF119AP_TILPort", "DEC2", 54, S1OFF, "Local port number at connection open"),
    _s("conn_time", "SMF119AP_TITime", "TME", 56, S1OFF, "Time of day of connection establishment"),
    _s("conn_date", "SMF119AP_TIDate", "DTE", 60, S1OFF, "Date of connection establishment"),
    _s("conn_stck", "SMF119AP_TISTCK", "HEX8", 64, S1OFF, "STCK of connection establishment"),
]
