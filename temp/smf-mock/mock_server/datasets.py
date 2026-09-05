"""In-memory fake SMF dataset registry for mock discovery and queries."""
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Tuple


@dataclass
class FakeDataset:
    name: str
    system_ids: List[str]
    creation_date: date
    # (type, subtype) -> approximate record count to report in discovery
    record_counts: Dict[Tuple[int, int], int] = field(default_factory=dict)


TODAY = date.today()

DATASETS: Dict[str, FakeDataset] = {
    "TEST.SMF.DATASET": FakeDataset(
        name="TEST.SMF.DATASET",
        system_ids=["SYSA", "SYSB"],
        creation_date=TODAY - timedelta(days=7),
        record_counts={},  # filled in at startup for every known type/subtype
    ),
    "DEV.SMF.SANDBOX": FakeDataset(
        name="DEV.SMF.SANDBOX",
        system_ids=["SYSC"],
        creation_date=TODAY - timedelta(days=1),
        record_counts={},
    ),
}


def get_dataset(name: str) -> FakeDataset | None:
    return DATASETS.get(name)
