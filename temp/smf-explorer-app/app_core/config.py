"""Pydantic settings; z/OS connection details come from login, not environment."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "SMF Explorer"
    # How long (seconds) an inactive session (connection + Context cache) is
    # kept in memory before reconnecting is required.
    session_ttl_seconds: int = 60 * 60 * 4  # 4h
    # Secret for signing app.storage.user (NiceGUI) — in production set
    # via the SMFAPP_STORAGE_SECRET environment variable.
    storage_secret: str = "dev-only-change-me"

    class Config:
        env_prefix = "SMFAPP_"


settings = Settings()
