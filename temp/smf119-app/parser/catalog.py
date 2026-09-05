"""Section / field catalog for SMF 119 decoding."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .header_layouts import HEADER, IDENT, TCP_INIT
from .layout import StructLayout, field_size
from .nmtp_layouts import LAYOUT_BY_EYE, LAYOUT_BY_NAME, PROFILE_SECTIONS
from .registry import (
    COVERAGE,
    EYE_LAYOUTS,
    SUBTYPE_SECTIONS,
    SectionSlot,
    coverage_for,
    register_eye,
    register_subtype,
)
from .subtypes import SUBTYPES, title_for

# Populate eye registry from NMTP
for _eye, _layout in LAYOUT_BY_EYE.items():
    register_eye(_eye, _layout)


@dataclass
class SectionInfo:
    key: str
    layout: StructLayout
    description: str
    eyecatcher: int | None = None
    chooser: Callable[[bytes, int], StructLayout] | None = None


def all_layouts() -> list[StructLayout]:
    layouts = [HEADER, IDENT, TCP_INIT]
    layouts.extend(layout for _, layout, _ in PROFILE_SECTIONS)
    seen = {id(x) for x in layouts}
    for slots in SUBTYPE_SECTIONS.values():
        for slot in slots:
            if id(slot.layout) not in seen:
                layouts.append(slot.layout)
                seen.add(id(slot.layout))
    for layout in EYE_LAYOUTS.values():
        if id(layout) not in seen:
            layouts.append(layout)
            seen.add(id(layout))
    return layouts


def field_catalog_rows() -> list[dict]:
    rows: list[dict] = []
    for layout in all_layouts():
        for f in layout.fields:
            if f.reserved:
                continue
            rows.append(
                {
                    "section": layout.name,
                    "field": f.name,
                    "offset": layout.offsets.get(f.name, 0),
                    "size": field_size(f) if f.kind != "var_ebcdic" else "var",
                    "kind": f.kind,
                    "description": f.description or layout.description,
                }
            )
    return rows


def section_for_eye(eye: int) -> SectionInfo | None:
    layout = EYE_LAYOUTS.get(eye) or LAYOUT_BY_EYE.get(eye)
    if not layout:
        return None
    name = next((n for n, lay, e in PROFILE_SECTIONS if e == eye), layout.name)
    return SectionInfo(key=name, layout=layout, description=layout.description, eyecatcher=eye)


def profile_section_at_triplet(triplet_index: int) -> SectionInfo | None:
    if triplet_index == 0:
        return SectionInfo(key="Ident", layout=IDENT, description=IDENT.description)
    idx = triplet_index - 1
    if 0 <= idx < len(PROFILE_SECTIONS):
        name, layout, eye = PROFILE_SECTIONS[idx]
        return SectionInfo(
            key=name, layout=layout, description=layout.description, eyecatcher=eye
        )
    return None


def layout_for_subtype_section(
    subtype: int,
    triplet_index: int,
    *,
    blob: bytes = b"",
    section_len: int = 0,
) -> SectionInfo | None:
    if triplet_index == 0:
        return SectionInfo(key="Ident", layout=IDENT, description=IDENT.description)

    if subtype == 4:
        return profile_section_at_triplet(triplet_index)

    slots = SUBTYPE_SECTIONS.get(subtype)
    if slots:
        for slot in slots:
            if slot.triplet_index == triplet_index:
                layout = slot.layout
                if slot.chooser:
                    layout = slot.chooser(blob, section_len)
                return SectionInfo(
                    key=slot.key,
                    layout=layout,
                    description=layout.description,
                    chooser=slot.chooser,
                )
        # by_eye fallback among registered slots
        if blob and len(blob) >= 4:
            import struct

            eye = struct.unpack_from(">I", blob, 0)[0]
            info = section_for_eye(eye)
            if info:
                return info

    if subtype == 1 and triplet_index == 1:
        return SectionInfo(key="TCPInit", layout=TCP_INIT, description=TCP_INIT.description)

    return None


def subtype_catalog_rows() -> list[dict]:
    rows = []
    for st in sorted(SUBTYPES):
        cov = coverage_for(st)
        if st in (94, 95, 96, 97, 98):
            cov = "external"
        elif st == 4:
            cov = COVERAGE.get(st, "mapped")
        elif st in SUBTYPE_SECTIONS:
            cov = COVERAGE.get(st, "mapped")
        else:
            cov = COVERAGE.get(st, "unmapped")

        mapped_fields = 0
        mapped_sections = 0
        if st == 4:
            mapped_sections = len(PROFILE_SECTIONS)
            mapped_fields = sum(
                len([f for f in layout.fields if not f.reserved]) for _, layout, _ in PROFILE_SECTIONS
            )
        elif st in SUBTYPE_SECTIONS:
            slots = SUBTYPE_SECTIONS[st]
            mapped_sections = len(slots)
            mapped_fields = sum(
                len([f for f in slot.layout.fields if not f.reserved]) for slot in slots
            )

        rows.append(
            {
                "subtype": st,
                "title": title_for(st),
                "coverage": cov,
                "mapped_profile": st == 4,
                "mapped_sections": mapped_sections,
                "mapped_fields": mapped_fields,
            }
        )
    return rows


def ensure_builtin_registration() -> None:
    """Register subtypes 1 and 4 coverage."""
    register_subtype(
        1,
        [SectionSlot(triplet_index=1, key="TCPInit", layout=TCP_INIT)],
        coverage="mapped",
    )
    register_subtype(4, [], coverage="mapped")  # handled specially via PROFILE_SECTIONS


ensure_builtin_registration()

# Generated / hand-written layouts (overwrite builtins where present)
try:
    from . import layouts_loader  # noqa: F401
except Exception as _exc:  # noqa: BLE001
    import sys

    print(f"smf119 layouts_loader warning: {_exc}", file=sys.stderr)


__all__ = [
    "SectionInfo",
    "LAYOUT_BY_EYE",
    "LAYOUT_BY_NAME",
    "all_layouts",
    "field_catalog_rows",
    "section_for_eye",
    "profile_section_at_triplet",
    "layout_for_subtype_section",
    "subtype_catalog_rows",
    "coverage_for",
]
