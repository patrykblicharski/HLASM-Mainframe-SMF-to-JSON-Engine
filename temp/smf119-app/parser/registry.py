"""Subtype section registry — maps triplet slots to layouts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .layout import StructLayout


@dataclass(frozen=True)
class SectionSlot:
    """One record-specific section (triplet index after Ident)."""

    triplet_index: int  # 1 = first record-specific (SMF119S1)
    key: str
    layout: StructLayout
    optional: bool = False
    # Optional: choose layout dynamically from section bytes / triplet len
    chooser: Callable[[bytes, int], StructLayout] | None = None
    by_eye: bool = False  # resolve via eyecatcher registry instead


# subtype -> list of slots (Ident is always triplet 0, handled separately)
SUBTYPE_SECTIONS: dict[int, list[SectionSlot]] = {}

# eyecatcher u32 -> layout (NMTP + TN profile + FTPD, etc.)
EYE_LAYOUTS: dict[int, StructLayout] = {}

# subtype coverage: "mapped" | "partial" | "unmapped" | "external"
COVERAGE: dict[int, str] = {}


def register_subtype(
    subtype: int,
    slots: list[SectionSlot],
    *,
    coverage: str = "mapped",
) -> None:
    SUBTYPE_SECTIONS[subtype] = slots
    COVERAGE[subtype] = coverage


def register_eye(eye: int, layout: StructLayout) -> None:
    EYE_LAYOUTS[eye] = layout


def coverage_for(subtype: int) -> str:
    return COVERAGE.get(subtype, "unmapped")
