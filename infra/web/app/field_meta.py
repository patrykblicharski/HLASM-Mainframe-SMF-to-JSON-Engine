"""Human-readable descriptions for SMF / UI columns (table tips + details modal)."""

from __future__ import annotations

from typing import Any

# Keys are lowercase; lookup is case-insensitive.
FIELD_DESCRIPTIONS: dict[str, str] = {
    # Common / UI
    "timestamp": "Latest event time in the selected window for this row.",
    "last_ts": "Latest event timestamp for the aggregated row.",
    "event_date": "SMF event date (YYYY-MM-DD).",
    "time": "SMF event time of day (HH:MM:SS).",
    "date": "Alternate date field when present on the record.",
    "rows": "Number of matching SMF records in the selected window.",
    "ends": "Count of job-end (SMF 30-5) records.",
    "excp": "Sum of EXCP (I/O) counts from dataset open/close records.",
    "direction": "I/O direction: INPUT (SMF 14) or OUTPUT (SMF 15).",
    "dir": "I/O direction: INPUT (SMF 14) or OUTPUT (SMF 15).",
    "job": "z/OS job name.",
    "job_name": "z/OS job name from the SMF record.",
    "dataset": "Dataset name (DSN).",
    "dsname": "Dataset name (DSN). Blank/control JFCB names may be empty.",
    "dsname_display": "Display label for the dataset (safe fallback when DSN is blank).",
    "vol": "Volume serial (VOLSER).",
    "volser": "Volume serial number associated with the dataset.",
    "volser_1": "First volume serial from SMF 14/15.",
    "volume_serial": "Volume serial from SMF 17 scratch records.",
    "sid": "SMF system identifier (SID).",
    "smf_system_id": "SMF system identifier (SID) of the recording system.",
    "programs (top)": "Most frequent program names from SMF 30-4 step ends.",
    "steps (top)": "Most frequent step names from SMF 30-4 step ends.",
    "cpu (timer units)": "Sum of CPU step timer units from SMF 30-4 (not wall seconds).",
    "cpu_sum": "Sum of CPU step timer units from SMF 30-4.",
    "programs": "Program name(s) from job step records.",
    "steps": "Step name(s) from job step records.",
    "program_name": "Program name executed in the job step (SMF 30-4).",
    "step_name": "Job step name (SMF 30-4).",
    "job_class": "JES job class.",
    "ddname": "DD name used for the dataset allocation.",
    "dd": "DD name used for the dataset allocation.",
    "cc": "Completion code.",
    # Lifecycle / catalog
    "action": "Catalog action: DEFINE (61), DELETE (65), or ALTER (66).",
    "entry": "Catalog entry name (dataset / object name).",
    "entry_name": "Catalog entry name from SMF 61/65/66.",
    "catalog": "ICF catalog name.",
    "catalog_name": "ICF catalog name from SMF 61/65/66.",
    # RACF / security
    "user": "RACF user ID.",
    "user_id": "RACF user ID associated with the event.",
    "racf_user": "RACF user ID from job accounting / identity fields.",
    "evt": "RACF event code (SMF 80).",
    "event_code": "RACF event code (SMF 80).",
    "class": "RACF resource class name.",
    "class_name": "RACF resource class (e.g. DATASET, FACILITY).",
    "resource": "RACF resource name checked.",
    "old_resource": "RACF resource name (often dataset or profile name).",
    "resource_name": "Resource / workload name from the SMF record.",
    "req": "Access level requested.",
    "access_requested": "RACF access level requested.",
    "allow": "Access level allowed.",
    "access_allowed": "RACF access level allowed.",
    "events": "Count of RACF (SMF 80) events.",
    "racf_events": "Count of related RACF events for this job.",
    # TCP / network
    "ip": "Remote IP address.",
    "remote_ip": "Remote (partner) IP address.",
    "local_ip": "Local IP address on the TCP stack.",
    "local_port": "Local TCP port number.",
    "remote_port": "Remote TCP port number.",
    "port": "Local TCP port number.",
    "conns": "Connection count in the selected window.",
    "in": "Inbound byte count.",
    "out": "Outbound byte count.",
    "in_bytes": "Bytes received (inbound).",
    "out_bytes": "Bytes sent (outbound).",
    "stack": "TCP/IP stack name.",
    "tcp_stack": "z/OS TCP/IP stack name.",
    "term_code": "TCP connection termination code.",
    "connection_id": "TCP connection identifier.",
    "as_name": "Address space name associated with the connection.",
    "workload": "Workload / resource name tied to network activity.",
    "local_user": "Local user identity on the TCP connection.",
    # Job / identity extras
    "cpu": "CPU usage measure for the row.",
    "cpu_step_time": "CPU time consumed by the step (SMF timer units).",
    "step_comp_code": "Step completion code.",
    "excp_count": "EXCP (Execute Channel Program) I/O count for the dataset.",
    "smfid": "SMF system identifier.",
    "sysplex_name": "Sysplex name when present.",
    "product_name": "Product or subsystem name.",
    "subtype": "SMF record subtype.",
    "record_type": "SMF record type number.",
}


def field_description(name: Any, default: str = "") -> str:
    """Return a tip for a column/field name (case-insensitive)."""
    if name is None:
        return default
    key = str(name).strip()
    if not key:
        return default
    return FIELD_DESCRIPTIONS.get(key.lower(), default) or FIELD_DESCRIPTIONS.get(
        key.lower().replace(" ", "_"), default
    )


def field_meta_json() -> dict[str, str]:
    """Map suitable for embedding in the browser (lowercase keys)."""
    return dict(FIELD_DESCRIPTIONS)
