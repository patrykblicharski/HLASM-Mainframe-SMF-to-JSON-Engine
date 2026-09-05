"""FastAPI mock of z/OS Data Gatherer SMF REST Services for local smfexplorer development."""
from __future__ import annotations

import json
import os
import random
import secrets
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from . import datasets as ds
from .generator import RecordGenerator

SPEC_PATH = Path(__file__).parent / "openapi_spec.json"
BASE_PATH = "/zosmf/zosdg/smf"  # mirrors the real z/OSMF-hosted path prefix

MOCK_USER = os.environ.get("MOCK_SMF_USER")
MOCK_PASSWORD = os.environ.get("MOCK_SMF_PASSWORD")

with open(SPEC_PATH, encoding="utf-8") as f:
    OPENAPI_SPEC = json.load(f)

SCHEMAS = OPENAPI_SPEC["components"]["schemas"]
GENERATOR = RecordGenerator(SCHEMAS)


def _resolve_ref(ref: str) -> str:
    return ref.rsplit("/", 1)[-1]


def _discover_type_subtype_schema_map() -> dict:
    """Map (smf_type, smf_subtype) to root OpenAPI schema from /v1/smf/type/... paths."""
    mapping = {}
    for path, methods in OPENAPI_SPEC["paths"].items():
        if not path.startswith("/v1/smf/type/"):
            continue
        get = methods.get("get")
        if not get:
            continue
        parts = path.strip("/").split("/")
        # Path is a template; type/subtype come from the response schema name.
        resp_schema_ref = (
            get.get("responses", {})
            .get("200", {})
            .get("content", {})
            .get("*/*", {})
            .get("schema", {})
        )
        if not resp_schema_ref:
            # some specs use application/json instead of */*
            content = get.get("responses", {}).get("200", {}).get("content", {})
            for c in content.values():
                resp_schema_ref = c.get("schema", {})
                break
        if "$ref" not in resp_schema_ref:
            continue
        indexed_map_schema_name = _resolve_ref(resp_schema_ref["$ref"])
        root_schema = SCHEMAS.get(indexed_map_schema_name, {})
        additional = root_schema.get("additionalProperties", {})
        if "$ref" not in additional:
            continue
        root_schema_name = _resolve_ref(additional["$ref"])

        # root_schema_name follows "SMF<type>_SUBTYPE<subtype>"
        import re

        m = re.match(r"^SMF(\d+)_SUBTYPE(\d+)$", root_schema_name)
        if not m:
            continue
        smf_type, smf_subtype = int(m.group(1)), int(m.group(2))
        mapping[(smf_type, smf_subtype)] = root_schema_name
    return mapping


TYPE_SUBTYPE_TO_SCHEMA = _discover_type_subtype_schema_map()

# Seed record counts per type/subtype so discovery lists look varied.
for _dataset in ds.DATASETS.values():
    for _key in TYPE_SUBTYPE_TO_SCHEMA:
        _dataset.record_counts[_key] = random.randint(50, 5000)


app = FastAPI(title="Mock z/OS Data Gatherer SMF REST Services")
security = HTTPBasic(auto_error=False)


def check_auth(credentials: Optional[HTTPBasicCredentials] = Depends(security)):
    """Basic auth: any credentials unless MOCK_SMF_USER/MOCK_SMF_PASSWORD are set."""
    if MOCK_USER is None:
        return
    if credentials is None or not (
        secrets.compare_digest(credentials.username, MOCK_USER)
        and secrets.compare_digest(credentials.password, MOCK_PASSWORD or "")
    ):
        raise HTTPException(status_code=401, detail="User authentication failed")


def maybe_force_status(_mock_status: Optional[int]):
    if _mock_status is None:
        return
    messages = {
        401: "User authentication failed",
        403: "User has insufficient permissions for request",
        404: "Resource not found",
        429: "Other request for the dataset is currently processed. Try again later.",
        500: "Internal server error",
    }
    raise HTTPException(
        status_code=_mock_status, detail=messages.get(_mock_status, "Forced error")
    )


# --------------------------------------------------------------------------- #
#                                  API docs                                   #
# --------------------------------------------------------------------------- #


@app.get(f"{BASE_PATH}/v3/api-docs")
def api_docs():
    """Serves the real spec verbatim - smfexplorer checks `info.title`
    against it on every `Environment.check()` and uses the schemas to
    build its internal field-name mapping cache.
    """
    return OPENAPI_SPEC


# --------------------------------------------------------------------------- #
#                                  Discovery                                  #
# --------------------------------------------------------------------------- #


@app.get(f"{BASE_PATH}/v1/smf/discover/dataset/exists/{{dataset_name}}")
def dataset_exists(
    dataset_name: str,
    _mock_status: Optional[int] = Query(default=None),
    _: None = Depends(check_auth),
):
    maybe_force_status(_mock_status)
    if ds.get_dataset(dataset_name) is None:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found")
    return Response(status_code=200)


def _build_dataset_description(dataset: ds.FakeDataset) -> dict:
    all_move_times = []
    smf_groups = {}
    for (smf_type, smf_subtype), count in dataset.record_counts.items():
        key = f"{smf_type}-{smf_subtype}"
        earliest_move = f"{dataset.creation_date.isoformat()}T00:00:00.000"
        latest_move = f"{date.today().isoformat()}T23:59:59.000"
        all_move_times.append(earliest_move)
        all_move_times.append(latest_move)
        smf_groups[key] = {
            "estimatedByteSize": count * random.randint(200, 2000),
            "totalNumberOfRecords": count,
            "smfIds": dataset.system_ids,
            "earliestSmfRecordMoveTime": earliest_move,
            "latestSmfRecordMoveTime": latest_move,
            "earliestStartOfSmfInterval": earliest_move,
            "latestStartOfSmfInterval": latest_move,
            "earliestEndOfSmfInterval": earliest_move,
            "latestEndOfSmfInterval": latest_move,
        }

    total_records = sum(dataset.record_counts.values())
    return {
        "datasetCreationDate": dataset.creation_date.isoformat(),
        "discoveryTimestamp": f"{date.today().isoformat()}T00:00:00.000",
        "estimatedByteSize": sum(g["estimatedByteSize"] for g in smf_groups.values()),
        "totalNumberOfRecords": total_records,
        "smfIds": dataset.system_ids,
        "earliestSmfRecordMoveTime": min(all_move_times) if all_move_times else None,
        "latestSmfRecordMoveTime": max(all_move_times) if all_move_times else None,
        "smfGroups": smf_groups,
    }


@app.api_route(
    f"{BASE_PATH}/v1/smf/discover/describe/{{dataset_name}}", methods=["GET", "POST"]
)
def describe_dataset(
    dataset_name: str,
    _mock_status: Optional[int] = Query(default=None),
    _: None = Depends(check_auth),
):
    maybe_force_status(_mock_status)
    dataset = ds.get_dataset(dataset_name)
    if dataset is None:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found")
    return _build_dataset_description(dataset)


# --------------------------------------------------------------------------- #
#                                Data fetching                                #
# --------------------------------------------------------------------------- #


@app.get(f"{BASE_PATH}/v1/smf/type/{{smf_type}}/subtype/{{smf_subtype}}")
def get_smf_data(
    smf_type: int,
    smf_subtype: int,
    request: Request,
    datasetName: str = Query(...),
    systemName: Optional[str] = Query(default=None),
    startTime: Optional[str] = Query(default=None),
    endTime: Optional[str] = Query(default=None),
    showMeta: Optional[bool] = Query(default=None),
    count: int = Query(default=15, ge=0, le=5000, description="Dev-only: how many fake records to generate"),
    _mock_status: Optional[int] = Query(default=None),
    _: None = Depends(check_auth),
):
    maybe_force_status(_mock_status)

    dataset = ds.get_dataset(datasetName)
    if dataset is None:
        raise HTTPException(status_code=404, detail=f"Dataset '{datasetName}' not found")

    schema_name = TYPE_SUBTYPE_TO_SCHEMA.get((smf_type, smf_subtype))
    if schema_name is None:
        raise HTTPException(
            status_code=404,
            detail=f"SMF type {smf_type} subtype {smf_subtype} is not defined in the API",
        )

    # NOTE: No field-selector/time/system filters — smfexplorer ignores extra JSON; full records are simpler.
    base_date = dataset.creation_date

    # NOTE: Do not emit top-level "empty" — spec artifact; smfexplorer would parse it as a record index.
    result = {}
    for i in range(count):
        record = GENERATOR.generate(schema_name, base_date)
        if systemName:
            _apply_system_id(record, systemName.strip())
        result[str(i)] = record

    return result


def _apply_system_id(record: dict, system_name: str) -> None:
    """Set a top-level *SID field to systemName when present (cosmetic filter consistency)."""
    for key in record:
        if key.endswith("SID") and isinstance(record[key], str):
            record[key] = system_name[:4].ljust(4)
            return


@app.get("/")
def index():
    return {
        "service": "Mock z/OS Data Gatherer SMF REST Services",
        "api_docs": f"{BASE_PATH}/v3/api-docs",
        "known_datasets": list(ds.DATASETS.keys()),
        "known_type_subtypes": sorted(TYPE_SUBTYPE_TO_SCHEMA.keys()),
        "hint": "Point smf_webapp's connection URL at http://127.0.0.1:9000" + BASE_PATH,
    }
