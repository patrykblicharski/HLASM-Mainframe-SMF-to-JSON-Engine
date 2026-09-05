"""SMF type 119 — TCP/IP (header + ident + per-subtype sections).

Section layouts are generated from PACSYS / IBM IFASMFR tables
(``python/tools/gen_smf119_maps.py``). Header and stack ident stay
hand-written so json keys stay stable across subtypes.
"""

from __future__ import annotations

from ..types import FieldSpec as F
from .smf119_generated import SECTION_FIELDS, SUBTYPE_TITLES

# Self-defining triplets (absolute offsets from RDW / SMF119LEN)
IDOFF = 28


def _h(key, ibm, ftype, off, desc):
    return F(key, ibm, ftype, off, None, description=desc)


def _s(key, ibm, ftype, off, trip, desc):
    return F(key, ibm, ftype, off, trip, description=desc)


HEADER = [
    _h("smf_sys_flag", "SMF119FLG", "DEC1", 4, "System indicator flags"),
    _h("smf_record_type", "SMF119RTY", "DEC1", 5, "Record type (119)"),
    _h("time", "SMF119TME", "TME", 6, "Time record moved to SMF buffer"),
    _h("date", "SMF119DTE", "DTE", 10, "Date record moved to SMF buffer (0cyydddF)"),
    _h("smf_system_id", "SMF119SID", "CHR4", 14, "System identification (SID)"),
    _h("smf_subsystem_id", "SMF119SSI", "CHR4", 18, "Subsystem identification"),
    _h("smf_subtype", "SMF119STY", "DEC2", 22, "Record subtype"),
]

IDENT = [
    _s("sys_name", "SMF119TI_SYSName", "CHR8", 0, IDOFF, "System name from SYSNAME in IEASYSxx"),
    _s("sysplex_name", "SMF119TI_SysplexName", "CHR8", 8, IDOFF, "Sysplex name from SYSPLEX in COUPLExx"),
    _s("tcp_stack", "SMF119TI_Stack", "CHR8", 16, IDOFF, "TCP/IP stack name"),
    _s(
        "tcp_release",
        "SMF119TI_ReleaseID",
        "CHR8",
        24,
        IDOFF,
        "z/OS Communications Server TCP/IP release identifier",
    ),
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
]

COMMON = HEADER + IDENT

FIELDS_BY_SUBTYPE: dict[int, list[F]] = {
    sty: COMMON + list(sections) for sty, sections in SECTION_FIELDS.items()
}

# Back-compat: subtype 1 is the original map.
FIELDS = FIELDS_BY_SUBTYPE[1]

__all__ = [
    "COMMON",
    "FIELDS",
    "FIELDS_BY_SUBTYPE",
    "HEADER",
    "IDENT",
    "SECTION_FIELDS",
    "SUBTYPE_TITLES",
]
