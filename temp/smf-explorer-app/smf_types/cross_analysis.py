"""Non-ML cross-SMF analyses (aggregations, correlation) via app_core/query."""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from app_core import query as query_layer
from app_core.session import Session, dataframe_to_records
from smf_types.core import Column, Highlight, Kpi, SmfType, avg, pearson
from smf_types.dictionaries import CAT_CROSS

X_CPU_BATCH = "x-cpu-batch"
X_CPU_FORECAST = "x-cpu-forecast"
X_WLM_BOTTLENECK = "x-wlm-bottleneck"
X_PAGING_PRESSURE = "x-paging-pressure"
X_ENQUEUE_CONTENTION = "x-enqueue-contention"
X_JOB_RISK = "x-job-risk"
X_ALERTS = "x-alerts"

CROSS_ANALYSIS_IDS = [
    X_ALERTS, X_CPU_BATCH, X_CPU_FORECAST, X_WLM_BOTTLENECK,
    X_PAGING_PRESSURE, X_ENQUEUE_CONTENTION, X_JOB_RISK,
]

# (type, subtype) pairs that must all be present in session.available
CROSS_ANALYSIS_REQUIRES: dict[str, set[tuple[int, int]]] = {
    X_ALERTS: {(30, 4), (74, 1), (72, 3), (77, 1)},
    X_CPU_BATCH: {(70, 1), (30, 4)},
    X_CPU_FORECAST: {(70, 1)},
    X_WLM_BOTTLENECK: {(72, 3), (70, 1), (74, 1)},
    X_PAGING_PRESSURE: {(71, 1), (70, 1)},
    X_ENQUEUE_CONTENTION: {(77, 1)},
    X_JOB_RISK: {(30, 4)},
}

CROSS_ANALYSIS_TITLES = {
    X_ALERTS: "Alert feed — anomalies across record types",
    X_CPU_BATCH: "CPU × Batch — workload correlation",
    X_CPU_FORECAST: "CPU forecast (24h)",
    X_WLM_BOTTLENECK: "WLM — bottleneck analysis",
    X_PAGING_PRESSURE: "Paging pressure vs. CPU (SMF71 × SMF70)",
    X_ENQUEUE_CONTENTION: "Enqueue contention hotspots (SMF77)",
    X_JOB_RISK: "Job risk ranking (SMF30 abends × CPU)",
}

CROSS_ANALYSIS_DESCRIPTIONS = {
    X_ALERTS: (
        "Combined alert feed across SMF30 (step abends), SMF74 (DASD busy), "
        "SMF72 (WLM goal achievement), and SMF77 (enqueue contention) — "
        "a prototype heuristic feed, NOT an ML model."
    ),
    X_CPU_BATCH: (
        "Pearson correlation between CPU usage (SMF70) and the number of "
        "completed batch jobs (SMF30 subtype 4) in the same time window."
    ),
    X_CPU_FORECAST: (
        "Simple linear extrapolation of the CPU usage trend (SMF70) for the "
        "next 24h based on the latest data window. This is NOT an ML model."
    ),
    X_WLM_BOTTLENECK: (
        "Combines CPU delay (SMF72), CPU usage (SMF70), and DASD activity "
        "(SMF74) in the same window — helps identify whether a slowdown "
        "originates from CPU, WLM, or I/O."
    ),
    X_PAGING_PRESSURE: (
        "Page-in/page-out and swap rates (SMF71) plotted against CPU usage "
        "(SMF70) in the same window — flags intervals where active swapping "
        "coincides with high CPU busy, a sign of real memory constraint."
    ),
    X_ENQUEUE_CONTENTION: (
        "Aggregates ENQ/DEQ resource-contention events (SMF77) per resource "
        "— surfaces the resources with the most contention events and the "
        "longest total job wait time."
    ),
    X_JOB_RISK: (
        "Risk score per job combining step abends and CPU-time outliers "
        "(SMF30 subtype 4) — a prototype heuristic ranking, NOT an ML model."
    ),
}


def _query_limit(session: Session) -> int:
    return session.query_limit or 5000


def _time_window(hours: int) -> tuple[datetime, datetime]:
    end_time = datetime.now()
    return end_time - timedelta(hours=hours), end_time


def _scale_cpu_busy(series: pd.Series) -> pd.Series:
    """Scale fraction (0–1) to percent; leave values that already look like % alone."""
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.dropna().empty:
        return numeric
    if float(numeric.max()) <= 1.5:
        return numeric * 100.0
    return numeric


def _ensure_datetime_index(df: pd.DataFrame, value_cols: list[str]) -> pd.DataFrame:
    """Return DataFrame indexed by timestamp with selected columns, hourly-ready."""
    if df is None or df.empty or "timestamp" not in df.columns:
        return pd.DataFrame()
    out = df[["timestamp", *[c for c in value_cols if c in df.columns]]].copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
    out = out.dropna(subset=["timestamp"]).set_index("timestamp").sort_index()
    return out


def _hourly_mean(df: pd.DataFrame, col: str) -> pd.Series:
    if df.empty or col not in df.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[col], errors="coerce").resample("1h").mean()


def _hourly_count(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)
    return df.resample("1h").size().astype(float)


def _truncation_kpi(dfs: list[pd.DataFrame], limit: int) -> list[Kpi]:
    if any(len(df) >= limit for df in dfs if df is not None):
        return [Kpi("Result truncated", f"hit limit {limit}")]
    return []


def _col_or_zero(df: pd.DataFrame, name: str) -> pd.Series:
    if name in df.columns:
        return pd.to_numeric(df[name], errors="coerce").fillna(0)
    return pd.Series(0, index=df.index, dtype=float)


def _col_or_false(df: pd.DataFrame, name: str) -> pd.Series:
    if name in df.columns:
        return df[name].fillna(False).astype(bool)
    return pd.Series(False, index=df.index, dtype=bool)


def build_x_alerts(session: Session, hours: int = 24) -> SmfType:
    start_time, end_time = _time_window(hours)
    limit = _query_limit(session)
    alerts: list[dict] = []
    dfs: list[pd.DataFrame] = []

    job_df = query_layer.run_query(
        session, "SMF30S4", ["timestamp", "job_name", "step_completion_code"],
        start_time=start_time, end_time=end_time, limit=limit,
        system_name=session.system_name,
    )
    dfs.append(job_df)
    if not job_df.empty and "step_completion_code" in job_df:
        bad = job_df[job_df["step_completion_code"].fillna("0000") != "0000"]
        for r in dataframe_to_records(bad):
            alerts.append({
                "time": r.get("timestamp"), "severity": "High", "source": "SMF30",
                "event": "Step abend / non-zero completion code",
                "detail": f"{r.get('job_name')} — completion code {r.get('step_completion_code')}",
            })

    dasd_df = query_layer.run_query(
        session, "SMF74S1", ["timestamp", "dev", "atd"],
        start_time=start_time, end_time=end_time, limit=limit,
        system_name=session.system_name,
    )
    dfs.append(dasd_df)
    if not dasd_df.empty and "atd" in dasd_df:
        bad = dasd_df[dasd_df["atd"].fillna(0) > 0]
        for r in dataframe_to_records(bad):
            alerts.append({
                "time": r.get("timestamp"), "severity": "Low", "source": "SMF74",
                "event": "PAV alias throttling delay",
                "detail": f"Device {r.get('dev')} — {r.get('atd')} delayed I/Os",
            })

    wlm_df = query_layer.run_query(
        session, "SMF72S3", ["timestamp", "sample_cpu_delay"],
        start_time=start_time, end_time=end_time, limit=limit,
        system_name=session.system_name,
    )
    dfs.append(wlm_df)
    if not wlm_df.empty and "sample_cpu_delay" in wlm_df:
        bad = wlm_df[wlm_df["sample_cpu_delay"].fillna(0) > 80]
        for r in dataframe_to_records(bad):
            alerts.append({
                "time": r.get("timestamp"), "severity": "Medium", "source": "SMF72",
                "event": "High WLM CPU delay",
                "detail": f"CPU delay {r.get('sample_cpu_delay')}",
            })

    enq_df = query_layer.run_query(
        session, "SMF77S1", ["timestamp", "qnm", "jobs_waiting"],
        start_time=start_time, end_time=end_time, limit=limit,
        system_name=session.system_name,
    )
    dfs.append(enq_df)
    if not enq_df.empty and "jobs_waiting" in enq_df:
        bad = enq_df[enq_df["jobs_waiting"].fillna(0) > 0]
        for r in dataframe_to_records(bad):
            alerts.append({
                "time": r.get("timestamp"), "severity": "Medium", "source": "SMF77",
                "event": "Enqueue contention",
                "detail": f"{r.get('qnm')} — {r.get('jobs_waiting')} jobs waiting",
            })

    severity_order = {"High": 0, "Medium": 1, "Low": 2}
    alerts.sort(key=lambda a: (severity_order.get(a["severity"], 3), str(a.get("time") or "")))

    kpis = [
        Kpi("Total alerts", len(alerts)),
        Kpi("High severity", sum(1 for a in alerts if a["severity"] == "High")),
        Kpi("Sources correlated", len({a["source"] for a in alerts})),
        *_truncation_kpi(dfs, limit),
    ]

    columns = [
        Column("time", "Time", "Timestamp of the underlying record.", True, kind='datetime'),
        Column("severity", "Severity", "Alert severity (High/Medium/Low).", True),
        Column("source", "Source", "SMF record type this alert was derived from.", True),
        Column("event", "Event", "Short description of the anomaly.", True),
        Column("detail", "Detail", "Additional detail for this alert.", True),
    ]

    return SmfType(
        id=X_ALERTS, title=CROSS_ANALYSIS_TITLES[X_ALERTS], category=CAT_CROSS,
        description=CROSS_ANALYSIS_DESCRIPTIONS[X_ALERTS], viz="events", order=0,
        kpis=kpis, columns=columns, rows=alerts,
        highlight=Highlight("severity", "eq", "High", "bad"),
    )


def build_x_cpu_batch(session: Session, hours: int = 24) -> SmfType:
    start_time, end_time = _time_window(hours)
    limit = _query_limit(session)

    cpu_raw = query_layer.run_query(
        session, "SMF70S1", ["timestamp", "cpu_busy_percentage"],
        start_time=start_time, end_time=end_time, limit=limit,
        system_name=session.system_name,
    )
    job_raw = query_layer.run_query(
        session, "SMF30S4", ["timestamp", "job_name"],
        start_time=start_time, end_time=end_time, limit=limit,
        system_name=session.system_name,
    )

    cpu_idx = _ensure_datetime_index(cpu_raw, ["cpu_busy_percentage"])
    if not cpu_idx.empty and "cpu_busy_percentage" in cpu_idx.columns:
        cpu_idx["cpu_busy_percentage"] = _scale_cpu_busy(cpu_idx["cpu_busy_percentage"])
    job_idx = _ensure_datetime_index(job_raw, ["job_name"])

    cpu_hourly = _hourly_mean(cpu_idx, "cpu_busy_percentage")
    jobs_hourly = _hourly_count(job_idx)
    joined = pd.concat([cpu_hourly.rename("cpu"), jobs_hourly.rename("jobs")], axis=1).dropna()

    cpu_series = joined["cpu"].tolist() if not joined.empty else []
    job_series = joined["jobs"].tolist() if not joined.empty else []
    labels = [ts.strftime("%Y-%m-%d %H:%M") for ts in joined.index] if not joined.empty else []
    n = len(joined)
    corr = pearson(cpu_series, job_series) if n > 1 else 0.0

    kpis = [
        Kpi("CPU records (SMF70)", len(cpu_raw)),
        Kpi("Completed jobs (SMF30S4)", len(job_raw)),
        Kpi("Pearson correlation", round(corr, 3)),
        *_truncation_kpi([cpu_raw, job_raw], limit),
    ]

    chart = None
    columns: list[Column] = []
    rows: list[dict] = []
    if n > 1:
        chart = {
            "kind": "line",
            "labels": labels,
            "series": [
                {"name": "CPU busy %", "data": cpu_series, "yAxis": 0, "yAxisName": "CPU busy %"},
                {"name": "Completed jobs / hr", "data": job_series, "yAxis": 1, "yAxisName": "Jobs / hr"},
            ],
        }
        columns = [
            Column("interval", "Interval", "Hourly interval start.", True, kind="datetime"),
            Column("cpuBusyPct", "CPU busy %", "Mean CPU busy % in this hour.", True, numeric=True),
            Column("jobsPerHour", "Completed jobs / hr", "Jobs completed in this hour.", True, numeric=True),
        ]
        rows = [
            {"interval": labels[i], "cpuBusyPct": round(cpu_series[i], 2), "jobsPerHour": int(job_series[i])}
            for i in range(n)
        ]

    return SmfType(
        id=X_CPU_BATCH, title=CROSS_ANALYSIS_TITLES[X_CPU_BATCH], category=CAT_CROSS,
        description=CROSS_ANALYSIS_DESCRIPTIONS[X_CPU_BATCH], viz="timeseries", order=1,
        kpis=kpis, chart=chart, columns=columns, rows=rows,
    )


def build_x_cpu_forecast(session: Session, hours: int = 24) -> SmfType:
    start_time, end_time = _time_window(hours)
    limit = _query_limit(session)
    forecast_hours = 24

    cpu_raw = query_layer.run_query(
        session, "SMF70S1", ["timestamp", "cpu_busy_percentage"],
        start_time=start_time, end_time=end_time, limit=limit,
        system_name=session.system_name,
    )
    cpu_idx = _ensure_datetime_index(cpu_raw, ["cpu_busy_percentage"])
    if not cpu_idx.empty and "cpu_busy_percentage" in cpu_idx.columns:
        cpu_idx["cpu_busy_percentage"] = _scale_cpu_busy(cpu_idx["cpu_busy_percentage"])
    hourly = _hourly_mean(cpu_idx, "cpu_busy_percentage").dropna()

    series = hourly.tolist()
    n = len(series)
    obs_labels = [ts.strftime("%Y-%m-%d %H:%M") for ts in hourly.index]

    forecast: list[float] = []
    forecast_labels: list[str] = []
    if n >= 2:
        xs = list(range(n))
        mean_x, mean_y = avg([float(x) for x in xs]), avg(series)
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, series))
        den = sum((x - mean_x) ** 2 for x in xs)
        slope = num / den if den else 0.0
        intercept = mean_y - slope * mean_x
        last_ts = hourly.index[-1]
        for i in range(1, forecast_hours + 1):
            forecast.append(max(0.0, min(100.0, slope * (n - 1 + i) + intercept)))
            forecast_labels.append((last_ts + pd.Timedelta(hours=i)).strftime("%Y-%m-%d %H:%M"))

    kpis = [
        Kpi("CPU hourly points (SMF70)", n),
        Kpi("Avg. CPU busy %", avg(series)),
        Kpi("Forecast (+24h) %", round(forecast[-1], 1) if forecast else 0.0),
        *_truncation_kpi([cpu_raw], limit),
    ]

    chart = None
    columns: list[Column] = []
    rows: list[dict] = []
    if n >= 2 and forecast:
        labels = obs_labels + forecast_labels
        chart = {
            "kind": "line",
            "labels": labels,
            "series": [
                {"name": "CPU busy % (observed)", "data": series + [None] * forecast_hours},
                {"name": "Forecast (linear, NOT ML)", "data": [None] * n + forecast, "dashed": True},
            ],
        }
        columns = [
            Column("point", "Point", "Hourly timestamp.", True, kind="datetime"),
            Column("observedCpuPct", "CPU busy % (observed)", "Observed hourly mean CPU busy %.", True, numeric=True),
            Column("forecastCpuPct", "Forecast CPU busy %", "Linearly extrapolated CPU busy %.", True, numeric=True),
            Column("isForecast", "Forecast", "Whether this row is forecasted.", True, kind='bool'),
        ]
        rows = [
            {"point": obs_labels[i], "observedCpuPct": round(series[i], 2), "forecastCpuPct": None, "isForecast": False}
            for i in range(n)
        ] + [
            {"point": forecast_labels[i], "observedCpuPct": None, "forecastCpuPct": round(forecast[i], 2), "isForecast": True}
            for i in range(forecast_hours)
        ]

    return SmfType(
        id=X_CPU_FORECAST, title=CROSS_ANALYSIS_TITLES[X_CPU_FORECAST], category=CAT_CROSS,
        description=CROSS_ANALYSIS_DESCRIPTIONS[X_CPU_FORECAST], viz="timeseries", order=2,
        kpis=kpis, chart=chart, columns=columns, rows=rows,
    )


def build_x_wlm_bottleneck(session: Session, hours: int = 24) -> SmfType:
    start_time, end_time = _time_window(hours)
    limit = _query_limit(session)

    wlm_raw = query_layer.run_query(
        session, "SMF72S3", ["timestamp", "sample_cpu_delay"],
        start_time=start_time, end_time=end_time, limit=limit,
        system_name=session.system_name,
    )
    cpu_raw = query_layer.run_query(
        session, "SMF70S1", ["timestamp", "cpu_busy_percentage"],
        start_time=start_time, end_time=end_time, limit=limit,
        system_name=session.system_name,
    )
    dasd_raw = query_layer.run_query(
        session, "SMF74S1", ["dev", "atd"],
        start_time=start_time, end_time=end_time, limit=limit,
        system_name=session.system_name,
    )

    wlm_idx = _ensure_datetime_index(wlm_raw, ["sample_cpu_delay"])
    cpu_idx = _ensure_datetime_index(cpu_raw, ["cpu_busy_percentage"])
    if not cpu_idx.empty and "cpu_busy_percentage" in cpu_idx.columns:
        cpu_idx["cpu_busy_percentage"] = _scale_cpu_busy(cpu_idx["cpu_busy_percentage"])

    delay_h = _hourly_mean(wlm_idx, "sample_cpu_delay")
    busy_h = _hourly_mean(cpu_idx, "cpu_busy_percentage")
    joined = pd.concat([delay_h.rename("delay"), busy_h.rename("busy")], axis=1).dropna()

    kpis = [
        Kpi("WLM records (SMF72S3)", len(wlm_raw)),
        Kpi("CPU records (SMF70)", len(cpu_raw)),
        Kpi("DASD records (SMF74S1)", len(dasd_raw)),
        *_truncation_kpi([wlm_raw, cpu_raw, dasd_raw], limit),
    ]
    if not joined.empty:
        kpis.append(Kpi("Avg. CPU delay (WLM)", round(float(joined["delay"].mean()), 2)))
        kpis.append(Kpi("Avg. CPU busy %", round(float(joined["busy"].mean()), 2)))

    chart = None
    columns: list[Column] = []
    rows: list[dict] = []
    n = len(joined)
    if n > 1:
        labels = [ts.strftime("%Y-%m-%d %H:%M") for ts in joined.index]
        delay = joined["delay"].tolist()
        busy = joined["busy"].tolist()
        chart = {
            "kind": "line",
            "labels": labels,
            "series": [
                {"name": "CPU delay (WLM)", "data": delay, "yAxis": 0, "yAxisName": "CPU delay"},
                {"name": "CPU busy %", "data": busy, "yAxis": 1, "yAxisName": "CPU busy %"},
            ],
        }
        columns = [
            Column("sample", "Hour", "Hourly interval start.", True, kind="datetime"),
            Column("cpuDelay", "CPU delay (WLM)", "Mean WLM CPU delay this hour.", True, numeric=True),
            Column("cpuBusyPct", "CPU busy %", "Mean system CPU busy % this hour.", True, numeric=True),
        ]
        rows = [
            {"sample": labels[i], "cpuDelay": round(delay[i], 2), "cpuBusyPct": round(busy[i], 2)}
            for i in range(n)
        ]

    return SmfType(
        id=X_WLM_BOTTLENECK, title=CROSS_ANALYSIS_TITLES[X_WLM_BOTTLENECK], category=CAT_CROSS,
        description=CROSS_ANALYSIS_DESCRIPTIONS[X_WLM_BOTTLENECK], viz="timeseries", order=3,
        kpis=kpis, chart=chart, columns=columns, rows=rows,
        highlight=Highlight("cpuDelay", "gt", 80, "warn"),
    )


def build_x_paging_pressure(session: Session, hours: int = 24) -> SmfType:
    start_time, end_time = _time_window(hours)
    limit = _query_limit(session)

    paging_raw = query_layer.run_query(
        session, "SMF71S1", ["timestamp", "pin", "pot", "sin", "sot", "avf"],
        start_time=start_time, end_time=end_time, limit=limit,
        system_name=session.system_name,
    )
    cpu_raw = query_layer.run_query(
        session, "SMF70S1", ["timestamp", "cpu_busy_percentage"],
        start_time=start_time, end_time=end_time, limit=limit,
        system_name=session.system_name,
    )

    paging_idx = _ensure_datetime_index(paging_raw, ["pin", "pot", "sin", "sot", "avf"])
    cpu_idx = _ensure_datetime_index(cpu_raw, ["cpu_busy_percentage"])
    if not cpu_idx.empty and "cpu_busy_percentage" in cpu_idx.columns:
        cpu_idx["cpu_busy_percentage"] = _scale_cpu_busy(cpu_idx["cpu_busy_percentage"])

    pin_h = _hourly_mean(paging_idx, "pin")
    pot_h = _hourly_mean(paging_idx, "pot")
    sin_h = _hourly_mean(paging_idx, "sin")
    sot_h = _hourly_mean(paging_idx, "sot")
    avf_h = _hourly_mean(paging_idx, "avf")
    busy_h = _hourly_mean(cpu_idx, "cpu_busy_percentage")
    joined = pd.concat(
        [
            pin_h.rename("pin"), pot_h.rename("pot"), sin_h.rename("sin"),
            sot_h.rename("sot"), avf_h.rename("avf"), busy_h.rename("busy"),
        ],
        axis=1,
    ).dropna(subset=["pin", "busy"])

    pin = joined["pin"].tolist() if not joined.empty else []
    busy = joined["busy"].tolist() if not joined.empty else []
    n = len(joined)
    corr = pearson(pin, busy) if n > 1 else 0.0
    swap_events = int(((joined["sin"].fillna(0) > 0) | (joined["sot"].fillna(0) > 0)).sum()) if n else 0

    kpis = [
        Kpi("Paging records (SMF71S1)", len(paging_raw)),
        Kpi("Paging↔CPU correlation", round(corr, 3)),
        Kpi("Intervals with active swapping", swap_events),
        *_truncation_kpi([paging_raw, cpu_raw], limit),
    ]

    chart = None
    columns: list[Column] = []
    rows: list[dict] = []
    if n > 1:
        labels = [ts.strftime("%Y-%m-%d %H:%M") for ts in joined.index]
        chart = {
            "kind": "line",
            "labels": labels,
            "series": [
                {"name": "Page-in rate", "data": pin, "yAxis": 0, "yAxisName": "Page-in rate"},
                {"name": "CPU busy %", "data": busy, "yAxis": 1, "yAxisName": "CPU busy %"},
            ],
        }
        columns = [
            Column("interval", "Hour", "Hourly interval start.", True, kind="datetime"),
            Column("pageInRate", "Page-in rate", "Mean page-ins excluding VIO/swap.", True, numeric=True),
            Column("pageOutRate", "Page-out rate", "Mean page-outs excluding VIO/swap.", True, numeric=True),
            Column("swapInRate", "Swap-in rate", "Mean swap-in pages.", False, numeric=True),
            Column("swapOutRate", "Swap-out rate", "Mean swap-out pages.", False, numeric=True),
            Column("availFrames", "Avail. page frames", "Mean available central storage frames.", False, numeric=True),
            Column("cpuBusyPct", "CPU busy %", "Mean system CPU busy %.", True, numeric=True),
            Column("swappingActive", "Swapping active", "Whether swap activity was observed.", True, kind='bool'),
        ]
        for i, ts_label in enumerate(labels):
            si = float(joined["sin"].iloc[i] or 0)
            so = float(joined["sot"].iloc[i] or 0)
            rows.append({
                "interval": ts_label,
                "pageInRate": round(float(joined["pin"].iloc[i]), 2),
                "pageOutRate": round(float(joined["pot"].iloc[i]), 2) if pd.notna(joined["pot"].iloc[i]) else None,
                "swapInRate": round(si, 2),
                "swapOutRate": round(so, 2),
                "availFrames": round(float(joined["avf"].iloc[i]), 2) if pd.notna(joined["avf"].iloc[i]) else None,
                "cpuBusyPct": round(busy[i], 2),
                "swappingActive": si > 0 or so > 0,
            })

    return SmfType(
        id=X_PAGING_PRESSURE, title=CROSS_ANALYSIS_TITLES[X_PAGING_PRESSURE], category=CAT_CROSS,
        description=CROSS_ANALYSIS_DESCRIPTIONS[X_PAGING_PRESSURE], viz="timeseries", order=4,
        kpis=kpis, chart=chart, columns=columns, rows=rows,
        highlight=Highlight("swappingActive", "eq", True, "warn"),
    )


def build_x_enqueue_contention(session: Session, hours: int = 24) -> SmfType:
    start_time, end_time = _time_window(hours)
    limit = _query_limit(session)

    enq_df = query_layer.run_query(
        session, "SMF77S1", ["qnm", "rnm", "evt", "jobs_waiting", "wtt", "wtx"],
        start_time=start_time, end_time=end_time, limit=limit,
        system_name=session.system_name,
    )

    kpis = [Kpi("Enqueue records (SMF77S1)", len(enq_df)), *_truncation_kpi([enq_df], limit)]

    columns: list[Column] = []
    rows: list[dict] = []
    chart = None
    if not enq_df.empty and "qnm" in enq_df:
        grouped = enq_df.groupby("qnm", dropna=False).agg(
            contentionEvents=("evt", "sum") if "evt" in enq_df else ("qnm", "count"),
            jobsWaiting=("jobs_waiting", "sum") if "jobs_waiting" in enq_df else ("qnm", "count"),
            maxWaitTime=("wtx", "max") if "wtx" in enq_df else ("qnm", "count"),
            totalWaitTime=("wtt", "sum") if "wtt" in enq_df else ("qnm", "count"),
        ).reset_index().rename(columns={"qnm": "resource"})
        grouped = grouped.sort_values("totalWaitTime", ascending=False)
        rows = grouped.to_dict("records")
        columns = [
            Column("resource", "Resource", "ENQ major resource name.", True),
            Column("contentionEvents", "Contention events", "Total contention events for this resource.", True, numeric=True),
            Column("jobsWaiting", "Jobs waiting", "Total jobs observed waiting on this resource.", True, numeric=True),
            Column("maxWaitTime", "Max wait time", "Maximum observed waiting time.", True, numeric=True),
            Column("totalWaitTime", "Total wait time", "Sum of waiting time across samples.", True, numeric=True),
        ]
        kpis.append(Kpi("Distinct resources", len(rows)))
        if rows:
            kpis.append(Kpi("Most contested resource", rows[0]["resource"]))
        top = rows[:15]
        chart = {
            "kind": "bar",
            "labels": [str(r["resource"]) for r in top],
            "series": [{"name": "Total wait time", "data": [r["totalWaitTime"] for r in top]}],
        }

    return SmfType(
        id=X_ENQUEUE_CONTENTION, title=CROSS_ANALYSIS_TITLES[X_ENQUEUE_CONTENTION], category=CAT_CROSS,
        description=CROSS_ANALYSIS_DESCRIPTIONS[X_ENQUEUE_CONTENTION], viz="table", order=5,
        kpis=kpis, chart=chart, columns=columns, rows=rows,
    )


def build_x_job_risk(session: Session, hours: int = 24) -> SmfType:
    start_time, end_time = _time_window(hours)
    limit = _query_limit(session)

    job_df = query_layer.run_query(
        session, "SMF30S4", ["job_name", "abd", "step_time", "srb_step_cpu_time"],
        start_time=start_time, end_time=end_time, limit=limit,
        system_name=session.system_name,
    )

    kpis = [Kpi("Job step records (SMF30S4)", len(job_df)), *_truncation_kpi([job_df], limit)]

    columns: list[Column] = []
    rows: list[dict] = []
    if not job_df.empty and "job_name" in job_df:
        job_df = job_df.copy()
        job_df["cpuSec"] = _col_or_zero(job_df, "step_time") + _col_or_zero(job_df, "srb_step_cpu_time")
        job_df["abendFlag"] = _col_or_false(job_df, "abd")
        cpu_p90 = job_df["cpuSec"].quantile(0.9) if len(job_df) > 1 else 0.0
        grouped = job_df.groupby("job_name").agg(
            abends=("abendFlag", "sum"), totalCpuSec=("cpuSec", "sum"), avgCpuSec=("cpuSec", "mean"),
        ).reset_index().rename(columns={"job_name": "jobName"})
        grouped["riskScore"] = grouped["abends"] * 5 + (grouped["avgCpuSec"] > cpu_p90).astype(int) * 3
        grouped["totalCpuSec"] = grouped["totalCpuSec"].round(1)
        grouped["avgCpuSec"] = grouped["avgCpuSec"].round(1)
        grouped = grouped.sort_values("riskScore", ascending=False)
        rows = grouped.to_dict("records")
        columns = [
            Column("jobName", "Job", "Job/session name.", True),
            Column("riskScore", "Risk score", "Heuristic risk score (abends×5 + high-CPU-outlier bonus).", True, numeric=True),
            Column("abends", "Abends", "Number of step abends observed.", True, numeric=True),
            Column("totalCpuSec", "Total CPU (s)", "Total step + SRB CPU time consumed.", True, numeric=True),
            Column("avgCpuSec", "Avg. CPU (s)", "Average step + SRB CPU time per step.", True, numeric=True),
        ]
        kpis.append(Kpi("Jobs scored", len(rows)))
        if rows:
            kpis.append(Kpi("Highest risk", f"{rows[0]['jobName']} ({rows[0]['riskScore']} pts)"))

    return SmfType(
        id=X_JOB_RISK, title=CROSS_ANALYSIS_TITLES[X_JOB_RISK], category=CAT_CROSS,
        description=CROSS_ANALYSIS_DESCRIPTIONS[X_JOB_RISK], viz="table", order=6,
        kpis=kpis, columns=columns, rows=rows,
        highlight=Highlight("riskScore", "gt", 5, "bad"),
    )


CROSS_ANALYSIS_BUILDERS = {
    X_ALERTS: build_x_alerts,
    X_CPU_BATCH: build_x_cpu_batch,
    X_CPU_FORECAST: build_x_cpu_forecast,
    X_WLM_BOTTLENECK: build_x_wlm_bottleneck,
    X_PAGING_PRESSURE: build_x_paging_pressure,
    X_ENQUEUE_CONTENTION: build_x_enqueue_contention,
    X_JOB_RISK: build_x_job_risk,
}
