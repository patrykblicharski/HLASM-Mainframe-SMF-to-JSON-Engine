"""SMF type 80 — RACF processing (z/OS 3.1 / 3.01.00).

Fixed-section layout matches PACSYS
https://www.pacsys.com/smf/smf80.htm
and IBM *Record type 80: RACF processing record* (z/OS 3.1 SMF).
Relocate data types: *z/OS Security Server RACF Macros and Interfaces*.

**Not a subtype record.** Bytes 22–23 are ``SMF80USR``, not ``SMFxSTY``.
Discrimination is by ``SMF80EVT`` (+ ``SMF80EVQ``). Kept in
``MAPS_BY_TYPE[80]`` so the engine never keys type 80 on those bytes.

``SMF80REL`` / ``SMF80RL2`` are offsets **from SMF80FLG** (absolute =
value + 4 when the RDW is present). PACSYS sometimes labels this “from
beginning of record”; IBM/HLASM treat it as from FLG — engine ``RS_*`` /
``RS2_*`` apply +4.

Common EVT groups: 1 job init/logon, 2 resource access, 3–7
DEFINE/RENAME/DELETE, commands / APPCLU / UNIX / certificate — see RACF
Macros. Extended-length tags (``SMF80TP2``) include MFA 441/444 etc.
"""

from __future__ import annotations

from ..types import FieldSpec as F


def _h(key, ibm, ftype, off, desc, length=None):
    return F(key, ibm, ftype, off, None, length=length, description=desc)


def _rs(key, tag, desc, ftype="RS_STR"):
    """Classic relocate: control at SMF80REL (offset 38), 1-byte DTP/DLN."""
    return F(key, "SMF80REL", ftype, 38, tag=tag, description=desc)


def _rs2(key, tag, desc, ftype="RS2_STR"):
    """Extended-length relocate: control at SMF80RL2 (offset 92), 2-byte TP2/DL2."""
    return F(key, "SMF80RL2", ftype, 92, tag=tag, description=desc)


FIELDS = [
    # --- PACSYS / IBM fixed section (absolute from SMF80LEN / RDW) ---
    _h("smf_sys_flag", "SMF80FLG", "HEX1", 4, "System indicator flags"),
    _h("smf_record_type", "SMF80RTY", "DEC1", 5, "Record type (80)"),
    _h("time", "SMF80TME", "TME", 6, "Time record moved to SMF buffer"),
    _h("date", "SMF80DTE", "DTE", 10, "Date record moved to SMF buffer"),
    _h("smf_system_id", "SMF80SID", "CHR4", 14, "System identification (SID)"),
    _h(
        "descriptor_flags",
        "SMF80DES",
        "HEX2",
        18,
        "Descriptor flags (violation, undefined user, warning, VRM present, …)",
    ),
    _h(
        "event_code",
        "SMF80EVT",
        "DEC1",
        20,
        "RACF event code (1=job init/logon, 2=resource access, …)",
    ),
    _h(
        "event_qualifier",
        "SMF80EVQ",
        "DEC1",
        21,
        "Event code qualifier (outcome / detail; see RACF Macros and Interfaces)",
    ),
    _h(
        "user_id",
        "SMF80USR",
        "CHR8",
        22,
        "User associated with event (job name if user not RACF-defined)",
    ),
    _h(
        "group_name",
        "SMF80GRP",
        "CHR8",
        30,
        "Connect group (step name if user not RACF-defined)",
    ),
    _h(
        "relocate_offset",
        "SMF80REL",
        "DEC2",
        38,
        "Offset to first relocate section from SMF80FLG",
    ),
    _h("relocate_count", "SMF80CNT", "DEC2", 40, "Number of relocate sections"),
    _h(
        "authorities_used",
        "SMF80ATH",
        "HEX1",
        42,
        "Authorities used (SPECIAL/OPERATIONS/AUDITOR/exit/failsoft/bypass/trusted)",
    ),
    _h(
        "logging_reason",
        "SMF80REA",
        "HEX1",
        43,
        "Reason for logging (AUDIT/UAUDIT/SPECIAL/resource AUDIT/…)",
    ),
    _h(
        "terminal_level",
        "SMF80TLV",
        "DEC1",
        44,
        "Terminal level number of foreground user (0 if N/A)",
    ),
    _h(
        "command_error",
        "SMF80ERR",
        "HEX1",
        45,
        "Command processing error flags",
    ),
    _h(
        "terminal_id",
        "SMF80TRM",
        "CHR8",
        46,
        "Terminal ID of foreground user (blank/zero if N/A)",
    ),
    _h("job_name", "SMF80JBN", "CHR8", 54, "Job name / APPC transaction name"),
    _h(
        "reader_start_t",
        "SMF80RST",
        "TME",
        62,
        "Reader recognized JOB card — time",
    ),
    _h(
        "reader_start_d",
        "SMF80RSD",
        "DTE",
        66,
        "Reader recognized JOB card — date",
    ),
    _h(
        "user_identification",
        "SMF80UID",
        "CHR8",
        70,
        "User identification from SMF common exit parameter area",
    ),
    _h(
        "version_indicator",
        "SMF80VER",
        "DEC1",
        78,
        "Version indicator (legacy; prefer SMF80VRM)",
    ),
    _h(
        "logging_reason_2",
        "SMF80RE2",
        "HEX1",
        79,
        "Additional logging reasons (SECLABELAUDIT, LOGOPTIONS, …)",
    ),
    _h(
        "racf_fmid",
        "SMF80VRM",
        "CHR4",
        80,
        "RACF FMID / VRRM (e.g. 77E0 = z/OS 3.1 Security Server)",
    ),
    _h(
        "security_label",
        "SMF80SEC",
        "CHR8",
        84,
        "Security label of the user",
    ),
    _h(
        "ext_relocate_offset",
        "SMF80RL2",
        "DEC2",
        92,
        "Offset to extended-length relocate sections from SMF80FLG",
    ),
    _h(
        "ext_relocate_count",
        "SMF80CT2",
        "DEC2",
        94,
        "Count of extended-length relocate sections",
    ),
    _h(
        "authorities_used_2",
        "SMF80AU2",
        "HEX1",
        96,
        "Authority continued (OpenEdition superuser / system function)",
    ),
    # --- Classic relocate (SMF80DTP / DLN / DTA) — PACSYS sample uses 1/3/4/17 ---
    _rs(
        "old_resource",
        1,
        "Relocate tag 1 — resource name or old resource name (AUTH/DEFINE)",
    ),
    _rs(
        "new_dataset_name",
        2,
        "Relocate tag 2 — new data set name (DEFINE rename)",
    ),
    _rs(
        "access_requested",
        3,
        "Relocate tag 3 — access authority requested (1-byte binary)",
        ftype="RS_HEX",
    ),
    _rs(
        "access_allowed",
        4,
        "Relocate tag 4 — access authority allowed (1-byte binary)",
        ftype="RS_HEX",
    ),
    _rs(
        "command_data",
        6,
        "Relocate tag 6 — command-related data (see RACF table of data type 6)",
        ftype="RS_HEX",
    ),
    _rs(
        "user_name",
        8,
        "Relocate tag 8 — NAME user-name (ADDUSER/ALTUSER)",
    ),
    _rs(
        "command_resource",
        9,
        "Relocate tag 9 — resource name (PERMIT/RALTER/RDEFINE/RDELETE)",
    ),
    _rs(
        "from_resource",
        13,
        "Relocate tag 13 — FROM resource name (PERMIT/ADDSD/RDEFINE)",
    ),
    _rs(
        "volser",
        15,
        "Relocate tag 15 — VOLSER volume serial (AUTH/DEFINE)",
    ),
    _rs(
        "old_volser",
        16,
        "Relocate tag 16 — OLDVOL volume serial (AUTH/DEFINE)",
    ),
    _rs(
        "class_name",
        17,
        "Relocate tag 17 — class name (AUTH/DEFINE/commands / z/OS UNIX)",
    ),
    _rs(
        "application_name",
        20,
        "Relocate tag 20 — application name (VERIFY/VERIFYX / job init)",
    ),
    # --- Extended-length relocate (SMF80TP2) — MFA / long names (z/OS 3.1) ---
    _rs2(
        "mfa_factor_name",
        441,
        "Extended relocate 441 — multifactor authentication factor name",
    ),
    _rs2(
        "mfa_policy_name",
        444,
        "Extended relocate 444 — MFA policy name (ADDPOLICY/DELPOLICY)",
    ),
]
