from __future__ import annotations

import os


class Config:
    SECRET_KEY = os.environ.get("SMF_WEB_SECRET", "smf-analytics-dev")
    CLICKHOUSE_URL = os.environ.get("CLICKHOUSE_URL", "http://clickhouse:8123")
    CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "smf")
    CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "blacha123")
    CLICKHOUSE_DATABASE = os.environ.get("CLICKHOUSE_DATABASE", "smf")
    DEFAULT_DAYS = int(os.environ.get("SMF_DEFAULT_DAYS", "4"))
    QUERY_TIMEOUT = float(os.environ.get("SMF_QUERY_TIMEOUT", "60"))
