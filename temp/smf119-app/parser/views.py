"""Summary column specs and extractors for readable record lists."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from .layout import flatten_value

if TYPE_CHECKING:
    from .decode import DecodedRecord


@dataclass(frozen=True)
class ColumnSpec:
    key: str
    label: str
    default: bool = True
    width: int = 100


def _hdr(decoded: DecodedRecord, key: str) -> Any:
    return decoded.header.get(key)


def _ident(decoded: DecodedRecord, key: str) -> Any:
    if not decoded.ident:
        return None
    return decoded.ident.get(key)


def _section_field(decoded: DecodedRecord, section_key: str, field: str) -> Any:
    for sec in decoded.sections:
        if sec.info and sec.info.key == section_key and sec.entries:
            return sec.entries[0].get(field)
    for sec in decoded.sections:
        if sec.triplet.index == 0:
            continue
        if sec.entries and field in sec.entries[0]:
            return sec.entries[0].get(field)
    return None


def _flat(val: Any) -> str:
    return flatten_value(val)


BASE_COLUMNS = [
    ColumnSpec("offset", "Offset", True, 80),
    ColumnSpec("time", "Time", True, 90),
    ColumnSpec("sid", "SID", True, 50),
    ColumnSpec("stack", "Stack", True, 70),
]


def _base_values(decoded: DecodedRecord, file_offset: int) -> dict[str, Any]:
    return {
        "offset": file_offset,
        "time": _hdr(decoded, "SMF119HDTimeFmt") or _hdr(decoded, "SMF119HDTime"),
        "sid": _hdr(decoded, "SMF119HDSID"),
        "stack": _ident(decoded, "SMF119TI_Stack"),
        "sysname": _ident(decoded, "SMF119TI_SYSName"),
        "comp": _ident(decoded, "SMF119TI_Comp"),
        "subtype": decoded.subtype,
        "title": decoded.subtype_title,
        "sections": sum(1 for s in decoded.sections if s.triplet.number),
    }


Extractor = Callable[["DecodedRecord"], Any]

_EXTRA: dict[int, list[tuple[ColumnSpec, Extractor]]] = {}


def _reg(subtype: int, specs: list[tuple[ColumnSpec, Extractor]]) -> None:
    _EXTRA[subtype] = specs


def _sf(section: str, field: str) -> Extractor:
    return lambda d: _section_field(d, section, field)


_reg(
    1,
    [
        (ColumnSpec("resource", "Resource", True, 80), _sf("S1", "SMF119AP_TIRName")),
        (ColumnSpec("lip", "Local IP", True, 110), _sf("S1", "SMF119AP_TILIP")),
        (ColumnSpec("lport", "LPort", True, 55), _sf("S1", "SMF119AP_TILPort")),
        (ColumnSpec("rip", "Remote IP", True, 110), _sf("S1", "SMF119AP_TIRIP")),
        (ColumnSpec("rport", "RPort", True, 55), _sf("S1", "SMF119AP_TIRPort")),
        (ColumnSpec("connid", "ConnID", False, 70), _sf("S1", "SMF119AP_TIConnID")),
    ],
)
_reg(
    2,
    [
        (ColumnSpec("resource", "Resource", True, 80), _sf("S1", "SMF119AP_TTRName")),
        (ColumnSpec("lip", "Local IP", True, 110), _sf("S1", "SMF119AP_TTLIP")),
        (ColumnSpec("lport", "LPort", True, 55), _sf("S1", "SMF119AP_TTLPort")),
        (ColumnSpec("rip", "Remote IP", True, 110), _sf("S1", "SMF119AP_TTRIP")),
        (ColumnSpec("rport", "RPort", True, 55), _sf("S1", "SMF119AP_TTRPort")),
        (ColumnSpec("in_bytes", "In bytes", True, 80), _sf("S1", "SMF119AP_TTInBytes")),
        (ColumnSpec("out_bytes", "Out bytes", True, 80), _sf("S1", "SMF119AP_TTOutBytes")),
        (ColumnSpec("term", "Term code", True, 70), _sf("S1", "SMF119AP_TTTermCode")),
    ],
)
_reg(
    4,
    [
        (ColumnSpec("comp", "Component", True, 70), lambda d: _ident(d, "SMF119TI_Comp")),
        (
            ColumnSpec("change_rsn", "Change reason", True, 90),
            _sf("PICommon", "NMTP_PICOChangeRsn"),
        ),
        (
            ColumnSpec("sec_changed", "Sections changed", True, 140),
            _sf("PICommon", "NMTP_PICOSecChanged"),
        ),
        (ColumnSpec("console", "Console", False, 80), _sf("PICommon", "NMTP_PICOConsName")),
    ],
)
_reg(
    3,
    [
        (ColumnSpec("cmd", "FTP cmd", True, 60), _sf("S1", "SMF119FT_FCCmd")),
        (ColumnSpec("user", "User", True, 70), _sf("S1", "SMF119FT_FCRUser")),
        (ColumnSpec("bytes", "Bytes", True, 80), _sf("S1", "SMF119FT_FCBytes")),
        (ColumnSpec("reply", "Reply", True, 55), _sf("S1", "SMF119FT_FCLReply")),
        (ColumnSpec("lip", "Local IP", True, 110), _sf("S1", "SMF119FT_FCCLIP")),
        (ColumnSpec("rip", "Remote IP", True, 110), _sf("S1", "SMF119FT_FCCRIP")),
        (ColumnSpec("dsn", "DSN", True, 160), _sf("S2", "SMF119FT_FCFileName")),
    ],
)
_reg(
    70,
    [
        (ColumnSpec("oper", "Operation", True, 70), _sf("S1", "SMF119FT_FSOper")),
        (ColumnSpec("user", "User", True, 70), _sf("S1", "SMF119FT_FSSUser")),
        (ColumnSpec("bytes", "Bytes", True, 80), _sf("S1", "SMF119FT_FSBytes")),
        (ColumnSpec("reply", "Reply", True, 55), _sf("S1", "SMF119FT_FSLReply")),
        (ColumnSpec("dsn", "DSN", True, 160), _sf("S3", "SMF119FT_FSFileName1")),
    ],
)
_reg(
    11,
    [
        (ColumnSpec("event", "Event", True, 70), _sf("S1", "SMF119SC_SAEvent_Type")),
        (ColumnSpec("lip", "Local IP", True, 110), _sf("S1", "SMF119SC_SALIP")),
        (ColumnSpec("rip", "Remote IP", True, 110), _sf("S1", "SMF119SC_SARIP")),
        (ColumnSpec("lport", "LPort", True, 55), _sf("S1", "SMF119SC_SALPort")),
        (ColumnSpec("rport", "RPort", True, 55), _sf("S1", "SMF119SC_SARPort")),
    ],
)
_reg(
    20,
    [
        (ColumnSpec("lu", "LU", True, 70), _sf("S1", "SMF119TN_NILU")),
        (ColumnSpec("appl", "Appl", True, 70), _sf("S1", "SMF119TN_NIAppl")),
        (ColumnSpec("lip", "Local IP", True, 110), _sf("S1", "SMF119TN_NILIP")),
        (ColumnSpec("rip", "Remote IP", True, 110), _sf("S1", "SMF119TN_NIRIP")),
    ],
)
_reg(
    21,
    [
        (ColumnSpec("lu", "LU", True, 70), _sf("S1", "SMF119TN_NTLU")),
        (ColumnSpec("appl", "Appl", True, 70), _sf("S1", "SMF119TN_NTAppl")),
        (ColumnSpec("in_bytes", "In bytes", True, 80), _sf("S1", "SMF119TN_NTInByte")),
        (ColumnSpec("out_bytes", "Out bytes", True, 80), _sf("S1", "SMF119TN_NTOutByte")),
    ],
)


def columns_for(subtype: int) -> list[ColumnSpec]:
    extras = [c for c, _ in _EXTRA.get(subtype, [])]
    keys = {c.key for c in BASE_COLUMNS} | {c.key for c in extras}
    out = list(BASE_COLUMNS) + extras
    if "comp" not in keys:
        out.append(ColumnSpec("comp", "Component", False, 70))
    return out


def default_visible_keys(subtype: int) -> set[str]:
    return {c.key for c in columns_for(subtype) if c.default}


def summarize(decoded: DecodedRecord, *, file_offset: int = 0) -> dict[str, Any]:
    row = _base_values(decoded, file_offset)
    for col, extractor in _EXTRA.get(decoded.subtype, []):
        try:
            row[col.key] = _flat(extractor(decoded))
        except Exception:  # noqa: BLE001
            row[col.key] = ""
    if "comp" not in row or row.get("comp") in (None, ""):
        row["comp"] = _flat(_ident(decoded, "SMF119TI_Comp"))
    for k in list(row):
        if k not in ("offset", "subtype", "sections") and not isinstance(
            row[k], (str, int, float, type(None))
        ):
            row[k] = _flat(row[k])
    return row


def register_summary(subtype: int, specs: list[tuple[ColumnSpec, Extractor]]) -> None:
    _EXTRA[subtype] = specs


def has_summary(subtype: int) -> bool:
    return subtype in _EXTRA
