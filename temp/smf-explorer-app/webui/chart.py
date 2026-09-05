"""Charts (Apache ECharts via ui.echart) — theme depends on day/night."""
from nicegui import ui

from . import theme
from .theme import PALETTE


def build_option(chart: dict, dark: bool) -> dict:
    """`chart` is a dict {'kind': 'line'|'bar', 'labels': [...], 'series': [{'name','data','dashed'?,'yAxis'?,'yAxisName'?}]}.

    When any series has `yAxis: 1`, the chart gets a second (right) Y axis — useful
    when combined quantities have very different scales (e.g. CPU busy % 0-100 vs.
    event counters in the tens of thousands), otherwise the lower-scale series
    visually flattens to a line near zero.
    """
    text_color = theme.chart_text_color(dark)
    axis_color = theme.chart_axis_color(dark)
    grid_color = theme.chart_grid_color(dark)
    kind = chart.get('kind', 'line')
    dual_axis = any(s.get('yAxis') == 1 for s in chart['series'])

    series = []
    for i, s in enumerate(chart['series']):
        color = PALETTE[i % len(PALETTE)]
        item = {
            'name': s['name'], 'type': 'bar' if kind == 'bar' else 'line',
            'data': s['data'], 'symbol': 'none', 'smooth': True,
            'itemStyle': {'color': color}, 'connectNulls': False,
        }
        if dual_axis:
            item['yAxisIndex'] = s.get('yAxis', 0)
        if kind == 'line':
            item['areaStyle'] = {'opacity': 0.08}
            item['lineStyle'] = {'width': 2}
            if s.get('dashed'):
                item['lineStyle'] = {'width': 2, 'type': 'dashed'}
        series.append(item)

    if dual_axis:
        left_name = next((s.get('yAxisName') for s in chart['series'] if s.get('yAxis', 0) == 0 and s.get('yAxisName')), '')
        right_name = next((s.get('yAxisName') for s in chart['series'] if s.get('yAxis') == 1 and s.get('yAxisName')), '')
        y_axis = [
            {
                'type': 'value', 'name': left_name,
                'axisLabel': {'color': axis_color},
                'splitLine': {'lineStyle': {'color': grid_color}},
            },
            {
                'type': 'value', 'name': right_name,
                'axisLabel': {'color': axis_color},
                'splitLine': {'show': False},
            },
        ]
    else:
        y_axis = {
            'type': 'value',
            'axisLabel': {'color': axis_color},
            'splitLine': {'lineStyle': {'color': grid_color}},
        }

    option = {
        'backgroundColor': 'transparent',
        'textStyle': {'color': text_color},
        'tooltip': {'trigger': 'axis'},
        'legend': {'top': 0, 'textStyle': {'color': text_color}},
        'grid': {'left': 55, 'right': 55 if dual_axis else 25, 'top': 44, 'bottom': 60, 'containLabel': False},
        'xAxis': {
            'type': 'category', 'data': chart['labels'], 'boundaryGap': kind == 'bar',
            'axisLabel': {'color': axis_color, 'rotate': 30, 'fontSize': 10},
            'axisLine': {'lineStyle': {'color': grid_color}},
        },
        'yAxis': y_axis,
        'series': series,
    }
    return option


def render_chart(chart: dict, dark: bool):
    """Renders a new chart element and returns it (for later live updates)."""
    option = build_option(chart, dark)
    return ui.echart(option).classes('w-full').style('height: 360px')


def update_chart(element, chart: dict, dark: bool) -> None:
    """Updates an existing chart element (e.g. after appending a live data point)."""
    element.options.clear()
    element.options.update(build_option(chart, dark))
    element.update()
