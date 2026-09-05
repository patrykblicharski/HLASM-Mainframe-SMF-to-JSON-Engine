"""Column metadata for decoded SMF tables (labels/descriptions from OpenAPI)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .catalog import openapi_root_name
from .decode import load_openapi_schemas

# Same first-pass curation rule as smf-explorer-app/scripts/generate_catalog.py
DEFAULT_COLUMN_LIMIT = 12

# Always-useful synthetic columns (not from OpenAPI root leafs).
_HEADER_COLUMNS: list[tuple[str, str, str, bool]] = [
    ("_offset", "File offset", "Byte offset of this record in the dump file.", True),
    ("SMF_SID", "System ID", "SMF system identifier (SID) from the standard header.", True),
    ("SMF_SSI", "Subsystem ID", "SMF subsystem identifier (SSI) from the standard header.", True),
    ("SMF_RTY", "Record type", "SMF record type number.", True),
    ("SMF_STY", "Subtype", "SMF record subtype number.", True),
    ("SMF_TME", "Time", "Record written time (hh:mm:ss.xx since midnight).", True),
    ("SMF_DTE_RAW", "Date (raw)", "Record written date (packed, hex).", False),
    ("SMF_LEN", "Record length", "SMF record length from the standard header.", False),
    ("SMF_FLG", "Header flags", "SMF header flag byte as bit string.", False),
    ("SMF_SEG", "Segment", "SMF segment descriptor.", False),
    ("_length", "Bytes read", "Number of bytes read for this record from the dump.", False),
]


@dataclass(frozen=True)
class ColumnSpec:
    key: str
    label: str
    description: str
    default: bool = True


def _friendly_label(field_name: str, description: str | None) -> str:
    """Prefer OpenAPI description; fall back to a cleaned field name."""
    desc = (description or "").strip()
    if desc:
        # One-line label for the table header.
        first = desc.split("\n", 1)[0].strip()
        if len(first) > 48:
            first = first[:45].rstrip() + "…"
        return first
    # SMF79LEN -> SMF79LEN (keep technical name if no description)
    return field_name


def _is_leaf_prop(prop: dict[str, Any]) -> bool:
    if "$ref" in prop:
        return False
    if prop.get("type") == "object" or "additionalProperties" in prop:
        return False
    return True


def column_specs_for(smf_type: int, subtype: int) -> list[ColumnSpec]:
    """Build column list: synthetic header fields + OpenAPI root leafs.

    Default visibility: synthetic defaults + the first ``DEFAULT_COLUMN_LIMIT``
    OpenAPI leaf fields (meta fields still included but usually non-default
    unless they fall in that window — we skip ``x-zdg-is-meta`` for defaults).
    """
    specs: list[ColumnSpec] = [
        ColumnSpec(key=k, label=lab, description=desc, default=default)
        for k, lab, desc, default in _HEADER_COLUMNS
    ]
    seen = {s.key for s in specs}

    schemas = load_openapi_schemas()
    root = schemas.get(openapi_root_name(smf_type, subtype)) or {}
    props = root.get("properties") or {}

    openapi_cols: list[ColumnSpec] = []
    for name, prop in props.items():
        if not _is_leaf_prop(prop):
            continue
        if name in seen:
            continue
        desc = (prop.get("description") or "").strip() or name
        openapi_cols.append(
            ColumnSpec(
                key=name,
                label=_friendly_label(name, desc),
                description=desc,
                default=False,  # set below
            )
        )

    # First N non-meta OpenAPI fields are default; remainder stay optional.
    defaulted = 0
    finalized: list[ColumnSpec] = []
    for col in openapi_cols:
        prop = props.get(col.key) or {}
        is_meta = bool(prop.get("x-zdg-is-meta"))
        make_default = (not is_meta) and defaulted < DEFAULT_COLUMN_LIMIT
        if make_default:
            defaulted += 1
        finalized.append(
            ColumnSpec(
                key=col.key,
                label=col.label,
                description=col.description,
                default=make_default,
            )
        )

    return specs + finalized


def default_visible_keys(columns: list[ColumnSpec]) -> set[str]:
    visible = {c.key for c in columns if c.default}
    return visible or ({columns[0].key} if columns else set())
