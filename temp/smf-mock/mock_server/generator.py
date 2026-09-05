"""Schema-driven random SMF records from OpenAPI components/schemas."""
from __future__ import annotations

import random
import string
from datetime import date, datetime, timedelta
from typing import Any, Dict

_ALNUM = string.ascii_uppercase + string.digits


def _random_string(n: int = 8) -> str:
    return "".join(random.choice(_ALNUM) for _ in range(n))


def _random_date(base: date, spread_days: int = 30) -> date:
    return base - timedelta(days=random.randint(0, spread_days))


def _random_time_str(max_minutes: int = 24 * 60) -> str:
    total_seconds = random.uniform(0, max_minutes * 60)
    h = int(total_seconds // 3600)
    m = int((total_seconds % 3600) // 60)
    s = int(total_seconds % 60)
    micro = random.randint(0, 999999)
    # smfexplorer's DGDataParser accepts "%H:%M:%S.%f" or "%H:%M:%S"
    return f"{h:02d}:{m:02d}:{s:02d}.{micro:06d}"


def _random_datetime_str(base: date) -> str:
    d = _random_date(base)
    h, m, s, micro = (
        random.randint(0, 23),
        random.randint(0, 59),
        random.randint(0, 59),
        random.randint(0, 999999),
    )
    # datetime.fromisoformat()-compatible (used for discovery timestamps)
    return f"{d.isoformat()}T{h:02d}:{m:02d}:{s:02d}.{micro:06d}"


def _random_bit_string(n_bits: int) -> str:
    # BIN_STR must be literal '0'/'1' bits or smfexplorer flag fields decode as False.
    return "".join(random.choice("01") for _ in range(n_bits))


def _scalar_value(prop_def: Dict[str, Any], base_date: date) -> Any:
    prop_type = prop_def.get("type")
    fmt = prop_def.get("format")

    if prop_def.get("x-zml-datatype") == "BIN_STR":
        size_bytes = prop_def.get("x-zml-size") or 1
        return _random_bit_string(size_bytes * 8)
    if prop_type == "integer":
        # x-zml-datatype UNSIGNED never negative; keep everything
        # non-negative, it's realistic enough for counters/offsets/sizes.
        return random.randint(0, 100_000)
    if prop_type == "number":
        return round(random.uniform(0, 100_000), 3)
    if prop_type == "boolean":
        return random.choice([True, False])
    if prop_type == "string":
        if fmt == "date":
            return _random_date(base_date).isoformat()
        if fmt == "time":
            # Keep monitor durations short (TOD sub-fields < interval) so virtual CPU math stays non-negative.
            zml_type = prop_def.get("x-zml-datatype")
            max_minutes = 5 if zml_type == "TOD" else 30
            return _random_time_str(max_minutes=max_minutes)
        if fmt == "date-time":
            return _random_datetime_str(base_date)
        return _random_string(random.randint(3, 8))
    return None


class RecordGenerator:
    """Generates fake record instances for schemas from a loaded OpenAPI spec."""

    MAX_DEPTH = 6
    MULTI_SECTION_MIN = 1
    MULTI_SECTION_MAX = 3
    ARRAY_MIN = 2
    ARRAY_MAX = 4

    def __init__(self, schemas: Dict[str, Any]):
        self._schemas = schemas

    def _ref_name(self, ref: str) -> str:
        return ref.rsplit("/", 1)[-1]

    def generate(
        self, schema_name: str, base_date: date, depth: int = 0
    ) -> Dict[str, Any]:
        schema = self._schemas.get(schema_name)
        if schema is None or "properties" not in schema:
            return {}

        obj: Dict[str, Any] = {}
        for prop_name, prop_def in schema["properties"].items():
            obj[prop_name] = self._value_for_property(prop_def, base_date, depth)
        return obj

    def _value_for_property(
        self, prop_def: Dict[str, Any], base_date: date, depth: int
    ) -> Any:
        if depth >= self.MAX_DEPTH:
            return None

        if "$ref" in prop_def:
            return self.generate(self._ref_name(prop_def["$ref"]), base_date, depth + 1)

        additional = prop_def.get("additionalProperties")
        if isinstance(additional, dict):
            if "$ref" in additional:
                # multi-cardinality nested section -> indexed map of objects
                n = random.randint(self.MULTI_SECTION_MIN, self.MULTI_SECTION_MAX)
                return {
                    str(i): self.generate(
                        self._ref_name(additional["$ref"]), base_date, depth + 1
                    )
                    for i in range(n)
                }
            # "array" field (primitives) -> indexed map of scalars
            n = random.randint(self.ARRAY_MIN, self.ARRAY_MAX)
            return {str(i): _scalar_value(additional, base_date) for i in range(n)}

        return _scalar_value(prop_def, base_date)
