"""Shared catalog types (Column, Kpi, SmfTypeSpec) and DataFrame mapping helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import pandas as pd


@dataclass
class Column:
    """Description of a single data column — used for table rendering and
    the column picker (default / non-default)."""
    key: str
    label: str
    description: str
    default: bool = True
    numeric: bool = False
    kind: str = 'text'  # 'text' | 'number' | 'datetime' | 'bool'


@dataclass
class Kpi:
    label: str
    value: Any
    unit: str = ''

    def text(self) -> str:
        v = self.value
        if isinstance(v, float):
            v = f'{v:,.2f}'.rstrip('0').rstrip('.')
        return f'{v} {self.unit}'.strip()


@dataclass
class Highlight:
    key: str
    op: str  # 'gt' | 'lt' | 'eq' | 'neq'
    value: Any
    cls: str  # 'bad' | 'warn'

    def matches(self, row: dict) -> bool:
        val = row.get(self.key)
        if self.op == 'gt':
            return val is not None and val > self.value
        if self.op == 'lt':
            return val is not None and val < self.value
        if self.op == 'eq':
            return val == self.value
        if self.op == 'neq':
            return val != self.value
        return False


@dataclass
class SmfTypeSpec:
    """Static definition of one SMF type/subtype in the catalog.

    Equivalent to a prototype generator (`gen_smf{N}`) but without RNG: instead of
    returning ready-made `rows`, it describes how to query `smfexplorer`
    (`record_module` + `field_names`) and how to build a display `SmfType` from
    the resulting `DataFrame` (`build()`).
    """
    id: str
    title: str
    category: str
    description: str
    viz: str  # 'table' | 'events' | 'timeseries'
    order: int
    record_module: str  # e.g. "SMF74S1" — smfexplorer.fields.* module
    field_names: list[str]  # field names from that module to query
    columns: list[Column] = field(default_factory=list)
    build_kpis: Optional[Callable[[pd.DataFrame], list[Kpi]]] = None
    build_chart: Optional[Callable[[pd.DataFrame], Optional[dict]]] = None
    highlight: Optional[Highlight] = None
    live_capable: bool = False  # whether the view makes sense as auto-refreshed poll


@dataclass
class SmfType:
    """Materialized view — `SmfTypeSpec` + data from one query.

    What `webui/kpi.py`, `webui/chart.py`, and `webui/data_table.py` render today.
    """
    id: str
    title: str
    category: str
    description: str
    viz: str
    order: int
    kpis: list[Kpi] = field(default_factory=list)
    columns: list[Column] = field(default_factory=list)
    rows: list[dict] = field(default_factory=list)
    highlight: Optional[Highlight] = None
    chart: Optional[dict] = None  # {'kind': 'line'|'bar', 'labels': [...], 'series': [{'name','data'}]}
    live_capable: bool = False


def avg(values: list[float]) -> float:
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 2) if values else 0.0


def pearson(xs: list[float], ys: list[float]) -> float:
    import math
    n = len(xs)
    if n == 0:
        return 0.0
    mx, my = avg(xs), avg(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs)
    dy = sum((y - my) ** 2 for y in ys)
    return num / math.sqrt(dx * dy) if dx and dy else 0.0
