"""Decode SMF 119 records via self-defining triplets + layout catalog."""
from __future__ import annotations

import json
import struct
from dataclasses import dataclass, field
from typing import Any

from .catalog import SectionInfo, layout_for_subtype_section, section_for_eye
from .header_layouts import HEADER, IDENT, SDEF_PROLOGUE, TRIPLET
from .layout import StructLayout, decode_repeated, decode_struct, flatten_value, short_label
from .subtypes import title_for
from .views import summarize as summarize_record


@dataclass
class TripletInfo:
    index: int
    offset: int
    length: int
    number: int


@dataclass
class DecodedSection:
    triplet: TripletInfo
    info: SectionInfo | None
    entries: list[dict[str, Any]] = field(default_factory=list)
    raw_hex_preview: str = ""
    note: str = ""


@dataclass
class DecodedRecord:
    header: dict[str, Any]
    subtype: int
    subtype_title: str
    triplet_count: int
    triplets: list[TripletInfo]
    sections: list[DecodedSection]
    ident: dict[str, Any] | None = None


def _format_smf_time(hsec: int) -> str:
    hours = hsec // (100 * 3600)
    minutes = (hsec // (100 * 60)) % 60
    seconds = (hsec // 100) % 60
    hundredths = hsec % 100
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{hundredths:02d}"


def decode_header(record: bytes) -> dict[str, Any]:
    raw = decode_struct(record[: HEADER.size], HEADER)
    tme = raw.get("SMF119HDTime")
    if isinstance(tme, int):
        raw["SMF119HDTimeFmt"] = _format_smf_time(tme)
    return raw


def parse_triplets(record: bytes) -> tuple[int, list[TripletInfo]]:
    if len(record) < 24 + SDEF_PROLOGUE.size:
        return 0, []
    prologue = decode_struct(record[24 : 24 + SDEF_PROLOGUE.size], SDEF_PROLOGUE)
    trn = int(prologue.get("SMF119SD_TRN") or 0)
    triplets: list[TripletInfo] = []
    base = 24 + SDEF_PROLOGUE.size
    for i in range(trn):
        off = base + i * TRIPLET.size
        if off + TRIPLET.size > len(record):
            break
        trip = decode_struct(record[off : off + TRIPLET.size], TRIPLET)
        triplets.append(
            TripletInfo(
                index=i,
                offset=int(trip["Off"]),
                length=int(trip["Len"]),
                number=int(trip["Num"]),
            )
        )
    return trn, triplets


def _resolve_section(subtype: int, trip: TripletInfo, blob: bytes) -> SectionInfo | None:
    info = layout_for_subtype_section(subtype, trip.index, blob=blob, section_len=trip.length)
    if info is not None:
        return info
    if len(blob) >= 4:
        eye = struct.unpack_from(">I", blob, 0)[0]
        return section_for_eye(eye)
    return None


def decode_section_entries(
    record: bytes,
    trip: TripletInfo,
    layout: StructLayout,
) -> list[dict[str, Any]]:
    if trip.offset <= 0 or trip.length <= 0 or trip.number <= 0:
        return []
    start = trip.offset
    end = start + trip.length * trip.number
    if start >= len(record):
        return []
    blob = record[start : min(end, len(record))]
    if layout.variable:
        return decode_repeated(blob, layout, 1, entry_len=len(blob))
    stride = trip.length if trip.length >= max(layout.size, 1) else layout.size
    return decode_repeated(blob, layout, trip.number, entry_len=stride)


def decode_record(record: bytes) -> DecodedRecord:
    header = decode_header(record)
    subtype = int(header.get("SMF119HDSubType") or 0)
    trn, triplets = parse_triplets(record)
    sections: list[DecodedSection] = []
    ident: dict[str, Any] | None = None

    for trip in triplets:
        start = trip.offset
        total = trip.length * trip.number if trip.length and trip.number else 0
        blob = b""
        if start > 0 and total > 0 and start < len(record):
            blob = record[start : min(start + total, len(record))]
        info = _resolve_section(subtype, trip, blob)
        entries: list[dict[str, Any]] = []
        note = ""
        if info is not None and blob:
            layout = info.layout
            if info.chooser:
                layout = info.chooser(blob, trip.length)
            entries = decode_section_entries(record, trip, layout)
            if trip.index == 0 and entries:
                ident = entries[0]
        elif trip.number and trip.length:
            note = "No field map for this section yet — showing raw preview"
        preview = blob[:64].hex() if blob else ""
        sections.append(
            DecodedSection(
                triplet=trip,
                info=info,
                entries=entries,
                raw_hex_preview=preview,
                note=note,
            )
        )

    return DecodedRecord(
        header=header,
        subtype=subtype,
        subtype_title=title_for(subtype),
        triplet_count=trn,
        triplets=triplets,
        sections=sections,
        ident=ident,
    )


def summary_row(decoded: DecodedRecord, *, file_offset: int = 0) -> dict[str, Any]:
    return summarize_record(decoded, file_offset=file_offset)


def section_table_rows(
    section: DecodedSection, *, use_labels: bool = False
) -> tuple[list[str], list[list[str]], list[str]]:
    """Return (headers, rows, ibm_names)."""
    if not section.info or not section.entries:
        return ["raw"], [[section.raw_hex_preview or section.note or ""]], ["raw"]
    layout = section.info.layout
    ibm_names = [f.name for f in layout.fields if not f.reserved]
    if use_labels:
        headers = [short_label(f) for f in layout.fields if not f.reserved]
    else:
        headers = ibm_names
    rows: list[list[str]] = []
    for entry in section.entries:
        rows.append([flatten_value(entry.get(n)) for n in ibm_names])
    return headers, rows, ibm_names


def export_record_full(decoded: DecodedRecord, *, file_offset: int = 0) -> dict[str, Any]:
    """Long-form dict: header + ident + section.field values."""
    out: dict[str, Any] = {
        "_offset": file_offset,
        "_subtype": decoded.subtype,
        "_title": decoded.subtype_title,
        "header": {k: flatten_value(v) for k, v in decoded.header.items() if not str(k).startswith("_")},
    }
    if decoded.ident:
        out["ident"] = {
            k: flatten_value(v) for k, v in decoded.ident.items() if not str(k).startswith("_")
        }
    for sec in decoded.sections:
        if not sec.info or not sec.entries:
            continue
        key = sec.info.key
        if len(sec.entries) == 1:
            out[key] = {
                k: flatten_value(v)
                for k, v in sec.entries[0].items()
                if not str(k).startswith("_")
            }
        else:
            out[key] = [
                {k: flatten_value(v) for k, v in e.items() if not str(k).startswith("_")}
                for e in sec.entries
            ]
    return out


def export_record_flat_rows(decoded: DecodedRecord, *, file_offset: int = 0) -> list[dict[str, Any]]:
    """One row per section entry with section.field columns (for CSV)."""
    base = {
        "file_offset": file_offset,
        "subtype": decoded.subtype,
        "title": decoded.subtype_title,
    }
    rows: list[dict[str, Any]] = []
    for sec in decoded.sections:
        if not sec.info or not sec.entries:
            continue
        for entry in sec.entries:
            row = dict(base)
            row["section"] = sec.info.key
            row["triplet"] = sec.triplet.index
            row["entry_index"] = entry.get("_index", 0)
            for k, v in entry.items():
                if str(k).startswith("_"):
                    continue
                row[f"{sec.info.key}.{k}"] = flatten_value(v)
            rows.append(row)
    return rows


def dump_record_json(decoded: DecodedRecord, *, file_offset: int = 0) -> str:
    return json.dumps(export_record_full(decoded, file_offset=file_offset), indent=2)
