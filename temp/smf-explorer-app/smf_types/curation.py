"""Manual KPI, column, and chart overrides on top of the generated catalog."""
from __future__ import annotations

from typing import Optional

import pandas as pd

from smf_types.core import Column, Highlight, Kpi, SmfTypeSpec


def _kpi_count_and_mean(df: pd.DataFrame, col: str, label: str) -> list[Kpi]:
    kpis = [Kpi("Record count", len(df))]
    if col in df.columns and not df.empty:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if not series.empty:
            kpis.append(Kpi(label, round(float(series.mean()), 2)))
    return kpis


def _scale_cpu(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.dropna().empty:
        return numeric
    if float(numeric.max()) <= 1.5:
        return numeric * 100.0
    return numeric


def _chart_line(df: pd.DataFrame, value_col: str, name: str) -> Optional[dict]:
    if df.empty or value_col not in df.columns:
        return None
    work = df.copy()
    if "timestamp" in work.columns:
        work["timestamp"] = pd.to_datetime(work["timestamp"], errors="coerce")
        work = work.dropna(subset=["timestamp"]).sort_values("timestamp")
        labels = [pd.Timestamp(t).strftime("%H:%M") for t in work["timestamp"]]
    else:
        labels = [str(i) for i in range(len(work))]
    values = pd.to_numeric(work[value_col], errors="coerce").tolist()
    if len(values) < 2:
        return None
    return {
        "kind": "line",
        "labels": labels,
        "series": [{"name": name, "data": values}],
    }


def _kpis_30_4(df: pd.DataFrame) -> list[Kpi]:
    kpis = [Kpi("Record count", len(df))]
    if "step_completion_code" in df.columns and not df.empty:
        bad = (df["step_completion_code"].fillna("0000") != "0000").sum()
        kpis.append(Kpi("Non-zero completion", int(bad)))
    if "job_name" in df.columns:
        kpis.append(Kpi("Distinct jobs", int(df["job_name"].nunique())))
    return kpis


def _kpis_70_1(df: pd.DataFrame) -> list[Kpi]:
    kpis = [Kpi("Record count", len(df))]
    if "cpu_busy_percentage" in df.columns and not df.empty:
        scaled = _scale_cpu(df["cpu_busy_percentage"])
        kpis.append(Kpi("Avg. CPU busy %", round(float(scaled.mean()), 2)))
    return kpis


def _chart_70_1(df: pd.DataFrame) -> Optional[dict]:
    if df.empty or "cpu_busy_percentage" not in df.columns:
        return None
    work = df.copy()
    work["cpu_busy_percentage"] = _scale_cpu(work["cpu_busy_percentage"])
    return _chart_line(work, "cpu_busy_percentage", "CPU busy %")


def _chart_71_1(df: pd.DataFrame) -> Optional[dict]:
    return _chart_line(df, "pin", "Page-in rate")


def _chart_72_3(df: pd.DataFrame) -> Optional[dict]:
    return _chart_line(df, "sample_cpu_delay", "CPU delay (WLM)")


def _kpis_74_1(df: pd.DataFrame) -> list[Kpi]:
    return _kpi_count_and_mean(df, "atd", "Avg. PAV alias delay")


def _kpis_77_1(df: pd.DataFrame) -> list[Kpi]:
    kpis = [Kpi("Record count", len(df))]
    if "jobs_waiting" in df.columns and not df.empty:
        waiting = pd.to_numeric(df["jobs_waiting"], errors="coerce").fillna(0)
        kpis.append(Kpi("Samples with waiters", int((waiting > 0).sum())))
    if "qnm" in df.columns:
        kpis.append(Kpi("Distinct resources", int(df["qnm"].nunique())))
    return kpis


# type_id -> partial override applied onto SmfTypeSpec
_CURATED: dict[str, dict] = {
    "30-4": {
        "field_names": [
            "timestamp", "job_name", "step_name", "step_completion_code",
            "abd", "step_time", "srb_step_cpu_time", "sys_name", "user_name",
        ],
        "columns": [
            Column("timestamp", "Timestamp", "Record timestamp.", True, kind="datetime"),
            Column("job_name", "Job", "Job / session name.", True),
            Column("step_name", "Step", "Step name.", True),
            Column("step_completion_code", "Completion", "Step completion code.", True),
            Column("abd", "Abend", "Abend indicator.", True, kind="bool"),
            Column("step_time", "Step CPU (s)", "Step CPU time.", True, numeric=True),
            Column("srb_step_cpu_time", "SRB CPU (s)", "SRB CPU time.", False, numeric=True),
            Column("sys_name", "System", "System name.", True),
            Column("user_name", "User", "Programmer / user name.", False),
        ],
        "build_kpis": _kpis_30_4,
        "highlight": Highlight("step_completion_code", "neq", "0000", "bad"),
        "viz": "table",
    },
    "70-1": {
        "field_names": [
            "timestamp", "cpu_busy_percentage", "system_name", "lpar_name",
            "cpu_wait_time", "interval",
        ],
        "columns": [
            Column("timestamp", "Timestamp", "Interval timestamp.", True, kind="datetime"),
            Column("cpu_busy_percentage", "CPU busy %", "CPU busy percentage.", True, numeric=True),
            Column("system_name", "System", "Operating-system instance.", True),
            Column("lpar_name", "LPAR", "LPAR name.", True),
            Column("cpu_wait_time", "CPU wait", "CPU wait time.", False, numeric=True),
            Column("interval", "Interval", "RMF interval length.", False),
        ],
        "build_kpis": _kpis_70_1,
        "build_chart": _chart_70_1,
        "viz": "timeseries",
    },
    "71-1": {
        "field_names": ["timestamp", "pin", "pot", "sin", "sot", "avf"],
        "columns": [
            Column("timestamp", "Timestamp", "Interval timestamp.", True, kind="datetime"),
            Column("pin", "Page-in", "Page-in rate.", True, numeric=True),
            Column("pot", "Page-out", "Page-out rate.", True, numeric=True),
            Column("sin", "Swap-in", "Swap-in rate.", True, numeric=True),
            Column("sot", "Swap-out", "Swap-out rate.", True, numeric=True),
            Column("avf", "Avail. frames", "Available page frames.", True, numeric=True),
        ],
        "build_kpis": lambda df: _kpi_count_and_mean(df, "pin", "Avg. page-in"),
        "build_chart": _chart_71_1,
        "viz": "timeseries",
    },
    "72-3": {
        "field_names": [
            "timestamp", "sample_cpu_delay", "class_name", "period_number",
        ],
        "columns": [
            Column("timestamp", "Timestamp", "Interval timestamp.", True, kind="datetime"),
            Column("sample_cpu_delay", "CPU delay", "WLM CPU delay samples.", True, numeric=True),
            Column("class_name", "Service class", "WLM service/report class.", True),
            Column("period_number", "Periods", "Number of periods for this class.", True, numeric=True),
        ],
        "build_kpis": lambda df: _kpi_count_and_mean(df, "sample_cpu_delay", "Avg. CPU delay"),
        "build_chart": _chart_72_3,
        "highlight": Highlight("sample_cpu_delay", "gt", 80, "warn"),
        "viz": "timeseries",
    },
    "74-1": {
        "field_names": ["timestamp", "dev", "atd"],
        "columns": [
            Column("timestamp", "Timestamp", "Interval timestamp.", True, kind="datetime"),
            Column("dev", "Device", "Device number.", True),
            Column("atd", "PAV delay", "PAV alias throttling delayed I/Os.", True, numeric=True),
        ],
        "build_kpis": _kpis_74_1,
        "highlight": Highlight("atd", "gt", 0, "warn"),
        "viz": "table",
    },
    "77-1": {
        "field_names": ["timestamp", "qnm", "rnm", "evt", "jobs_waiting", "wtt", "wtx"],
        "columns": [
            Column("timestamp", "Timestamp", "Event timestamp.", True, kind="datetime"),
            Column("qnm", "Major name", "ENQ major resource name.", True),
            Column("rnm", "Minor name", "ENQ minor resource name.", True),
            Column("evt", "Events", "Contention events.", True, numeric=True),
            Column("jobs_waiting", "Jobs waiting", "Jobs waiting on resource.", True, numeric=True),
            Column("wtt", "Wait time", "Total wait time.", False, numeric=True),
            Column("wtx", "Max wait", "Maximum wait time.", False, numeric=True),
        ],
        "build_kpis": _kpis_77_1,
        "highlight": Highlight("jobs_waiting", "gt", 0, "warn"),
        "viz": "table",
    },
}


def apply_curation(catalog_by_id: dict[str, SmfTypeSpec]) -> None:
    """Mutate curated specs in-place."""
    for type_id, override in _CURATED.items():
        spec = catalog_by_id.get(type_id)
        if spec is None:
            continue
        for key, value in override.items():
            setattr(spec, key, value)


def query_field_names(spec: SmfTypeSpec) -> list[str]:
    """Fields to request: curated field_names, else default columns (+ timestamp)."""
    if spec.id in _CURATED:
        return list(spec.field_names)
    keys = [c.key for c in spec.columns if c.default]
    if not keys:
        keys = list(spec.field_names[:12])
    if "timestamp" not in keys:
        keys = ["timestamp", *keys]
    # de-dupe preserving order
    seen: set[str] = set()
    out: list[str] = []
    for k in keys:
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out
