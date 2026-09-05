"""Persist visible-column choices per SMF record type / subtype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

DEFAULT_PATH = Path.home() / ".smf2json" / "columns.json"

GroupKey = Tuple[int, Optional[int]]


def config_path() -> Path:
    return DEFAULT_PATH


def load_config(path: Path | None = None) -> Dict[str, List[str]]:
    p = path or DEFAULT_PATH
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    out: Dict[str, List[str]] = {}
    for key, value in data.items():
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            out[str(key)] = list(value)
    return out


def save_config(config: Mapping[str, Sequence[str]], path: Path | None = None) -> Path:
    p = path or DEFAULT_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {str(k): list(v) for k, v in config.items()}
    p.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return p


def _parse_int(raw: Any) -> Optional[int]:
    if raw is None or raw == "":
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def row_group(row: Mapping[str, Any]) -> Optional[GroupKey]:
    rty = _parse_int(row.get("smf_record_type"))
    if rty is None:
        return None
    return (rty, _parse_int(row.get("smf_subtype")))


def group_config_key(rty: int, sty: Optional[int]) -> str:
    return f"{rty}-{sty}" if sty is not None else str(rty)


def group_label(rty: int, sty: Optional[int], count: Optional[int] = None) -> str:
    base = f"SMF {rty}-{sty}" if sty is not None else f"SMF {rty}"
    if count is None:
        return base
    return f"{base}  ({count})"


def present_smf_groups(rows: Iterable[Mapping[str, Any]]) -> List[GroupKey]:
    groups: List[GroupKey] = []
    seen = set()
    for row in rows:
        key = row_group(row)
        if key is None or key in seen:
            continue
        seen.add(key)
        groups.append(key)
    return groups


def present_smf_types(rows: Iterable[Mapping[str, Any]]) -> List[int]:
    types: List[int] = []
    seen = set()
    for rty, _sty in present_smf_groups(rows):
        if rty not in seen:
            seen.add(rty)
            types.append(rty)
    return types


def group_rows(rows: Sequence[Mapping[str, Any]]) -> List[Tuple[GroupKey, List[Dict[str, Any]]]]:
    buckets: Dict[GroupKey, List[Dict[str, Any]]] = {}
    order: List[GroupKey] = []
    for row in rows:
        key = row_group(row)
        if key is None:
            continue
        if key not in buckets:
            buckets[key] = []
            order.append(key)
        buckets[key].append(dict(row))
    return [(key, buckets[key]) for key in order]


def keys_for_type(meta: Mapping[str, Mapping[str, Any]], rty: int) -> set[str]:
    return {key for key, info in meta.items() if rty in info.get("types", [])}


def visible_for_group(
    available: Sequence[str],
    rty: int,
    sty: Optional[int],
    config: Mapping[str, Sequence[str]],
) -> List[str]:
    saved = config.get(group_config_key(rty, sty))
    if saved is None and sty is not None:
        saved = config.get(str(rty))
    if saved is None:
        return list(available)
    wanted = set(saved)
    return [key for key in available if key in wanted]


def visible_columns(
    available: Sequence[str],
    types: Sequence[int],
    config: Mapping[str, Sequence[str]],
    meta: Mapping[str, Mapping[str, Any]],
) -> List[str]:
    """Intersect saved per-type choices with columns present in the dump."""
    if not available:
        return []
    if not types or not any(str(t) in config for t in types):
        return list(available)

    wanted: set[str] = set()
    for rty in types:
        saved = config.get(str(rty))
        if saved is None:
            wanted.update(k for k in available if rty in meta.get(k, {}).get("types", ()))
            wanted.update(k for k in available if k not in meta)
        else:
            wanted.update(saved)
    return [key for key in available if key in wanted]


def store_group_selection(
    config: Dict[str, List[str]],
    rty: int,
    sty: Optional[int],
    selected: Sequence[str],
) -> Dict[str, List[str]]:
    config[group_config_key(rty, sty)] = list(selected)
    return config


def store_selection(
    config: Dict[str, List[str]],
    types: Sequence[int],
    selected: Sequence[str],
    meta: Mapping[str, Mapping[str, Any]],
) -> Dict[str, List[str]]:
    selected_list = list(selected)
    for rty in types:
        type_keys = keys_for_type(meta, rty)
        config[str(rty)] = [key for key in selected_list if key in type_keys]
    return config
