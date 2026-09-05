"""Shared visual theme (day/night) + CSS styles injected once per page."""
from nicegui import ui

PALETTE = ['#4fd1c5', '#f6ad55', '#fc8181', '#63b3ed', '#b794f4', '#68d391']

_CSS = """
.kpi-card { min-width: 168px; border-radius: 12px; }
.kpi-value { font-size: 1.35rem; line-height: 1.6rem; }
.smf-badge { font-size: 11px; font-weight: 700; letter-spacing: .02em; }
.cross-badge { background: #4fd1c5 !important; color: #0f1420 !important; }
.menu-cat-title {
  font-size: 11px; text-transform: uppercase; letter-spacing: .06em;
  opacity: .55; padding: 10px 14px 2px;
}
.menu-item { border-left: 3px solid transparent; cursor: pointer; }
.menu-item.active { border-left-color: #4fd1c5; }
.menu-item:hover { background: rgba(127,127,127,0.08); }
.row-bad { background-color: rgba(252, 129, 129, 0.16) !important; }
.row-warn { background-color: rgba(246, 173, 85, 0.16) !important; }
.smf-desc { opacity: .7; max-width: 900px; line-height: 1.5; }
.overview-btn {
  background: linear-gradient(135deg, rgba(79,209,197,0.20), rgba(99,179,237,0.10));
  border: 1px solid rgba(79,209,197,0.4);
}
.live-dot {
  width: 9px; height: 9px; border-radius: 50%; background: #68d391;
  box-shadow: 0 0 0 0 rgba(104,211,145,.7); animation: live-pulse 1.6s infinite;
}
@keyframes live-pulse {
  0% { box-shadow: 0 0 0 0 rgba(104,211,145,.6); }
  70% { box-shadow: 0 0 0 8px rgba(104,211,145,0); }
  100% { box-shadow: 0 0 0 0 rgba(104,211,145,0); }
}
"""


def install() -> None:
    """Injects global CSS. Call once per page (at the start of the layout)."""
    ui.add_css(_CSS)


def chart_text_color(dark: bool) -> str:
    return '#e2e8f0' if dark else '#1a202c'


def chart_axis_color(dark: bool) -> str:
    return '#93a1c2' if dark else '#4a5568'


def chart_grid_color(dark: bool) -> str:
    return '#2a3550' if dark else '#e2e8f0'
