"""SMF type 92 — File system activity (z/OS UNIX / OMVS).

Layouts from PACSYS https://www.pacsys.com/smf/smf92.htm and IBM
*Record type 92 (X'5C') — File system activity*.

Self-defining triplets: subsystem ``SMF92SOF`` @28, identification
``SMF92IOF`` @36, data ``SMF92DOF`` @44. Register via
``MAPS_BY_SUBTYPE[(92, sty)]``.

Mapped subtypes (USS file activity): 1, 2, 4, 5, 6, 7, 10–17.
zFS performance subtypes 50–57 are not mapped yet.
"""

from __future__ import annotations

from ..types import FieldSpec as F

SOF, IOF, DOF = 28, 36, 44


def _h(key, ibm, ftype, off, desc, length=None):
    return F(key, ibm, ftype, off, None, length=length, description=desc)


def _s(key, ibm, ftype, off, trip, desc, length=None):
    return F(key, ibm, ftype, off, trip, length=length, description=desc)


HEADER = [
    _h("smf_sys_flag", "SMF92FLG", "HEX1", 4, "Header flag byte (subtypes used, …)"),
    _h("smf_record_type", "SMF92RTY", "DEC1", 5, "Record type 92 (X'5C')"),
    _h("time", "SMF92TME", "TME", 6, "Time record moved to SMF buffer"),
    _h("date", "SMF92DTE", "DTE", 10, "Date record moved to SMF buffer"),
    _h("smf_system_id", "SMF92SID", "CHR4", 14, "System identification (SID)"),
    _h("smf_subsystem_id", "SMF92WID", "CHR4", 18, "Subsystem identification"),
    _h("smf_subtype", "SMF92STP", "DEC2", 22, "Record subtype"),
]

SUBSYSTEM = [
    _s("subtype_id", "SMF92TYP", "DEC2", 0, SOF, "Subtype identification (echo)"),
    _s("record_version", "SMF92RVN", "CHR2", 2, SOF, "Record version number"),
    _s("product_name", "SMF92PNM", "CHR8", 4, SOF, "Product name (OpenMVS / OMVS)"),
    _s("os_level", "SMF92OSL", "CHR8", 12, SOF, "MVS product level"),
]

IDENTIFICATION = [
    _s("job_name", "SMF92JBN", "CHR8", 0, IOF, "Job name"),
    _s("reader_start_t", "SMF92RST", "TME", 8, IOF, "Reader start time"),
    _s("reader_start_d", "SMF92RSD", "DTE", 12, IOF, "Reader start date"),
    _s("step_name", "SMF92STM", "CHR8", 16, IOF, "Step name"),
    _s("saf_group", "SMF92RGD", "CHR8", 24, IOF, "SAF group ID"),
    _s("saf_user", "SMF92RUD", "CHR8", 32, IOF, "SAF user ID"),
    _s("omvs_uid", "SMF92UID", "DEC4", 40, IOF, "z/OS UNIX real user ID"),
    _s("omvs_gid", "SMF92GID", "DEC4", 44, IOF, "z/OS UNIX real group ID"),
    _s("omvs_pid", "SMF92PID", "DEC4", 48, IOF, "z/OS UNIX process ID"),
    _s("omvs_pgid", "SMF92PGD", "DEC4", 52, IOF, "z/OS UNIX process group ID"),
    _s("omvs_sid", "SMF92SSD", "DEC4", 56, IOF, "z/OS UNIX session ID"),
    _s("omvs_anchor_pid", "SMF92API", "DEC4", 60, IOF, "z/OS UNIX anchor process ID"),
    _s("omvs_anchor_pgid", "SMF92APG", "DEC4", 64, IOF, "z/OS UNIX anchor process group ID"),
    _s("omvs_anchor_sid", "SMF92ASG", "DEC4", 68, IOF, "z/OS UNIX anchor session ID"),
]

COMMON = HEADER + SUBSYSTEM + IDENTIFICATION

SUBTYPE_TITLES = {
    1: "File system mount",
    2: "File system quiesce (suspend)",
    4: "File system unquiesce (resume)",
    5: "File system unmount",
    6: "File system remount",
    7: "File system move",
    10: "File open",
    11: "File close",
    12: "MMAP",
    13: "MUNMAP",
    14: "File delete or rename",
    15: "Security attribute change",
    16: "Socket / special file / pipe / FIFO close",
    17: "File access count (interval)",
}

# --- data sections (relative to SMF92DOF) ---

_ST1 = [
    _s("event_stck", "SMF92MTM", "HEX8", 0, DOF, "Time of mount (STCK)"),
    _s("path_offset", "SMF92MPF", "DEC4", 8, DOF, "Offset of path section from record start"),
    _s("fs_type", "SMF92MFT", "DEC4", 12, DOF, "File system type (BPXYMNTE)"),
    _s("fs_mode", "SMF92MFM", "DEC4", 16, DOF, "File system mode (BPXYMNTE)"),
    _s("fs_device", "SMF92MDN", "DEC4", 20, DOF, "File system device number"),
    _s("ddname", "SMF92MDD", "CHR8", 24, DOF, "DDNAME specified on mount"),
    _s("fs_type_name", "SMF92MTN", "CHR8", 32, DOF, "File system type name"),
    _s("fs_name", "SMF92MFN", "CHR", 40, DOF, "File system name", length=44),
    _s("fs_blocksize", "SMF92MBL", "DEC4", 84, DOF, "File system block size"),
    _s("fs_space_total", "SMF92MST", "DEC8", 88, DOF, "Total space (block-size units)"),
    _s("fs_space_used", "SMF92MSU", "DEC8", 96, DOF, "Allocated space (block-size units)"),
    _s("mount_flags", "SMF92MFG", "HEX1", 104, DOF, "Mount flags (automount / async)"),
    _s("mount_flags_2", "SMF92MF2", "HEX1", 105, DOF, "Local/remote / sysplex owner flags"),
]

_ST2 = [
    _s("event_stck", "SMF92STS", "HEX8", 0, DOF, "Time of suspend (STCK)"),
    _s("fs_type", "SMF92SFT", "DEC4", 8, DOF, "File system type"),
    _s("fs_mode", "SMF92SFM", "DEC4", 12, DOF, "File system mode"),
    _s("fs_device", "SMF92SDN", "DEC4", 16, DOF, "File system device number"),
    _s("ddname", "SMF92SDD", "CHR8", 20, DOF, "DDNAME specified on mount"),
    _s("fs_type_name", "SMF92STN", "CHR8", 28, DOF, "File system type name"),
    _s("fs_name", "SMF92SFN", "CHR", 36, DOF, "File system name", length=44),
    _s("quiesce_flags", "SMF92SFG", "HEX1", 80, DOF, "Local/remote / sysplex flags"),
]

_ST4 = [
    _s("suspend_stck", "SMF92RTS", "HEX8", 0, DOF, "Time of suspend (STCK)"),
    _s("resume_stck", "SMF92RTR", "HEX8", 8, DOF, "Time of resume (STCK)"),
    _s("fs_type", "SMF92RFT", "DEC4", 16, DOF, "File system type"),
    _s("fs_mode", "SMF92RFM", "DEC4", 20, DOF, "File system mode"),
    _s("fs_device", "SMF92RDN", "DEC4", 24, DOF, "File system device number"),
    _s("ddname", "SMF92RDD", "CHR8", 28, DOF, "DDNAME specified on mount"),
    _s("fs_type_name", "SMF92RTN", "CHR8", 36, DOF, "File system type name"),
    _s("fs_name", "SMF92RFN", "CHR", 44, DOF, "File system name", length=44),
    _s("resume_flags", "SMF92RFG", "HEX1", 88, DOF, "Local/remote / sysplex flags"),
]

_ST5_6 = [
    _s("mount_stck", "SMF92UTM", "HEX8", 0, DOF, "Time of mount (STCK)"),
    _s("unmount_stck", "SMF92UTU", "HEX8", 8, DOF, "Time of unmount (STCK)"),
    _s("fs_type", "SMF92UFT", "DEC4", 16, DOF, "File system type"),
    _s("fs_mode", "SMF92UFM", "DEC4", 20, DOF, "File system mode"),
    _s("fs_device", "SMF92UDN", "DEC4", 24, DOF, "File system device number"),
    _s("ddname", "SMF92UDD", "CHR8", 28, DOF, "DDNAME specified on mount"),
    _s("fs_type_name", "SMF92UTN", "CHR8", 36, DOF, "File system type name"),
    _s("fs_name", "SMF92UFN", "CHR", 44, DOF, "File system name", length=44),
    _s("fs_blocksize", "SMF92UBL", "DEC4", 88, DOF, "File system block size"),
    _s("fs_space_total", "SMF92UST", "DEC8", 92, DOF, "Total space (block-size units)"),
    _s("fs_space_used", "SMF92USU", "DEC8", 100, DOF, "Allocated space (block-size units)"),
    _s("read_calls", "SMF92USR", "DEC4", 108, DOF, "Read calls to mounted file system"),
    _s("write_calls", "SMF92USW", "DEC4", 112, DOF, "Write calls to mounted file system"),
    _s("dir_io_blocks", "SMF92UDI", "DEC4", 116, DOF, "Directory I/O blocks"),
    _s("io_blocks_read", "SMF92UIR", "DEC4", 120, DOF, "I/O blocks read"),
    _s("io_blocks_written", "SMF92UIW", "DEC4", 124, DOF, "I/O blocks written"),
    _s("bytes_read", "SMF92UBR", "DEC8", 128, DOF, "Bytes read"),
    _s("bytes_written", "SMF92UBW", "DEC8", 136, DOF, "Bytes written"),
    _s("unmount_flags", "SMF92UFG", "HEX1", 144, DOF, "Unmount flags (automount, …)"),
    _s("unmount_flags_2", "SMF92UF2", "HEX1", 145, DOF, "Local/remote / sysplex flags"),
]

_ST7 = [
    _s("move_stck", "SMF92VTV", "HEX8", 0, DOF, "Time of move (STCK)"),
    _s("mount_stck", "SMF92VTM", "HEX8", 8, DOF, "Time of mount (STCK)"),
    _s("fs_type", "SMF92VFT", "DEC4", 16, DOF, "File system type"),
    _s("fs_mode", "SMF92VFM", "DEC4", 20, DOF, "File system mode"),
    _s("fs_device", "SMF92VDN", "DEC4", 24, DOF, "File system device number"),
    _s("ddname", "SMF92VDD", "CHR8", 28, DOF, "DDNAME specified on mount"),
    _s("fs_type_name", "SMF92VTN", "CHR8", 36, DOF, "File system type name"),
    _s("fs_name", "SMF92VNM", "CHR", 44, DOF, "File system name", length=44),
    _s("fs_blocksize", "SMF92VBL", "DEC4", 88, DOF, "File system block size"),
    _s("fs_space_total", "SMF92VST", "DEC8", 92, DOF, "Total space (block-size units)"),
    _s("fs_space_used", "SMF92VSU", "DEC8", 100, DOF, "Allocated space (block-size units)"),
    _s("read_calls", "SMF92VSR", "DEC4", 108, DOF, "Read calls"),
    _s("write_calls", "SMF92VSW", "DEC4", 112, DOF, "Write calls"),
    _s("dir_io_blocks", "SMF92VDI", "DEC4", 116, DOF, "Directory I/O blocks"),
    _s("io_blocks_read", "SMF92VIR", "DEC4", 120, DOF, "I/O blocks read"),
    _s("io_blocks_written", "SMF92VIW", "DEC4", 124, DOF, "I/O blocks written"),
    _s("bytes_read", "SMF92VBR", "DEC8", 132, DOF, "Bytes read"),
    _s("bytes_written", "SMF92VBW", "DEC8", 140, DOF, "Bytes written"),
    _s("move_reason_flags", "SMF92VFG", "HEX1", 148, DOF, "Reason for move"),
    _s("old_status_flags", "SMF92VOF", "HEX1", 149, DOF, "Old status flags"),
    _s("new_status_flags", "SMF92VNF", "HEX1", 150, DOF, "New status flags"),
]

_ST10 = [
    _s("open_stck", "SMF92OTO", "HEX8", 0, DOF, "Time of open (STCK)"),
    _s("file_type", "SMF92OTY", "HEX1", 8, DOF, "File type (BPXYFTYP)"),
    _s("open_flags", "SMF92OFG", "HEX1", 9, DOF, "Record flag byte"),
    _s("file_token", "SMF92OTK", "DEC4", 12, DOF, "Open file token (matches close)"),
    _s("file_inode", "SMF92OIN", "DEC4", 16, DOF, "File serial number (inode)"),
    _s("fs_device", "SMF92ODN", "DEC4", 20, DOF, "Unique device number for the file"),
]

_ST11 = [
    _s("open_stck", "SMF92CTO", "HEX8", 0, DOF, "Time of open (STCK)"),
    _s("close_stck", "SMF92CTC", "HEX8", 8, DOF, "Time of close (STCK)"),
    _s("file_type", "SMF92CTY", "HEX1", 16, DOF, "File type (BPXYFTYP)"),
    _s("close_flags", "SMF92CFG", "HEX1", 17, DOF, "Record flag byte"),
    _s("file_token", "SMF92CTK", "DEC4", 20, DOF, "Open file token"),
    _s("file_inode", "SMF92CIN", "DEC4", 24, DOF, "File serial number (inode)"),
    _s("fs_device", "SMF92CDN", "DEC4", 28, DOF, "Unique device number for the file"),
    _s("read_calls", "SMF92CSR", "DEC4", 32, DOF, "Read calls issued to the file"),
    _s("write_calls", "SMF92CSW", "DEC4", 36, DOF, "Write calls issued to the file"),
    _s("dir_io_blocks", "SMF92CDI", "DEC4", 40, DOF, "Directory I/O blocks"),
    _s("io_blocks_read", "SMF92CIR", "DEC4", 44, DOF, "I/O blocks read"),
    _s("io_blocks_written", "SMF92CIW", "DEC4", 48, DOF, "I/O blocks written"),
    _s("bytes_read", "SMF92CBR", "DEC8", 52, DOF, "Bytes read"),
    _s("bytes_written", "SMF92CBW", "DEC8", 60, DOF, "Bytes written"),
    _s("pathname", "SMF92CPN", "CHR", 68, DOF, "Pathname at open (last 64 chars if longer)", length=64),
]

_ST12 = [
    _s("mmap_stck", "SMF92MTO", "HEX8", 0, DOF, "Time of mmap (STCK)"),
    _s("mmap_bytes", "SMF92MSZ", "DEC4", 8, DOF, "Number of bytes memory-mapped"),
    _s("file_token", "SMF92MTK", "DEC4", 12, DOF, "mmap file token (matches munmap)"),
    _s("file_inode", "SMF92MIN", "DEC4", 16, DOF, "File serial number"),
    _s("fs_device", "SMF92MMDN", "DEC4", 20, DOF, "File unique device number"),
]

_ST13 = [
    _s("mmap_stck", "SMF92MUTO", "HEX8", 0, DOF, "Time of mmap (STCK)"),
    _s("munmap_stck", "SMF92MUTC", "HEX8", 8, DOF, "Time of munmap (STCK)"),
    _s("mmap_bytes", "SMF92MUSZ", "DEC4", 16, DOF, "Number of bytes memory-mapped"),
    _s("file_token", "SMF92MUTK", "DEC4", 20, DOF, "mmap file token"),
    _s("file_inode", "SMF92MUIN", "DEC4", 24, DOF, "File serial number"),
    _s("fs_device", "SMF92MUDN", "DEC4", 28, DOF, "File unique device number"),
    _s("io_blocks_read", "SMF92MUIR", "DEC4", 32, DOF, "I/O blocks read"),
    _s("io_blocks_written", "SMF92MUIW", "DEC4", 36, DOF, "I/O blocks written"),
]

_ST14 = [
    _s("event_stck", "SMF92DFT", "HEX8", 0, DOF, "Time of delete/rename (STCK)"),
    _s("file_type", "SMF92DTY", "HEX1", 8, DOF, "File type (BPXYFTYP)"),
    _s("delete_flags", "SMF92DFLG", "HEX1", 9, DOF, "Bit flags"),
    _s("file_inode", "SMF92DIN", "DEC4", 12, DOF, "File serial number"),
    _s("parent_inode", "SMF92DINP", "DEC4", 16, DOF, "Parent directory serial number"),
    _s("fs_device", "SMF92DDN", "DEC4", 20, DOF, "Unique device number"),
    _s("fs_name", "SMF92DFS", "CHR", 24, DOF, "File system name", length=44),
    _s("file_name_len", "SMF92DNL", "DEC4", 68, DOF, "Length of deleted/renamed file name"),
    _s("file_name", "SMF92DFN", "CHR", 72, DOF, "Name of file deleted or renamed", length=64),
    _s("new_name_len", "SMF92DNLR", "DEC4", 136, DOF, "Length of new name (rename)"),
    _s("new_file_name", "SMF92DFNR", "CHR", 140, DOF, "New name after rename", length=64),
]

_ST15 = [
    _s("change_stck", "SMF92ACT", "HEX8", 0, DOF, "Time of security attribute change (STCK)"),
    _s("file_type", "SMF92ATY", "HEX1", 8, DOF, "File type (BPXYFTYP)"),
    _s("attr_flags", "SMF92AFLG", "HEX1", 9, DOF, "Flags"),
    _s("file_inode", "SMF92AIN", "DEC4", 12, DOF, "File inode number"),
    _s("fs_device", "SMF92ADN", "DEC4", 16, DOF, "File system device number"),
    _s("fs_name", "SMF92AFS", "CHR", 20, DOF, "File system name", length=44),
    _s("old_gen_value", "SMF92AOLDGENVAL", "HEX4", 64, DOF, "Original st_GenValue (BPXYSTAT)"),
    _s("old_sec_attrs", "SMF92AOLDSECATTRSC", "CHR4", 68, DOF, "Original security flags (A/P/S form)"),
    _s("new_gen_value", "SMF92ANEWGENVAL", "HEX4", 72, DOF, "New st_GenValue after change"),
    _s("new_sec_attrs", "SMF92ANEWSECATTRSC", "CHR4", 76, DOF, "New security flags (A/P/S form)"),
    _s("owner_uid", "SMF92AOWNUID", "DEC4", 80, DOF, "File owner user ID"),
    _s("owner_gid", "SMF92AOWNGID", "DEC4", 84, DOF, "File owner GID"),
    _s("security_label", "SMF92ASECLABEL", "CHR8", 88, DOF, "File security label"),
    _s("audit_file_id", "SMF92AAUDITFID", "CHR", 96, DOF, "RACF file ID (audit)", length=16),
    _s("getcwd_rc", "SMF92ACWDRC", "DEC4", 132, DOF, "getcwd return code (0 = absolute path)"),
    _s("getcwd_rsn", "SMF92ACWDRSN", "DEC4", 136, DOF, "getcwd reason code"),
    _s("path_name_len", "SMF92APNL", "DEC4", 140, DOF, "Length of file path name"),
]

_ST16 = [
    _s("reserved", "SMF92SUB16", "HEX8", 0, DOF, "Reserved / subtype-16 close placeholder"),
]

_ST17 = [
    _s("interval_stck", "SMF92FAWT", "HEX8", 0, DOF, "Interval / release time (STCK)"),
    _s("access_flags", "SMF92FAFG", "HEX1", 8, DOF, "Record flag byte (interval bit, …)"),
    _s("file_inode", "SMF92FAIN", "DEC4", 12, DOF, "Inode number"),
    _s("fs_device", "SMF92FADN", "DEC4", 16, DOF, "Unique device number"),
    _s("access_count", "SMF92FATI", "DEC4", 20, DOF, "Total accesses during interval"),
    _s("pathname", "SMF92FAPN", "CHR", 24, DOF, "Path name if known", length=64),
]

SECTION_FIELDS: dict[int, list[F]] = {
    1: list(_ST1),
    2: list(_ST2),
    4: list(_ST4),
    5: list(_ST5_6),
    6: list(_ST5_6),
    7: list(_ST7),
    10: list(_ST10),
    11: list(_ST11),
    12: list(_ST12),
    13: list(_ST13),
    14: list(_ST14),
    15: list(_ST15),
    16: list(_ST16),
    17: list(_ST17),
}

FIELDS_BY_SUBTYPE: dict[int, list[F]] = {
    sty: COMMON + list(sections) for sty, sections in SECTION_FIELDS.items()
}

FIELDS = FIELDS_BY_SUBTYPE[11]

__all__ = [
    "COMMON",
    "FIELDS",
    "FIELDS_BY_SUBTYPE",
    "SECTION_FIELDS",
    "SUBTYPE_TITLES",
]
