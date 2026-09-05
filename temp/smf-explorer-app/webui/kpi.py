"""KPI cards."""
from nicegui import ui

from smf_types.core import Kpi


def render_kpis(kpis: list[Kpi]) -> None:
    if not kpis:
        return
    with ui.row().classes('gap-3 w-full flex-wrap mb-4'):
        for k in kpis:
            with ui.card().tight().classes('kpi-card px-4 py-3 shadow-1'):
                ui.label(k.text()).classes('kpi-value font-bold text-primary')
                ui.label(k.label).classes('text-xs opacity-60')
