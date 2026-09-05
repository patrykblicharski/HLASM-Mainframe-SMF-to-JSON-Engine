#!/usr/bin/env python3
"""SMF Explorer — NiceGUI web app with per-session smfexplorer integration."""
import logging
import sys

from nicegui import ui

from app_core.config import settings
from app_core.console_quit import enable_console_quit
from webui.pages import register_pages

LOG = logging.getLogger(__name__)

if settings.storage_secret == "dev-only-change-me":
    print(
        "WARNING: SMFAPP_STORAGE_SECRET is using the default value. "
        "Set a strong secret via the SMFAPP_STORAGE_SECRET environment variable "
        "before any non-local deployment.",
        file=sys.stderr,
    )

register_pages()

if __name__ in {'__main__', '__mp_main__'}:
    # After NiceGUI prints URLs: Q in the console shuts down the server.
    enable_console_quit()
    ui.run(
        title=settings.app_name,
        host='0.0.0.0',
        port=8080,
        reload=False,
        dark=True,
        favicon='🖥️',
        storage_secret=settings.storage_secret,
        # Default 3s is too short: rendering AG Grid with several thousand rows (e.g. SMF74-4)
        # blocks the browser JS thread briefly, the client loses the websocket (ping/pong),
        # and the server drops the Client instance before the browser can switch —
        # the next handshake with the same client_id gets False and the page reloads
        # (visible as "reloading because handshake failed" in the console).
        reconnect_timeout=15.0,
    )
