"""Auto-generated layouts for SMF 119 subtype 50 (from PACSYS offset tables)."""
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

ML_S1 = build_layout(
    "SMF119ML_S1",
    [
        BYTES("SMF119ML_SI", 72, "Spool Identification"),
    ],
    description="SMF119ML_S1",
)

ML_S2 = build_layout(
    "SMF119ML_S2",
    [
        CHAR("SMF119ML_SI_Job", 8, "Jobname"),
        U32("SMF119ML_SI_Entry", "JES reader entry time - time since midnight, in hundredths of a second, that the reader recognized the JOB card (for this job)."),
        BYTES("SMF119ML_SI_EDate", 4, "JES reader entry date 0CYYDDDF - date when the reader recognized the JOB card (for this job), in the form 0cyydddF.", decode="date_hex"),
        CHAR("SMF119ML_SI_USEID", 8, "User-defined identification field (taken from common exit parameter area, not from USER=parameter on job statement)."),
        CHAR("SMF119ML_SI_JobId", 8, "Job Id of selected job"),
        CHAR("SMF119ML_SI_SYS", 8, "System name of the MVS™ image where the job output was created"),
        CHAR("SMF119ML_SI_XEQ", 8, "NJE node where job executed"),
        CHAR("SMF119ML_SI_CRER", 8, "Owning user id of data set"),
        U32("SMF119ML_SI_TKID", "JES task ID"),
        U32("SMF119ML_SI_Jnum", "JES job number in binary"),
        U32("SMF119ML_SI_Dsky", "JES dataset key"),
        U32("SMF119ML_SI_Dsnm", "JES dataset number"),
    ],
    description="SMF119ML_S2",
)

ML_S3 = build_layout(
    "SMF119ML_S3",
    [
        BYTES("SMF119ML_MI", 60, "Mail Identification 0 0 SMF119ML_MI_STime 4 Binary Time mail was read from JES - Hundredths of seconds"),
    ],
    description="SMF119ML_S3",
)

ML_S4 = build_layout(
    "SMF119ML_S4",
    [
        U16("SMF119ML_MH_Len", "Mail header length"),
        U16("SMF119ML_MH_Key", "Mail header type value"),
        CHAR("SMF119ML_MH_Data", 255, "Mail header data string"),
    ],
    description="SMF119ML_S4",
)

SECTION_SLOTS = [
    SectionSlot(triplet_index=1, key='S1', layout=ML_S1),
    SectionSlot(triplet_index=2, key='S2', layout=ML_S2),
    SectionSlot(triplet_index=3, key='S3', layout=ML_S3),
    SectionSlot(triplet_index=4, key='S4', layout=ML_S4),
]

__all__ = ['ML_S1', 'ML_S2', 'ML_S3', 'ML_S4', "SECTION_SLOTS"]
