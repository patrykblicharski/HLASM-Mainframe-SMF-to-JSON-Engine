#!/usr/bin/env python3
"""Generates smf_types/catalog.py from scripts/fields_dump.json (one-off maintainer tool)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DUMP = json.loads((ROOT / "scripts" / "fields_dump.json").read_text(encoding="utf-8"))

DEFAULT_COLUMN_LIMIT = 12

# type -> category constant name (short category label lives in dictionaries)
CATEGORY_BY_TYPE = {
    30: "CAT_JOB",
    70: "CAT_CPU",
    71: "CAT_PAGING",
    72: "CAT_WLM",
    73: "CAT_CHANNEL",
    74: "CAT_DASD",
    75: "CAT_PAGEDS",
    76: "CAT_TRACE",
    77: "CAT_ENQ",
    78: "CAT_IOSQ",
    79: "CAT_MON2",
    99: "CAT_MON3",
    113: "CAT_JAVA",
}

TITLE_BY_TYPE_SUBTYPE = {
    (30, 1): "Job/Step — initiation",
    (30, 2): "Job/Step — interval (transition point)",
    (30, 3): "Job/Step — step termination",
    (30, 4): "Job — job termination",
    (30, 5): "Job — session termination",
    (30, 6): "Job/Step — common address space",
    (70, 1): "CPU/LPAR — processor activity",
    (70, 2): "CPU/LPAR — configuration data",
    (71, 1): "Paging — paging activity",
    (72, 3): "WLM — service goal period",
    (72, 4): "WLM — transaction data",
    (72, 5): "WLM — reporting class",
    (73, 1): "I/O channels — channel activity",
    (74, 1): "DASD — device activity",
    (74, 2): "DASD — controller cache",
    (74, 3): "DASD — device group",
    (74, 4): "FICON — port activity",
    (74, 5): "Cache — subsystem statistics",
    (74, 6): "DASD — HyperPAV",
    (74, 7): "zHyperLink — activity",
    (74, 8): "DASD — extended statistics",
    (74, 9): "Coupling Facility — activity",
    (74, 10): "Coupling Facility — structures",
    (75, 1): "Page datasets — activity",
    (76, 1): "Trace — trace data",
    (77, 1): "Enqueue — resource contention",
    (78, 2): "Storage — virtual/real memory",
    (78, 3): "IOSQ — I/O queuing",
    (79, 1): "Monitor II — ASCB/address space",
    (79, 2): "Monitor II — storage resources",
    (79, 3): "Monitor II — I/O devices",
    (79, 4): "Monitor II — WLM service class",
    (79, 5): "Monitor II — common address space",
    (79, 6): "Monitor II — enqueue",
    (79, 7): "Monitor II — HSM",
    (79, 9): "Monitor II — XCF",
    (79, 11): "Monitor II — cache",
    (79, 12): "Monitor II — coupling facility",
    (79, 14): "Monitor II — zFS",
    (79, 15): "Monitor II — additional",
    (99, 1): "WLM Monitor III — service class period",
    (99, 2): "WLM Monitor III — resource group",
    (99, 6): "WLM Monitor III — storage",
    (99, 12): "WLM Monitor III — enclave",
    (99, 14): "WLM Monitor III — CPU",
    (113, 1): "Java Data Gatherer — capacity",
    (113, 2): "Java Data Gatherer — JVM details",
}


def parse_record_name(name: str) -> tuple[int, int]:
    # "SMF74S10" -> (74, 10)
    body = name[len("SMF"):]
    type_str, subtype_str = body.split("S", 1)
    return int(type_str), int(subtype_str)


def py_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def build_entry(record_name: str, order: int) -> str:
    fields = DUMP[record_name]
    type_, subtype = parse_record_name(record_name)
    category_const = CATEGORY_BY_TYPE[type_]
    title = TITLE_BY_TYPE_SUBTYPE.get((type_, subtype), f"SMF {type_} subtype {subtype}")

    non_virtual = [f for f in fields if not f["virtual"]]
    use_fields = non_virtual if non_virtual else fields

    lines = []
    lines.append("    SmfTypeSpec(")
    lines.append(f"        id={py_str(f'{type_}-{subtype}')},")
    lines.append(f"        title={py_str(title)},")
    lines.append(f"        category={category_const},")
    lines.append(f"        description={py_str(f'SMF {type_} subtype {subtype} record ({record_name}).')},")
    lines.append("        viz='table',")
    lines.append(f"        order={order},")
    lines.append(f"        record_module={py_str(record_name)},")
    lines.append("        field_names=[")
    for f in use_fields:
        lines.append(f"            {py_str(f['name'])},")
    lines.append("        ],")
    lines.append("        columns=[")
    for i, f in enumerate(use_fields):
        numeric = f["type"] in ("INTEGER", "LONG", "DOUBLE", "FLOAT", "DECIMAL")
        kind = "number" if numeric else "text"
        default = "True" if i < DEFAULT_COLUMN_LIMIT else "False"
        label = f["name"]
        desc = f["description"].replace("\n", " ")[:200]
        lines.append(
            "            Column("
            f"key={py_str(f['name'])}, label={py_str(label)}, "
            f"description={py_str(desc)}, default={default}, "
            f"numeric={numeric}, kind={py_str(kind)}),"
        )
    lines.append("        ],")
    lines.append("        build_kpis=lambda df: default_kpis(df),")
    lines.append("        build_chart=None,")
    lines.append("    ),")
    return "\n".join(lines)


def main() -> None:
    record_names = sorted(DUMP.keys(), key=parse_record_name)

    header = '''"""SMF type/subtype catalog (auto-generated; see scripts/generate_catalog.py)."""
from __future__ import annotations

from typing import Optional

import pandas as pd

from smf_types.core import Column, Kpi, SmfTypeSpec
from smf_types.dictionaries import (
    CAT_CHANNEL,
    CAT_CPU,
    CAT_DASD,
    CAT_ENQ,
    CAT_IOSQ,
    CAT_JAVA,
    CAT_JOB,
    CAT_MON2,
    CAT_MON3,
    CAT_PAGEDS,
    CAT_PAGING,
    CAT_TRACE,
    CAT_WLM,
)


def default_kpis(df: pd.DataFrame) -> list[Kpi]:
    """Generic KPIs: record count + mean of the first numeric column."""
    kpis = [Kpi("Record count", len(df))]
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) > 0:
        col = numeric_cols[0]
        kpis.append(Kpi(f"Avg. {col}", round(float(df[col].mean()), 2)))
    return kpis


CATALOG: list[SmfTypeSpec] = [
'''

    entries = []
    for i, record_name in enumerate(record_names, start=1):
        entries.append(build_entry(record_name, i))

    footer = "]\n\n\nCATALOG_BY_ID = {spec.id: spec for spec in CATALOG}\n"

    out_path = ROOT / "smf_types" / "catalog.py"
    out_path.write_text(header + "\n".join(entries) + "\n" + footer, encoding="utf-8")
    print(f"Wrote {out_path} with {len(record_names)} entries")


if __name__ == "__main__":
    main()
