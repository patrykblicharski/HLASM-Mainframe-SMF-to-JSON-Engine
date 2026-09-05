"""Map registry — by record type, or (type, subtype) when layouts differ."""

from __future__ import annotations

from typing import Optional, Sequence

from ..types import FieldSpec
from .smf30 import FIELDS as SMF30_FIELDS
from .smf80 import FIELDS as SMF80_FIELDS
from .smf89 import FIELDS as SMF89_FIELDS
from .smf119 import FIELDS_BY_SUBTYPE as SMF119_FIELDS

MAPS_BY_TYPE = {
    30: SMF30_FIELDS,
    80: SMF80_FIELDS,
    89: SMF89_FIELDS,
}

MAPS_BY_SUBTYPE = {(119, sty): fields for sty, fields in SMF119_FIELDS.items()}


def fields_for(record_type: int, subtype: Optional[int] = None) -> Sequence[FieldSpec]:
    if subtype is not None:
        mapped = MAPS_BY_SUBTYPE.get((record_type, subtype))
        if mapped is not None:
            return mapped
        if any(rty == record_type for rty, _sty in MAPS_BY_SUBTYPE):
            return ()
    return MAPS_BY_TYPE.get(record_type, ())
