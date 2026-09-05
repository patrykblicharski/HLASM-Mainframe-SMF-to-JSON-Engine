"""SMF type 42 — DFSMS statistics (subtypes 20–25).

Layouts from IBM z/OS SMF (IFASMFR / IGWSMF) and PACSYS smf42 tables.
Header + product section are shared; each subtype has its own section map.
Register via ``MAPS_BY_SUBTYPE[(42, sty)]`` — do not use a flat type-42 map.
"""

from __future__ import annotations

from ..types import FieldSpec as F

# Self-defining triplets (absolute offsets from RDW / SMF42LEN)
OPS = 28  # product section (all subtypes)
S1 = 36  # first subtype-specific section
S2 = 44  # second subtype-specific section
S3 = 52  # third subtype-specific section (21 / 24 / 25)


def _h(key, ibm, ftype, off, desc, length=None):
    return F(key, ibm, ftype, off, None, length=length, description=desc)


def _s(key, ibm, ftype, off, trip, desc, length=None):
    return F(key, ibm, ftype, off, trip, length=length, description=desc)


HEADER = [
    _h("smf_sys_flag", "SMF42FLG", "DEC1", 4, "System indicator flags"),
    _h("smf_record_type", "SMF42RTY", "DEC1", 5, "Record type (42)"),
    _h("time", "SMF42TME", "TME", 6, "Time record moved to SMF buffer"),
    _h("date", "SMF42DTE", "DTE", 10, "Date record moved to SMF buffer (0cyydddF)"),
    _h("smf_system_id", "SMF42SID", "CHR4", 14, "System identification (SID)"),
    _h("smf_subsystem_id", "SMF42SSI", "CHR4", 18, "Subsystem identification"),
    _h("smf_subtype", "SMF42STY", "DEC2", 22, "Record subtype"),
]

PRODUCT = [
    _s("product_level", "SMF42PDL", "CHR8", 0, OPS, "Product level"),
    _s("product_name", "SMF42PDN", "CHR", 8, OPS, "Product name", length=10),
    _s("subtype_version", "SMF42PSV", "DEC1", 18, OPS, "Subtype version number"),
]

COMMON = HEADER + PRODUCT

SUBTYPE_TITLES = {
    20: "STOW Initialize",
    21: "Member Delete",
    22: "DFSMSrmm audit records",
    23: "DFSMSrmm security records",
    24: "Member add/replace",
    25: "Member rename",
}

# Subtype 20 — STOW Initialize (KN1 job/DSN @S1, KN4 user @S2)
_ST20 = [
    _s("job_name", "SMF42KJB", "CHR8", 0, S1, "Job / STC / TSO user who issued STOW Initialize"),
    _s("step_name", "SMF42KST", "CHR8", 8, S1, "Step name"),
    _s("proc_name", "SMF42KPR", "CHR8", 16, S1, "Proc name (or blanks)"),
    _s("dsname", "SMF42KDS", "CHR", 24, S1, "Data set name", length=44),
    _s("volser", "SMF42KVS", "CHR", 68, S1, "Volume serial number", length=6),
    _s(
        "user_token",
        "SMF42KUI",
        "HEX",
        0,
        S2,
        "User information of STOW caller (ICHRUTKN)",
        length=16,
    ),
]

# Subtype 21 — Member Delete (LN1 @S1, alias count @S2, user @S3)
_ST21 = [
    _s("job_name", "SMF42LJB", "CHR8", 0, S1, "Job / STC / TSO user who issued STOW/DESERV delete"),
    _s("step_name", "SMF42LST", "CHR8", 8, S1, "Step name"),
    _s("proc_name", "SMF42LPR", "CHR8", 16, S1, "Proc name (or blanks)"),
    _s("dsname", "SMF42LDS", "CHR", 24, S1, "Data set name", length=44),
    _s("volser", "SMF42LVS", "CHR", 68, S1, "Volume serial number", length=6),
    _s("member_name_len", "SMF42LNL", "DEC2", 74, S1, "Length of deleted member name"),
    _s("member_flags", "SMF42LFL", "HEX4", 76, S1, "Member delete flags (aliases truncated, …)"),
    _s("member_name", "SMF42LMN", "VAR_CHR", 80, S1, "Member name that was deleted"),
    _s("alias_count", "SMF42LNA", "DEC2", 0, S2, "Number of alias names deleted in sympathy"),
    _s(
        "user_token",
        "SMF42LUI",
        "HEX",
        0,
        S3,
        "User information of STOW caller (ICHRUTKN)",
        length=16,
    ),
]

# Subtype 22 — DFSMSrmm audit (AUD @S1); record body @S2 is EDGSxREC (unmapped here)
_ST22 = [
    _s("job_name", "SMF42MJBN", "CHR8", 0, S1, "Job name"),
    _s("reader_start_t", "SMF42MRST", "TME", 8, S1, "Reader start time"),
    _s("reader_start_d", "SMF42MRSD", "DTE", 12, S1, "Reader start date"),
    _s("racf_user", "SMF42MUID", "CHR8", 16, S1, "RACF user ID"),
    _s(
        "activity_type",
        "SMF42MACT",
        "CHR1",
        24,
        S1,
        "Activity type (A=added, C=changed, D=deleted)",
    ),
    _s("audit_flags", "SMF42MFG1", "HEX1", 25, S1, "Flag 1 (last-in-set, journal available, …)"),
    _s("journal_record_number", "SMF42MCJNRECN", "DEC4", 36, S1, "Journal record number"),
]

# Subtype 23 — DFSMSrmm security (SEC @S1)
_ST23 = [
    _s("job_name", "SMF42NJBN", "CHR8", 0, S1, "Job name"),
    _s("reader_start_t", "SMF42NRST", "TME", 8, S1, "Reader start time"),
    _s("reader_start_d", "SMF42NRSD", "DTE", 12, S1, "Reader start date"),
    _s("user_id_field", "SMF42NUIF", "CHR8", 16, S1, "User identification"),
    _s("racf_user", "SMF42NUID", "CHR8", 24, S1, "RACF user ID"),
    _s("racf_group", "SMF42NCGP", "CHR8", 32, S1, "RACF connect group"),
    _s("record_version", "SMF42NVER", "CHR1", 40, S1, "Record version identifier"),
    _s(
        "activity_type",
        "SMF42NACT",
        "CHR1",
        41,
        S1,
        "Activity type (C/E/U/R/D create/extend/update/read/delete)",
    ),
    _s("security_type", "SMF42NSTP", "HEX1", 42, S1, "Security type (classification)"),
    _s("dsname", "SMF42NDSN", "CHR", 44, S1, "Data set name", length=44),
    _s("volser", "SMF42NVOL", "CHR", 88, S1, "Volume serial number", length=6),
    _s("device_type", "SMF42NUNT", "CHR8", 94, S1, "Device type"),
    _s("dataset_seq", "SMF42NDSQ", "DEC2", 102, S1, "Data set sequence number"),
    _s("volume_seq", "SMF42NVSQ", "DEC2", 104, S1, "Volume sequence number"),
]

# Subtype 24 — Member add/replace (PN1 @S1, alias @S2, user @S3)
_ST24 = [
    _s(
        "job_name",
        "SMF42PJB",
        "CHR8",
        0,
        S1,
        "Job / STC / TSO user who issued STOW add/replace or DESERV PUT",
    ),
    _s("step_name", "SMF42PST", "CHR8", 8, S1, "Step name"),
    _s("proc_name", "SMF42PPR", "CHR8", 16, S1, "Proc name (or blanks)"),
    _s("dsname", "SMF42PDS", "CHR", 24, S1, "Data set name", length=44),
    _s("volser", "SMF42PVS", "CHR", 68, S1, "Volume serial number", length=6),
    _s("member_name_len", "SMF42PML", "DEC2", 74, S1, "Length of member name added/replaced"),
    _s("member_flags", "SMF42PF1", "HEX1", 76, S1, "Flags (aliases truncated, new member, …)"),
    _s("member_name", "SMF42PMN", "VAR_CHR", 80, S1, "Member name that was added or replaced"),
    _s("alias_count", "SMF42PNA", "DEC2", 0, S2, "Number of alias names deleted in sympathy"),
    _s(
        "user_token",
        "SMF42PUI",
        "HEX",
        0,
        S3,
        "User information of STOW/DESERV caller (ICHRUTKN)",
        length=16,
    ),
]

# Subtype 25 — Member rename (QN1 @S1, old name @S2, user @S3)
_ST25 = [
    _s(
        "job_name",
        "SMF42QJB",
        "CHR8",
        0,
        S1,
        "Job / STC / TSO user who issued STOW rename or DESERV RENAME",
    ),
    _s("step_name", "SMF42QST", "CHR8", 8, S1, "Step name"),
    _s("proc_name", "SMF42QPR", "CHR8", 16, S1, "Proc name (or blanks)"),
    _s("dsname", "SMF42QDS", "CHR", 24, S1, "Data set name", length=44),
    _s("volser", "SMF42QVS", "CHR", 68, S1, "Volume serial number", length=6),
    _s("member_name_len", "SMF42QML", "DEC2", 74, S1, "Length of member name after rename"),
    _s("member_name", "SMF42QMN", "VAR_CHR", 76, S1, "Member name after the rename (new name)"),
    _s("old_member_name_len", "SMF42QOL", "DEC2", 0, S2, "Length of member name before rename"),
    _s("old_member_name", "SMF42QON", "VAR_CHR", 2, S2, "Member name before the rename (old name)"),
    _s(
        "user_token",
        "SMF42QUI",
        "HEX",
        0,
        S3,
        "User information of STOW/DESERV caller (ICHRUTKN)",
        length=16,
    ),
]

SECTION_FIELDS: dict[int, list[F]] = {
    20: _ST20,
    21: _ST21,
    22: _ST22,
    23: _ST23,
    24: _ST24,
    25: _ST25,
}

FIELDS_BY_SUBTYPE: dict[int, list[F]] = {
    sty: COMMON + list(sections) for sty, sections in SECTION_FIELDS.items()
}

__all__ = [
    "COMMON",
    "FIELDS_BY_SUBTYPE",
    "HEADER",
    "PRODUCT",
    "SECTION_FIELDS",
    "SUBTYPE_TITLES",
]
