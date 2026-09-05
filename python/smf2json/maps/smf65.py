"""SMF type 65 — ICF DELETE activity (IBM / PACSYS smf65).

Self-defining header with product (POF) and data (DOF) triplets.
Product section fields use absolute offsets for the common layout
where SMF65POF == 40 (VER through NNM). Catalog record (SMF65CRC)
is not mapped.
"""

from __future__ import annotations

from ..types import FieldSpec as F


def _h(key, ibm, ftype, off, desc, length=None):
    return F(key, ibm, ftype, off, None, length=length, description=desc)


FIELDS = [
    _h("smf_sys_flag", "SMF65SYS", "HEX1", 4, "System indicator flags"),
    _h("smf_record_type", "SMF65RTY", "DEC1", 5, "Record type 65 (X'41')"),
    _h("time", "SMF65TME", "TME", 6, "Time record moved to SMF buffer (HH:MM:SS)"),
    _h("date", "SMF65DTE", "DTE", 10, "Date record moved to SMF buffer (YYYY-MM-DD)"),
    _h("smf_system_id", "SMF65CPU", "CHR4", 14, "System identification (SID)"),
    _h(
        "catalog_action",
        "SMF65SUB",
        "CHR2",
        22,
        "Action on catalog entry (IN=insert, DE=delete, UP=update)",
    ),
    _h("product_offset", "SMF65POF", "DEC4", 24, "Offset of product section from RDW start"),
    _h("product_length", "SMF65PLN", "DEC2", 28, "Length of product section"),
    _h("product_number", "SMF65PNO", "DEC2", 30, "Number of product sections"),
    _h("data_offset", "SMF65DOF", "DEC4", 32, "Offset of data section from RDW start"),
    _h("data_length", "SMF65DLN", "DEC2", 36, "Length of data section"),
    _h("data_number", "SMF65DNO", "DEC2", 38, "Number of data sections"),
    # Product section @40 when POF=40
    _h("record_version", "SMF65VER", "CHR2", 40, "Version of the type 65 record"),
    _h("product_name", "SMF65PNM", "CHR8", 42, "Catalog management product identifier"),
    _h("job_name", "SMF65JNM", "CHR8", 50, "Job name (job log identification)"),
    _h("reader_start_t", "SMF65RST", "TME", 58, "Reader recognized JOB card — time"),
    _h("reader_start_d", "SMF65RDT", "DTE", 62, "Reader recognized JOB card — date"),
    _h(
        "user_id_field",
        "SMF65UID",
        "CHR8",
        66,
        "User-defined identification (common exit area)",
    ),
    _h(
        "function_indicator",
        "SMF65FNC",
        "CHR1",
        74,
        "S=data set scratched; U=catalog entries only modified",
    ),
    _h(
        "catalog_name",
        "SMF65CNM",
        "CHR",
        75,
        "Name of catalog in which record was updated or deleted",
        length=44,
    ),
    _h("entry_type", "SMF65TYP", "CHR1", 119, "Catalog entry type identifier"),
    _h("entry_name", "SMF65ENM", "CHR", 120, "Catalog entry name", length=44),
]
