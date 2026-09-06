"""Route registration for SMF Analytics."""

from __future__ import annotations

from flask import Flask

from .views import bp


def register(app: Flask) -> None:
    app.register_blueprint(bp)
