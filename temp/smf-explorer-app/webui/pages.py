"""NiceGUI routes: dashboard and per-type SMF views (session-guarded)."""
from __future__ import annotations

import time
from datetime import datetime, timedelta

from fastapi import Request
from nicegui import run, ui

from app_core import query as query_layer
from app_core.session import UnknownField, dataframe_to_records
from smf_types.catalog import CATALOG_BY_ID
from smf_types.core import Kpi, SmfType
from smf_types.cross_analysis import (
    CROSS_ANALYSIS_BUILDERS,
    CROSS_ANALYSIS_REQUIRES,
)
from smf_types.curation import apply_curation, query_field_names

from . import chart, data_table, kpi, layout, theme
from .login import register_login_page, require_session

# Apply domain overrides once at import (after catalog load).
apply_curation(CATALOG_BY_ID)


def _parse_params(request: Request, session) -> tuple[int, bool]:
    try:
        hours = int(request.query_params.get('hours', 24))
    except (TypeError, ValueError):
        hours = 24
    if hours not in layout.HOURS_OPTIONS:
        hours = min(layout.HOURS_OPTIONS, key=lambda h: abs(h - hours))
    dark = request.query_params.get('dark', '1') in ('1', 'true', 'True')

    system = request.query_params.get('system')
    if system is not None:
        session.system_name = system.strip() or None

    limit_raw = request.query_params.get('limit')
    if limit_raw is not None:
        try:
            limit = int(limit_raw)
            if limit in layout.LIMIT_OPTIONS:
                session.query_limit = limit
        except (TypeError, ValueError):
            pass

    return hours, dark


def _show_loading(container) -> ui.timer:
    start = time.time()
    with container:
        ui.linear_progress(show_value=False).props('indeterminate color=primary').classes('w-full')
        elapsed_label = ui.label('Querying… 0.0 s').classes('text-xs opacity-60 mt-1')

    def tick() -> None:
        elapsed_label.set_text(f'Querying… {time.time() - start:.1f} s')

    return ui.timer(0.2, tick)


def _run_query_fields(session, record_module: str, field_names: list[str], hours: int):
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    known = query_layer.filter_known_fields(record_module, field_names)
    if not known:
        raise UnknownField(f"No resolvable fields for {record_module}")
    return query_layer.run_query(
        session, record_module, known,
        start_time=start_time, end_time=end_time,
    )


def _load_smf_type_sync(session, type_id: str, hours: int) -> SmfType | None:
    spec = CATALOG_BY_ID.get(type_id)
    if spec is None:
        return None

    field_names = query_field_names(spec)
    df = _run_query_fields(session, spec.record_module, field_names, hours)
    rows = dataframe_to_records(df)

    kpis = spec.build_kpis(df) if spec.build_kpis else []
    chart_data = spec.build_chart(df) if spec.build_chart else None
    limit = session.query_limit or 5000
    if len(df) >= limit:
        kpis = [*kpis, Kpi("Result truncated", f"hit limit {limit}")]

    # Only expose columns that came back (plus curated defaults that may be empty).
    present = set(df.columns)
    columns = [c for c in spec.columns if c.key in present] or list(spec.columns)

    return SmfType(
        id=spec.id, title=spec.title, category=spec.category,
        description=spec.description, viz=spec.viz, order=spec.order,
        kpis=kpis, columns=columns, rows=rows,
        highlight=spec.highlight, chart=chart_data, live_capable=spec.live_capable,
    )


async def _load_smf_type(session, type_id: str, hours: int) -> SmfType | None:
    return await run.io_bound(_load_smf_type_sync, session, type_id, hours)


def _type_available(session, type_id: str) -> bool:
    key = layout.parse_type_id(type_id)
    return key is not None and session.has_type(*key)


def _cross_available(session, type_id: str) -> bool:
    required = CROSS_ANALYSIS_REQUIRES.get(type_id)
    if required is None:
        return False
    return session.has_types(required)


async def _refresh_and_navigate(session, type_id: str | None, hours: int, dark: bool) -> None:
    try:
        await run.io_bound(query_layer.refresh_available, session)
    except Exception as exc:
        ui.notify(f'Discover refresh failed: {type(exc).__name__}', type='negative')
    ui.navigate.to(
        layout.nav_url(type_id, hours, dark, system=session.system_name, limit=session.query_limit)
    )


def register_pages() -> None:
    register_login_page()

    def shell(session, active_id: str | None, hours: int, dark: bool):
        theme.install()
        dark_mode = ui.dark_mode(dark)
        layout.build_header(session, active_id, hours, dark)
        with ui.left_drawer(fixed=True).classes('p-0').style('width: 320px'):
            layout.build_menu(session, active_id, hours, dark)
        return dark_mode

    @ui.page('/')
    async def index_page(request: Request) -> None:
        session = require_session()
        if session is None:
            return
        hours, dark = _parse_params(request, session)
        dark_mode = shell(session, None, hours, dark)

        with ui.column().classes('w-full max-w-6xl mx-auto p-4'):
            layout.build_controls(
                session, None, hours, dark,
                on_refresh=lambda s=session, h=hours, d=dark: _refresh_and_navigate(s, None, h, d),
            )
            ui.label('System overview (Dashboard)').classes('text-xl font-bold mb-1')
            ui.label(
                'The left menu lists only SMF types present in the connected dataset '
                '(from discover). Select a type for KPIs, charts, and a data table.'
            ).classes('smf-desc mb-3')

            available_box = ui.column().classes('w-full')
            observations_box = ui.column().classes('w-full')
            with observations_box:
                ui.label('Key observations').classes('text-lg font-bold mt-5 mb-1')
            observations_timer = _show_loading(observations_box)

        await ui.context.client.connected()

        # Prefer session cache from login; refresh if empty.
        if not session.available:
            try:
                await run.io_bound(query_layer.refresh_available, session)
            except Exception as exc:
                with available_box:
                    ui.label(f'Failed to fetch available records: {type(exc).__name__}').classes(
                        'text-negative text-sm'
                    )

        with available_box:
            ui.label(
                f'Available record types in dataset "{session.dataset_name}": {len(session.available)}'
            ).classes('text-sm opacity-70 mb-2')
            if session.available:
                with ui.row().classes('gap-2 flex-wrap'):
                    for (smf_type, subtype), count in sorted(session.available.items()):
                        ui.badge(
                            f'SMF {smf_type}-{subtype} ({count})', color='grey-8'
                        ).classes('smf-badge')
            else:
                ui.label('Discover returned no record types.').classes('text-sm opacity-70')

        if 'x-alerts' in CROSS_ANALYSIS_BUILDERS and _cross_available(session, 'x-alerts'):
            try:
                alerts_smf = await run.io_bound(CROSS_ANALYSIS_BUILDERS['x-alerts'], session, hours)
                observations_timer.cancel()
                observations_box.clear()
                with observations_box:
                    ui.label('Key observations').classes('text-lg font-bold mt-5 mb-1')
                    kpi.render_kpis(alerts_smf.kpis)
                    if alerts_smf.rows:
                        severity_icon = {'High': '🔴', 'Medium': '🟠', 'Low': '🟡'}
                        with ui.column().classes('gap-1 w-full'):
                            for a in alerts_smf.rows[:6]:
                                icon = severity_icon.get(a.get('severity'), '⚪')
                                ui.label(
                                    f"{icon} [{a.get('source')}] {a.get('event')} — {a.get('detail')}"
                                ).classes('text-sm')
                        ui.link(
                            'View full alert feed →',
                            target=layout.nav_url(
                                'x-alerts', hours, dark,
                                system=session.system_name, limit=session.query_limit,
                            ),
                        ).classes('text-sm mt-1')
                    else:
                        ui.label('No anomalies detected in the selected window.').classes(
                            'text-sm opacity-70'
                        )
            except Exception as exc:
                observations_timer.cancel()
                observations_box.clear()
                with observations_box:
                    ui.label('Key observations').classes('text-lg font-bold mt-5 mb-1')
                    ui.label(
                        f'Failed to build anomaly summary: {type(exc).__name__}'
                    ).classes('text-negative text-sm')
        else:
            observations_timer.cancel()
            observations_box.clear()
            with observations_box:
                ui.label('Key observations').classes('text-lg font-bold mt-5 mb-1')
                ui.label(
                    'Alert feed unavailable — required SMF types are missing from this dataset.'
                ).classes('text-sm opacity-70')

    @ui.page('/view/{type_id}')
    async def view_page(type_id: str, request: Request) -> None:
        session = require_session()
        if session is None:
            return
        hours, dark = _parse_params(request, session)
        dark_mode = shell(session, type_id, hours, dark)

        is_cross = type_id in CROSS_ANALYSIS_BUILDERS
        spec = None if is_cross else CATALOG_BY_ID.get(type_id)

        if spec is None and not is_cross:
            with ui.column().classes('w-full max-w-6xl mx-auto p-4'):
                ui.label(f'Unknown SMF type: "{type_id}".').classes('text-red-500 text-lg')
                ui.link(
                    '← Back to overview',
                    target=layout.nav_url(None, hours, dark, system=session.system_name, limit=session.query_limit),
                )
            return

        if is_cross and not _cross_available(session, type_id):
            with ui.column().classes('w-full max-w-6xl mx-auto p-4'):
                ui.label(
                    f'Cross analysis "{type_id}" is not available in this dataset '
                    '(required SMF types are missing).'
                ).classes('text-red-500 text-lg')
                ui.link(
                    '← Back to overview',
                    target=layout.nav_url(None, hours, dark, system=session.system_name, limit=session.query_limit),
                )
            return

        if not is_cross and not _type_available(session, type_id):
            with ui.column().classes('w-full max-w-6xl mx-auto p-4'):
                ui.label(
                    f'SMF {type_id} is not present in dataset "{session.dataset_name}".'
                ).classes('text-red-500 text-lg')
                ui.link(
                    '← Back to overview',
                    target=layout.nav_url(None, hours, dark, system=session.system_name, limit=session.query_limit),
                )
            return

        with ui.column().classes('w-full max-w-6xl mx-auto p-4'):
            layout.build_controls(
                session, type_id, hours, dark,
                on_refresh=lambda s=session, t=type_id, h=hours, d=dark: _refresh_and_navigate(s, t, h, d),
            )
            content_box = ui.column().classes('w-full')
            loading_timer = _show_loading(content_box)

        await ui.context.client.connected()

        try:
            if is_cross:
                smf = await run.io_bound(CROSS_ANALYSIS_BUILDERS[type_id], session, hours)
            else:
                smf = await _load_smf_type(session, type_id, hours)
        except Exception as exc:
            loading_timer.cancel()
            content_box.clear()
            with content_box:
                ui.label(f'Query error: {type(exc).__name__}').classes('text-negative')
            return

        loading_timer.cancel()
        content_box.clear()
        with content_box:
            with ui.row().classes('items-center gap-2 mb-1 flex-wrap'):
                tag = 'ANALYSIS' if is_cross else f'SMF {smf.id}'
                ui.badge(tag, color='grey-8').classes('smf-badge')
                ui.label(smf.title).classes('text-xl font-bold')
            ui.label(smf.description).classes('smf-desc mb-3')

            kpi.render_kpis(smf.kpis)

            if smf.chart and smf.columns:
                with ui.tabs().classes('w-full') as tabs:
                    tab_chart = ui.tab('Chart')
                    tab_table = ui.tab('Table')
                with ui.tab_panels(tabs, value=tab_chart).classes('w-full'):
                    with ui.tab_panel(tab_chart):
                        chart.render_chart(smf.chart, dark_mode.value)
                    with ui.tab_panel(tab_table):
                        data_table.render_table(smf, dark_mode.value)
            elif smf.chart:
                chart.render_chart(smf.chart, dark_mode.value)
            elif smf.columns:
                data_table.render_table(smf, dark_mode.value)
            else:
                ui.label('No data to display for this type.').classes('opacity-60')
