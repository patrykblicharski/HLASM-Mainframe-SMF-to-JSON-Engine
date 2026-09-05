"""Map registry."""

from .smf30 import FIELDS as SMF30_FIELDS
from .smf80 import FIELDS as SMF80_FIELDS
from .smf89 import FIELDS as SMF89_FIELDS

MAPS_BY_TYPE = {
    30: SMF30_FIELDS,
    80: SMF80_FIELDS,
    89: SMF89_FIELDS,
}
