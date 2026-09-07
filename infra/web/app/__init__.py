"""SMF Analytics web application — ClickHouse-backed peer to Grafana."""

from __future__ import annotations

from flask import Flask

from . import routes


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    routes.register(app)

    @app.after_request
    def _no_store_html(response):
        ctype = response.headers.get("Content-Type", "")
        if "text/html" in ctype:
            response.headers["Cache-Control"] = "no-store, max-age=0"
            response.headers["Pragma"] = "no-cache"
        return response

    return app
