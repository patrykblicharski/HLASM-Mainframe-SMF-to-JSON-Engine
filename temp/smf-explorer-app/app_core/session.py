"""Only module that imports smfexplorer; one Environment per browser session."""
from __future__ import annotations

import importlib
import logging
import time
import uuid
from dataclasses import dataclass, field as dc_field
import threading
from typing import Dict, List, Optional, Tuple

import pandas as pd

import smfexplorer
from smfexplorer import error as smf_error
from smfexplorer.core.environment import Environment
from smfexplorer.core.field import Field

from app_core.config import settings

LOG = logging.getLogger(__name__)

AvailableKey = Tuple[int, int]


class SmfAppError(Exception):
    """Base error for this layer."""


class ConnectionFailed(SmfAppError):
    pass


class UnknownRecord(SmfAppError):
    pass


class UnknownField(SmfAppError):
    pass


@dataclass
class Session:
    session_id: str
    environment: Environment
    dataset_name: Optional[str] = None
    created_at: float = dc_field(default_factory=time.time)
    last_used_at: float = dc_field(default_factory=time.time)
    # dataset_name -> cached Context (Context caches discovery itself)
    contexts: Dict[str, object] = dc_field(default_factory=dict)
    # (type, subtype) -> record count from get_available_records(); empty until refresh
    available: Dict[AvailableKey, int] = dc_field(default_factory=dict)
    # Optional system filter applied to queries (UI / Phase 5)
    system_name: Optional[str] = None
    # Row limit for queries (UI / Phase 5); default matches historical hardcode
    query_limit: int = 5000

    def touch(self) -> None:
        self.last_used_at = time.time()

    def has_type(self, smf_type: int, subtype: int) -> bool:
        return (smf_type, subtype) in self.available

    def has_types(self, required: set[AvailableKey]) -> bool:
        return required.issubset(self.available.keys())


class SessionStore:
    """In-process session store; multi-worker needs sticky sessions (Environment not serializable)."""

    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.RLock()

    def create(self, connection_string: str, dataset_name: str) -> Session:
        try:
            environment = smfexplorer.new_environment(connection_string)
        except smf_error.SmfExplorerError as exc:
            raise ConnectionFailed(str(exc)) from exc
        except Exception as exc:  # requests.exceptions.* etc.
            raise ConnectionFailed(f"Connection failed: {exc}") from exc

        session_id = uuid.uuid4().hex
        session = Session(session_id=session_id, environment=environment, dataset_name=dataset_name)
        with self._lock:
            self._sessions[session_id] = session
        return session

    def get(self, session_id: Optional[str]) -> Optional[Session]:
        if not session_id:
            return None
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            if time.time() - session.last_used_at > settings.session_ttl_seconds:
                del self._sessions[session_id]
                return None
            session.touch()
            return session

    def drop(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)


SESSIONS = SessionStore()


# --------------------------------------------------------------------------- #
#                       SMF record / field catalog                            #
# --------------------------------------------------------------------------- #

KNOWN_RECORD_MODULES: List[str] = [
    "SMF30S1", "SMF30S2", "SMF30S3", "SMF30S4", "SMF30S5", "SMF30S6",
    "SMF70S1", "SMF70S2",
    "SMF71S1",
    "SMF72S3", "SMF72S4", "SMF72S5",
    "SMF73S1",
    "SMF74S1", "SMF74S2", "SMF74S3", "SMF74S4", "SMF74S5",
    "SMF74S6", "SMF74S7", "SMF74S8", "SMF74S9", "SMF74S10",
    "SMF75S1",
    "SMF76S1",
    "SMF77S1",
    "SMF78S2", "SMF78S3",
    "SMF79S1", "SMF79S2", "SMF79S3", "SMF79S4", "SMF79S5", "SMF79S6",
    "SMF79S7", "SMF79S9", "SMF79S11", "SMF79S12", "SMF79S14", "SMF79S15",
    "SMF99S1", "SMF99S2", "SMF99S6", "SMF99S12", "SMF99S14",
    "SMF113S1", "SMF113S2",
]


def _load_record_module(record_name: str):
    if record_name not in KNOWN_RECORD_MODULES:
        raise UnknownRecord(f"Unknown SMF record module '{record_name}'")
    try:
        return importlib.import_module(f"smfexplorer.fields.{record_name}")
    except ImportError as exc:
        raise UnknownRecord(f"Failed to load record module '{record_name}'") from exc


def list_fields(record_name: str) -> List[dict]:
    """Returns metadata for each field (Field) in the record module.

    Each entry: {name, description, type, virtual}
    """
    module = _load_record_module(record_name)
    out = []
    for attr_name in dir(module):
        if attr_name.startswith("_"):
            continue
        attr = getattr(module, attr_name)
        if isinstance(attr, Field):
            out.append(
                {
                    "name": attr.name,
                    "description": (attr.__doc__ or "").split("\n")[0].strip(),
                    "type": attr.type.name if attr.type else "UNDEFINED",
                    "virtual": bool(attr.virtual),
                }
            )
    out.sort(key=lambda f: f["name"])
    return out


def resolve_fields(record_name: str, field_names: List[str]) -> List[Field]:
    module = _load_record_module(record_name)
    resolved = []
    for name in field_names:
        attr = getattr(module, name, None)
        if not isinstance(attr, Field):
            raise UnknownField(f"Field '{name}' does not exist in record '{record_name}'")
        resolved.append(attr)
    return resolved


def known_field_names(record_name: str, field_names: List[str]) -> List[str]:
    """Filter `field_names` to those that exist as Field on the record module."""
    module = _load_record_module(record_name)
    return [n for n in field_names if isinstance(getattr(module, n, None), Field)]


# --------------------------------------------------------------------------- #
#                              Query execution                                #
# --------------------------------------------------------------------------- #


def get_or_create_context(session: Session, dataset_name: str):
    ctx = session.contexts.get(dataset_name)
    if ctx is None:
        ctx = session.environment.new_context(dataset_name)
        session.contexts[dataset_name] = ctx
    return ctx


def _json_safe(v):
    """Serialize pd.Timestamp/Timedelta as str — orjson rejects them and breaks the page."""
    if isinstance(v, (pd.Timestamp, pd.Timedelta)):
        return str(v)
    return v


def dataframe_to_records(df: pd.DataFrame) -> list[dict]:
    """Converts the DataFrame returned by smfexplorer to `list[dict]` —
    exactly the format consumed by `webui/data_table.py`.

    NaT/NaN/pd.NA are replaced with None so AG Grid / export do not choke
    on non-numeric values in JS/JSON.
    """
    safe_df = df.astype(object).where(pd.notnull(df), None)
    for col in safe_df.columns:
        safe_df[col] = safe_df[col].map(_json_safe)
    return safe_df.to_dict(orient="records")
