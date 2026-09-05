"""Gatherer-supported SMF type/subtype pairs (z/OS Data Gatherer / smfexplorer)."""
from __future__ import annotations

# Mirrors smf-explorer-app app_core/session.py KNOWN_RECORD_MODULES.
GATHERER_SUBTYPES: dict[int, set[int]] = {
    30: {1, 2, 3, 4, 5, 6},
    70: {1, 2},
    71: {1},
    72: {3, 4, 5},
    73: {1},
    74: {1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
    75: {1},
    76: {1},
    77: {1},
    78: {2, 3},
    79: {1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 14, 15},
    99: {1, 2, 6, 12, 14},
    113: {1, 2},
}

GATHERER_TYPES: set[int] = set(GATHERER_SUBTYPES)

TITLE_BY_TYPE_SUBTYPE: dict[tuple[int, int], str] = {
    (30, 1): "Job/Step — initiation",
    (30, 2): "Job/Step — interval",
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


def record_module_name(smf_type: int, subtype: int) -> str:
    return f"SMF{smf_type}S{subtype}"


def openapi_root_name(smf_type: int, subtype: int) -> str:
    return f"SMF{smf_type}_SUBTYPE{subtype}"


def title_for(smf_type: int, subtype: int) -> str:
    return TITLE_BY_TYPE_SUBTYPE.get(
        (smf_type, subtype), f"SMF {smf_type} subtype {subtype}"
    )
