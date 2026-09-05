"""Layouts for SMF 119 subtype 51 (CSSMTP JES spool)."""
from __future__ import annotations

from ..layout import BYTES, CHAR, RES, U32, build_layout
from ..registry import SectionSlot

ML_CI = build_layout(
    "SMF119ML_CI",
    [
        CHAR("SMF119ML_CI_JOB", 8, "CSSMTP job name"),
        U32("SMF119ML_CI_Entry", "JES reader entry time (1/100 s)"),
        BYTES("SMF119ML_CI_EDate", 4, "JES reader entry date", decode="date_hex"),
        CHAR("SMF119ML_CI_USEID", 8, "User-defined identification"),
        CHAR("SMF119ML_CI_EXTWRT", 8, "External writer name"),
        CHAR("SMF119ML_CI_Jes", 4, "JES subsystem name"),
    ],
    description="SMF119ML_CI",
)

ML_SI = build_layout(
    "SMF119ML_SI",
    [
        CHAR("SMF119ML_SI_Job", 8, "Jobname"),
        U32("SMF119ML_SI_Entry", "JES reader entry time"),
        BYTES("SMF119ML_SI_EDate", 4, "JES reader entry date", decode="date_hex"),
        CHAR("SMF119ML_SI_USEID", 8, "User-defined identification"),
        CHAR("SMF119ML_SI_JobId", 8, "Job Id of selected job"),
        CHAR("SMF119ML_SI_SYS", 8, "System name where job output was created"),
        CHAR("SMF119ML_SI_XEQ", 8, "NJE node where job executed"),
        CHAR("SMF119ML_SI_CRER", 8, "Owning user id of data set"),
        U32("SMF119ML_SI_TKID", "JES task ID"),
        U32("SMF119ML_SI_Jnum", "JES job number"),
        U32("SMF119ML_SI_Dsky", "JES dataset key"),
        U32("SMF119ML_SI_Dsnm", "JES dataset number"),
    ],
    description="SMF119ML_SI",
)

ML_SJ = build_layout(
    "SMF119ML_SJ",
    [
        U32("SMF119ML_SJEvent", "Spool job event type"),
        RES("SMF119ML_SJPad", 4),
        CHAR("SMF119ML_SJJob", 8, "Spool job name"),
        CHAR("SMF119ML_SJJobId", 8, "Spool job id"),
        CHAR("SMF119ML_SJClass", 1, "Output class"),
        RES("SMF119ML_SJRsv", 3),
        U32("SMF119ML_SJRecs", "Record count"),
        U32("SMF119ML_SJBytes", "Byte count"),
        CHAR("SMF119ML_SJDest", 8, "DEST"),
        CHAR("SMF119ML_SJWriter", 8, "External writer"),
    ],
    description="SMF119ML_SJ",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key="S1", layout=ML_CI),
    SectionSlot(triplet_index=2, key="S2", layout=ML_SI),
    SectionSlot(triplet_index=3, key="S3", layout=ML_SJ),
]

__all__ = ["ML_CI", "ML_SI", "ML_SJ", "SECTION_SLOTS"]
