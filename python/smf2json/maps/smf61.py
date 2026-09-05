"""SMF type 61 — ICF DEFINE activity (IBM / PACSYS smf61).

Self-defining header with product (POF) and data (DOF) triplets.
Product section fields use absolute offsets for the common layout
where SMF61POF == 40 (VER through NNM). Catalog record (SMF61CRC)
is not mapped.
"""

from __future__ import annotations

from ..types import FieldSpec as F


def _h(key, ibm, ftype, off, desc, length=None):
    return F(key, ibm, ftype, off, None, length=length, description=desc)


FIELDS = [
    _h("smf_sys_flag", "SMF61SYS", "HEX1", 4, "System indicator flags"),
    _h("smf_record_type", "SMF61RTY", "DEC1", 5, "Record type 61 (X'3D')"),
    _h("time", "SMF61TME", "TME", 6, "Time record moved to SMF buffer (HH:MM:SS)"),
    _h("date", "SMF61DTE", "DTE", 10, "Date record moved to SMF buffer (YYYY-MM-DD)"),
    _h("smf_system_id", "SMF61CPU", "CHR4", 14, "System identification (SID)"),
    _h(
        "catalog_action",
        "SMF61SUB",
        "CHR2",
        22,
        "Action on catalog entry (IN=insert, DE=delete, UP=update)",
    ),
    _h("product_offset", "SMF61POF", "DEC4", 24, "Offset of product section from RDW start"),
    _h("product_length", "SMF61PLN", "DEC2", 28, "Length of product section"),
    _h("product_number", "SMF61PNO", "DEC2", 30, "Number of product sections"),
    _h("data_offset", "SMF61DOF", "DEC4", 32, "Offset of data section from RDW start"),
    _h("data_length", "SMF61DLN", "DEC2", 36, "Length of data section"),
    _h("data_number", "SMF61DNO", "DEC2", 38, "Number of data sections"),
    # Product section @40 when POF=40
    _h("record_version", "SMF61VER", "CHR2", 40, "Version of the type 61 record"),
    _h("product_name", "SMF61PNM", "CHR8", 42, "Catalog management product identifier"),
    _h("job_name", "SMF61JNM", "CHR8", 50, "Job name (job log identification)"),
    _h("reader_start_t", "SMF61RST", "TME", 58, "Reader recognized JOB card — time"),
    _h("reader_start_d", "SMF61RDT", "DTE", 62, "Reader recognized JOB card — date"),
    _h(
        "user_id_field",
        "SMF61UID",
        "CHR8",
        66,
        "User-defined identification (common exit area)",
    ),
    _h("function_indicator", "SMF61FNC", "HEX1", 74, "Reserved for type 61"),
    _h(
        "catalog_name",
        "SMF61CNM",
        "CHR",
        75,
        "Name of catalog in which entry is defined",
        length=44,
    ),
    _h("entry_type", "SMF61TYP", "CHR1", 119, "Catalog entry type identifier"),
    _h("entry_name", "SMF61ENM", "CHR", 120, "Catalog entry name", length=44),
]
