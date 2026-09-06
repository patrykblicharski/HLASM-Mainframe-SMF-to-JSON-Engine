"""SMF Analytics web application — ClickHouse-backed peer to Grafana."""

from __future__ import annotations

from flask import Flask

from . import routes


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    routes.register(app)
    return app
