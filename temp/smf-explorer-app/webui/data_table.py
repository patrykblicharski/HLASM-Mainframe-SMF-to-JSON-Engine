"""AG Grid table with search, column picker, and CSV/JSON/PDF export."""
from __future__ import annotations

import json

from nicegui import ui

import export_utils
from smf_types.core import Column, SmfType

_OP_JS = {'gt': '>', 'lt': '<', 'eq': '===', 'neq': '!=='}


def _row_class_rules(smf: SmfType) -> dict:
    if not smf.highlight:
        return {}
    h = smf.highlight
    op = _OP_JS.get(h.op, '===')
    value_js = json.dumps(h.value)
    return {f'row-{h.cls}': f'data.{h.key} {op} {value_js}'}


def _column_def(col: Column) -> dict:
    cd = {
        'field': col.key, 'headerName': col.label, 'sortable': True, 'filter': True,
        'resizable': True, 'tooltipField': col.key,
    }
    if col.numeric:
        cd['type'] = 'numericColumn'
        cd['filter'] = 'agNumberColumnFilter'
    return cd


def open_column_dialog(smf: SmfType, visible: set[str], on_apply) -> None:
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
        ui.label(f'Columns — {smf.title}').classes('text-lg font-bold')
        ui.label(
            'Select the columns to display. "Non-default" fields are additional fields of the '
            'same SMF record, available in the data but not shown by default.'
        ).classes('text-sm opacity-70 mb-2')
        checks: dict[str, ui.checkbox] = {}
        with ui.column().classes('gap-0 w-full').style('max-height: 60vh; overflow-y: auto'):
            for col in smf.columns:
                with ui.row().classes('items-start gap-2 w-full py-1').style(
                        'border-bottom: 1px solid rgba(127,127,127,.15)'):
                    cb = ui.checkbox(value=col.key in visible).props('dense')
                    checks[col.key] = cb
                    with ui.column().classes('gap-0 flex-grow'):
                        with ui.row().classes('items-center gap-2'):
                            ui.label(col.label).classes('text-sm font-medium')
                            if col.default:
                                ui.badge('default', color='grey-7').classes('smf-badge')
                            else:
                                ui.badge('non-default', color='teal').classes('smf-badge')
                        ui.label(col.description).classes('text-xs opacity-60')
        with ui.row().classes('w-full justify-end gap-2 mt-3'):
            def select_all():
                for cb in checks.values():
                    cb.value = True

            def select_default():
                for key, cb in checks.items():
                    cb.value = next(c.default for c in smf.columns if c.key == key)

            ui.button('Select all', on_click=select_all).props('flat dense')
            ui.button('Defaults only', on_click=select_default).props('flat dense')
            ui.space()
            ui.button('Cancel', on_click=dialog.close).props('flat')

            def apply_and_close():
                selected = {k for k, cb in checks.items() if cb.value}
                if not selected:
                    ui.notify('Select at least one column.', type='warning')
                    return
                on_apply(selected)
                dialog.close()

            ui.button('Apply', on_click=apply_and_close).props('unelevated color=primary')
    dialog.open()


def render_table(smf: SmfType, dark: bool):
    """Renders toolbar + table. Returns the `@ui.refreshable` object responsible
    for the data grid — calling `.refresh()` on it after `smf.rows` changes
    (e.g. after appending a live record) redraws the table without reloading the page."""
    if not smf.columns:
        ui.label('No columns defined for this view.').classes('opacity-60')
        return None

    state = {
        'visible': {c.key for c in smf.columns if c.default} or {smf.columns[0].key},
        'search': '',
    }

    def current_columns() -> list[Column]:
        cols = [c for c in smf.columns if c.key in state['visible']]
        return cols or smf.columns[:1]

    def current_rows() -> list[dict]:
        term = state['search'].strip().lower()
        if not term:
            return smf.rows
        return [r for r in smf.rows if any(term in str(r.get(c.key, '')).lower() for c in smf.columns)]

    count_label = {'el': None}

    @ui.refreshable
    def grid_area() -> None:
        cols = current_columns()
        rows = current_rows()
        if count_label['el'] is not None:
            count_label['el'].set_text(f'{len(smf.rows)} rows total (visible: {len(rows)})')
        theme_cls = 'ag-theme-alpine-dark' if dark else 'ag-theme-alpine'
        ui.aggrid({
            'columnDefs': [_column_def(c) for c in cols],
            'rowData': rows,
            'defaultColDef': {'sortable': True, 'filter': True, 'resizable': True, 'minWidth': 110},
            'pagination': True,
            'paginationPageSize': 25,
            'paginationPageSizeSelector': [10, 25, 50, 100],
            'rowClassRules': _row_class_rules(smf),
            'domLayout': 'autoHeight',
            'tooltipShowDelay': 200,
        }).classes(f'w-full {theme_cls}').style('height: auto')
        if not rows:
            ui.label('No data matches the search criteria.').classes('opacity-60 mt-2')

    def do_search(e) -> None:
        state['search'] = e.value or ''
        grid_area.refresh()

    def apply_columns(new_visible: set[str]) -> None:
        state['visible'] = new_visible
        grid_area.refresh()

    def do_export(kind: str) -> None:
        cols = current_columns()
        rows = current_rows()
        if kind == 'pdf' and len(rows) > 500:
            rows = rows[:500]
            ui.notify('PDF export capped at 500 rows.', type='warning')
        if kind == 'csv':
            data = export_utils.rows_to_csv_bytes(cols, rows)
            ui.download(data, f'smf-{smf.id}.csv')
        elif kind == 'json':
            data = export_utils.rows_to_json_bytes(cols, rows)
            ui.download(data, f'smf-{smf.id}.json')
        elif kind == 'pdf':
            data = export_utils.rows_to_pdf_bytes(smf.title, smf.description, cols, rows)
            ui.download(data, f'smf-{smf.id}.pdf')
        ui.notify(f'{kind.upper()} export ready ({len(rows)} rows, {len(cols)} columns).', type='positive')

    with ui.row().classes('items-center gap-2 w-full mb-2 flex-wrap'):
        ui.input(placeholder='Search table...', on_change=do_search) \
            .props('dense outlined clearable').classes('w-64')
        ui.button('Columns', icon='view_column',
                   on_click=lambda: open_column_dialog(smf, state['visible'], apply_columns)) \
            .props('outline dense')
        with ui.button_group().props('outline'):
            ui.button('CSV', icon='download', on_click=lambda: do_export('csv')).props('dense')
            ui.button('JSON', icon='data_object', on_click=lambda: do_export('json')).props('dense')
            ui.button('PDF', icon='picture_as_pdf', on_click=lambda: do_export('pdf')).props('dense')
        ui.space()
        count_label['el'] = ui.label('').classes('text-xs opacity-60')

    grid_area()
    return grid_area
