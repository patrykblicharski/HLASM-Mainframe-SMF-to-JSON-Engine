"""SMF type 80 field map — port of MAP80.asm."""

from __future__ import annotations

from ..types import FieldSpec as F

FIELDS = [
    F("smf_record_type", "SMF80RTY", "DEC1", 5, description="Record type (80)"),
    F("smf_system_id", "SMF80SID", "CHR4", 14, description="System identification (SID)"),
    F("time", "SMF80TME", "TME", 6, description="Time moved to SMF buffer"),
    F("date", "SMF80DTE", "DTE", 10, description="Date moved to SMF buffer"),
    F("user_id", "SMF80USR", "CHR8", 22, description="RACF user ID"),
    F("group_name", "SMF80GRP", "CHR8", 30, description="RACF group name"),
    F(
        "old_resource",
        "SMF80REL",
        "RS_STR",
        38,
        tag=1,
        description="Relocate section tag 1 — old resource name",
    ),
    F(
        "class_name",
        "SMF80REL",
        "RS_STR",
        38,
        tag=17,
        description="Relocate section tag 17 — class name",
    ),
]
