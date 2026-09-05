"""Import and register all per-subtype layout modules."""
from __future__ import annotations

import importlib
import pkgutil

from . import layouts
from .registry import register_subtype
from .subtypes import SUBTYPES
from .views import ColumnSpec, register_summary, _sf  # noqa: PLC2701


def _auto_summary(subtype: int, slots) -> None:
    """Build a basic summary from the first record-specific section's useful fields."""
    if not slots:
        return
    first = slots[0]
    layout = first.layout
    specs = []
    # Prefer well-known field name patterns
    prefer = [
        ("Name", "name", 80),
        ("RName", "resource", 80),
        ("Job", "job", 70),
        ("User", "user", 70),
        ("LIP", "lip", 110),
        ("RIP", "rip", 110),
        ("LPort", "lport", 55),
        ("RPort", "rport", 55),
        ("InBytes", "in_bytes", 80),
        ("OutBytes", "out_bytes", 80),
        ("Bytes", "bytes", 80),
        ("TermCode", "term", 70),
        ("Status", "status", 70),
        ("LU", "lu", 70),
        ("Appl", "appl", 70),
    ]
    used = set()
    for f in layout.fields:
        if f.reserved:
            continue
        for suffix, key, width in prefer:
            if f.name.endswith(suffix) and key not in used:
                specs.append(
                    (
                        ColumnSpec(key, suffix if len(suffix) <= 10 else key.title(), True, width),
                        _sf(first.key, f.name),
                    )
                )
                used.add(key)
                break
        if len(specs) >= 8:
            break
    if specs:
        register_summary(subtype, specs)


def load_all() -> None:
    """Discover parser.layouts.stXX modules and register SECTION_SLOTS."""
    for modinfo in pkgutil.iter_modules(layouts.__path__, layouts.__name__ + "."):
        name = modinfo.name.rsplit(".", 1)[-1]
        if not name.startswith("st") or name.startswith("st_"):
            continue
        try:
            subtype = int(name[2:])
        except ValueError:
            continue
        mod = importlib.import_module(modinfo.name)
        slots = getattr(mod, "SECTION_SLOTS", None)
        if not slots:
            continue
        # OpenSSH constants exist but have no layouts in ezasmf
        coverage = "mapped"
        register_subtype(subtype, list(slots), coverage=coverage)
        # Don't override hand-tuned summaries
        from .views import has_summary

        if not has_summary(subtype):
            _auto_summary(subtype, slots)

    # Mark external / still-missing
    for st in SUBTYPES:
        from .registry import COVERAGE, SUBTYPE_SECTIONS

        if st in (94, 95, 96, 97, 98):
            COVERAGE[st] = "external"
        elif st not in SUBTYPE_SECTIONS and st != 4:
            COVERAGE.setdefault(st, "unmapped")


# Load on import
load_all()
