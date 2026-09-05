"""SMF type 89 field map — port of MAP89.asm (header subset)."""

from __future__ import annotations

from ..types import FieldSpec as F

FIELDS = [
    F("smf_record_type", "SMF89RTY", "DEC1", 5, description="Record type (89)"),
    F("smf_system_id", "SMF89SID", "CHR4", 14, description="System identification (SID)"),
    F("time", "SMF89TME", "TME", 6, description="Time moved to SMF buffer"),
    F("date", "SMF89DTE", "DTE", 10, description="Date moved to SMF buffer"),
]
