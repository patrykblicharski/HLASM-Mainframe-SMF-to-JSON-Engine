"""Map registry — by record type, or (type, subtype) when layouts differ."""

from __future__ import annotations

from typing import Optional, Sequence

from ..types import FieldSpec
from .smf14 import FIELDS as SMF14_FIELDS
from .smf15 import FIELDS as SMF15_FIELDS
from .smf17 import FIELDS as SMF17_FIELDS
from .smf30 import FIELDS_BY_SUBTYPE as SMF30_FIELDS
from .smf42 import FIELDS_BY_SUBTYPE as SMF42_FIELDS
from .smf61 import FIELDS as SMF61_FIELDS
from .smf65 import FIELDS as SMF65_FIELDS
from .smf66 import FIELDS as SMF66_FIELDS
from .smf80 import FIELDS as SMF80_FIELDS
from .smf89 import FIELDS as SMF89_FIELDS
from .smf119 import FIELDS_BY_SUBTYPE as SMF119_FIELDS

MAPS_BY_TYPE = {
    14: SMF14_FIELDS,
    15: SMF15_FIELDS,
    17: SMF17_FIELDS,
    61: SMF61_FIELDS,
    65: SMF65_FIELDS,
    66: SMF66_FIELDS,
    80: SMF80_FIELDS,
    89: SMF89_FIELDS,
}

MAPS_BY_SUBTYPE = {
    **{(30, sty): fields for sty, fields in SMF30_FIELDS.items()},
    **{(42, sty): fields for sty, fields in SMF42_FIELDS.items()},
    **{(119, sty): fields for sty, fields in SMF119_FIELDS.items()},
}


def fields_for(record_type: int, subtype: Optional[int] = None) -> Sequence[FieldSpec]:
    if subtype is not None:
        mapped = MAPS_BY_SUBTYPE.get((record_type, subtype))
        if mapped is not None:
            return mapped
        if any(rty == record_type for rty, _sty in MAPS_BY_SUBTYPE):
            return ()
    return MAPS_BY_TYPE.get(record_type, ())
