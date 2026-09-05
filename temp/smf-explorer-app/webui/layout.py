"""Header, sidebar menu, and time-range controls (filtered by session.available)."""
from __future__ import annotations

from nicegui import ui

from app_core.session import Session
from smf_types.catalog import CATALOG
from smf_types.cross_analysis import (
    CROSS_ANALYSIS_IDS,
    CROSS_ANALYSIS_REQUIRES,
    CROSS_ANALYSIS_TITLES,
)
from smf_types.dictionaries import CATEGORY_ORDER
from webui.login import logout

HOURS_OPTIONS = [1, 6, 12, 24, 48, 72, 120]
LIMIT_OPTIONS = [500, 1000, 2500, 5000, 10000]


def nav_url(
    type_id: str | None,
    hours: int,
    dark: bool = True,
    *,
    system: str | None = None,
    limit: int | None = None,
) -> str:
    base = '/' if type_id is None else f'/view/{type_id}'
    parts = [f'hours={hours}', f'dark={"1" if dark else "0"}']
    if system:
        parts.append(f'system={system}')
    if limit is not None:
        parts.append(f'limit={limit}')
    return f'{base}?{"&".join(parts)}'


def parse_type_id(type_id: str) -> tuple[int, int] | None:
    """'70-1' / '74-10' -> (70, 1) / (74, 10)."""
    try:
        type_str, subtype_str = type_id.split('-', 1)
        return int(type_str), int(subtype_str)
    except (TypeError, ValueError):
        return None


def catalog_by_category() -> dict[str, list]:
    grouped: dict[str, list] = {}
    for spec in CATALOG:
        grouped.setdefault(spec.category, []).append(spec)
    return grouped


def build_header(session: Session, active_id: str | None, hours: int, dark: bool) -> None:
    with ui.header().classes('items-center justify-between px-4 py-2 gap-4'):
        with ui.link(target=nav_url(None, hours, dark, system=session.system_name, limit=session.query_limit)).classes('no-underline text-inherit'):
            with ui.row().classes('items-center gap-2'):
                ui.icon('dns', size='28px')
                ui.label('SMF Explorer').classes('text-lg font-bold')
                ui.badge(session.dataset_name or '—', color='teal').classes('smf-badge')
        with ui.row().classes('items-center gap-3'):
            ui.button(
                icon='light_mode' if dark else 'dark_mode',
                on_click=lambda: ui.navigate.to(
                    nav_url(active_id, hours, not dark, system=session.system_name, limit=session.query_limit)
                ),
            ).props('flat round dense').tooltip('Toggle light/dark mode')
            ui.button('Sign out', icon='logout', on_click=logout).props('flat dense')


def build_menu(session: Session, active_id: str | None, hours: int, dark: bool) -> None:
    available = session.available
    grouped = catalog_by_category()
    sys = session.system_name
    lim = session.query_limit

    with ui.column().classes('gap-0 w-full py-2'):
        with ui.link(target=nav_url(None, hours, dark, system=sys, limit=lim)).classes('no-underline text-inherit'):
            with ui.row().classes('items-center gap-2 mx-3 my-1 px-3 py-2 rounded-borders overview-btn'):
                ui.icon('dashboard')
                ui.label('Overview (Dashboard)').classes('font-semibold text-sm')

        if not available:
            ui.label('No SMF types in this dataset.').classes('text-xs opacity-60 mx-3 my-2')
            return

        visible_cross = [
            x_id for x_id in CROSS_ANALYSIS_IDS
            if session.has_types(CROSS_ANALYSIS_REQUIRES.get(x_id, set()))
        ]
        if visible_cross:
            ui.label('Cross analyses').classes('menu-cat-title')
            for x_id in visible_cross:
                cls = 'menu-item px-3 py-2 no-underline text-inherit block'
                if x_id == active_id:
                    cls += ' active'
                with ui.link(target=nav_url(x_id, hours, dark, system=sys, limit=lim)).classes(cls):
                    with ui.row().classes('items-center gap-2 flex-nowrap'):
                        ui.badge('X', color='teal').classes('smf-badge cross-badge')
                        ui.label(CROSS_ANALYSIS_TITLES[x_id]).classes('text-sm')

        for cat in CATEGORY_ORDER:
            items = grouped.get(cat)
            if not items:
                continue
            visible = []
            for spec in sorted(items, key=lambda s: s.order):
                key = parse_type_id(spec.id)
                if key is None or key not in available:
                    continue
                visible.append((spec, available[key]))
            if not visible:
                continue
            ui.label(cat).classes('menu-cat-title')
            for spec, count in visible:
                cls = 'menu-item px-3 py-2 no-underline text-inherit block'
                if spec.id == active_id:
                    cls += ' active'
                with ui.link(target=nav_url(spec.id, hours, dark, system=sys, limit=lim)).classes(cls):
                    with ui.row().classes('items-center gap-2 flex-nowrap'):
                        ui.badge(f'SMF {spec.id} ({count})', color='grey-8').classes('smf-badge')
                        ui.label(spec.title).classes('text-sm')


def build_controls(session: Session, type_id: str | None, hours: int, dark: bool, on_refresh) -> None:
    """Time range + system filter + row limit + refresh."""
    sys = session.system_name
    lim = session.query_limit

    with ui.row().classes('items-center gap-3 mb-3 flex-wrap'):
        ui.label('Range:').classes('text-xs opacity-60')
        with ui.button_group().props('outline'):
            for h in HOURS_OPTIONS:
                btn = ui.button(
                    f'{h}h',
                    on_click=lambda h=h: ui.navigate.to(
                        nav_url(type_id, h, dark, system=session.system_name, limit=session.query_limit)
                    ),
                ).props('dense')
                if h == hours:
                    btn.props('unelevated color=primary')

        ui.label('Limit:').classes('text-xs opacity-60')
        with ui.button_group().props('outline'):
            for n in LIMIT_OPTIONS:
                btn = ui.button(
                    str(n),
                    on_click=lambda n=n: _set_limit_and_nav(session, type_id, hours, dark, n),
                ).props('dense')
                if n == lim:
                    btn.props('unelevated color=primary')

        system_input = ui.input(
            placeholder='System (optional)',
            value=sys or '',
        ).props('dense outlined clearable').classes('w-40')

        def apply_system() -> None:
            value = (system_input.value or '').strip() or None
            session.system_name = value
            ui.navigate.to(nav_url(type_id, hours, dark, system=value, limit=session.query_limit))

        ui.button('Apply system', on_click=apply_system).props('outline dense')
        ui.button(icon='refresh', on_click=on_refresh).props('flat dense round').tooltip(
            'Re-run discover + query'
        )


def _set_limit_and_nav(session: Session, type_id: str | None, hours: int, dark: bool, limit: int) -> None:
    session.query_limit = limit
    ui.navigate.to(nav_url(type_id, hours, dark, system=session.system_name, limit=limit))
