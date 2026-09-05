#!/usr/bin/env python3
"""Generate non-Gatherer maps (42/14/15/119) and deepen handcrafted 30/70.1/72.3."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
CAT42 = ROOT / "catalog" / "smf42"
PAC119 = ROOT / "temp" / "smf119-app" / "tools" / "pacsys_json"


def write_asm(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def field_line(off: str, typ: str, js: str, triplet: str | None = None) -> str:
    if triplet:
        return (
            f"         SMF_FIELD {off},TRIPLET={triplet},        X\n"
            f"               TYPE={typ},JSON={js}\n"
        )
    return f"         SMF_FIELD {off},TYPE={typ},JSON={js}\n"


def json_key(name: str, used: set[str], hints: dict[str, str] | None = None) -> str:
    hints = hints or {}
    if name in hints:
        key = hints[name]
    else:
        tail = re.sub(r"^(SMF\d+|S42|R\d+|SMF119[A-Z0-9_]*_)", "", name)
        tail = re.sub(r"[^A-Za-z0-9]", "", tail) or name
        key = tail.lower()[:16]
        if not re.match(r"^[a-z]", key):
            key = ("f" + key)[:16]
    base = key[:16]
    if base not in used:
        used.add(base)
        return base
    n = 2
    while True:
        suf = str(n)
        cand = (base[: 16 - len(suf)] + suf)[:16]
        if cand not in used:
            used.add(cand)
            return cand
        n += 1


# ---------------------------------------------------------------------------
# MAP30 / MAP70S1 / MAP72S3 deepen
# ---------------------------------------------------------------------------

MAP30_EXTRA = [
    # product
    ("SMF30OSL-SMF30PSS", "T_CHR8", "os_level", "SMF30SOF-SMF30LEN"),
    ("SMF30SYN-SMF30PSS", "T_CHR8", "sys_name", "SMF30SOF-SMF30LEN"),
    ("SMF30SYP-SMF30PSS", "T_CHR8", "sysplex_name", "SMF30SOF-SMF30LEN"),
    # identification
    ("SMF30STN-SMF30JBN", "T_DEC2", "step_number", "SMF30IOF-SMF30LEN"),
    ("SMF30CLS-SMF30JBN", "T_CHR1", "job_class", "SMF30IOF-SMF30LEN"),
    ("SMF30CL8-SMF30JBN", "T_CHR8", "job_class8", "SMF30IOF-SMF30LEN"),
    ("SMF30JPT-SMF30JBN", "T_DEC2", "jes_priority", "SMF30IOF-SMF30LEN"),
    ("SMF30RST-SMF30JBN", "T_TME", "reader_start_t", "SMF30IOF-SMF30LEN"),
    ("SMF30RSD-SMF30JBN", "T_DTE", "reader_start_d", "SMF30IOF-SMF30LEN"),
    ("SMF30SIT-SMF30JBN", "T_TME", "step_init_t", "SMF30IOF-SMF30LEN"),
    ("SMF30STD-SMF30JBN", "T_DTE", "step_init_d", "SMF30IOF-SMF30LEN"),
    ("SMF30GRP-SMF30JBN", "T_CHR8", "racf_group", "SMF30IOF-SMF30LEN"),
    ("SMF30RUD-SMF30JBN", "T_CHR8", "racf_user", "SMF30IOF-SMF30LEN"),
    ("SMF30ASI-SMF30JBN", "T_DEC2", "asid", "SMF30IOF-SMF30LEN"),
    # processor
    ("SMF30ICU-SMF30PTY", "T_DEC4", "init_tcb_time", "SMF30COF-SMF30LEN"),
    ("SMF30ISB-SMF30PTY", "T_DEC4", "init_srb_time", "SMF30COF-SMF30LEN"),
    ("SMF30IST-SMF30PTY", "T_DEC4", "interval_start", "SMF30COF-SMF30LEN"),
    ("SMF30IDT-SMF30PTY", "T_DTE", "interval_date", "SMF30COF-SMF30LEN"),
    ("SMF30CSC-SMF30PTY", "T_DEC4", "crypto_count", "SMF30COF-SMF30LEN"),
]


def write_map30cmn() -> None:
    lines = [
        "* Shared SMF type-30 field list (copied into TABLE30 / TABLE30_n)",
        "         SMF_FIELD SMF30RTY-SMF30LEN,TYPE=T_DEC1,JSON=smf_record_type",
        "",
        "         SMF_FIELD SMF30SID-SMF30LEN,TYPE=T_CHR4,JSON=smf_system_id",
        "",
        "         SMF_FIELD SMF30TME-SMF30LEN,TYPE=T_TME,JSON=time",
        "",
        "         SMF_FIELD SMF30DTE-SMF30LEN,TYPE=T_DTE,JSON=date",
        "",
        "         SMF_FIELD SMF30WID-SMF30LEN,TYPE=T_CHR4,JSON=work_class_id",
        "",
        "         SMF_FIELD SMF30STP-SMF30LEN,TYPE=T_DEC2,JSON=subtype",
        "",
        "         SMF_FIELD SMF30RVN-SMF30PSS,TRIPLET=SMF30SOF-SMF30LEN,        X",
        "               TYPE=T_CHR2,JSON=rec_version",
        "",
        "         SMF_FIELD SMF30PNM-SMF30PSS,TRIPLET=SMF30SOF-SMF30LEN,        X",
        "               TYPE=T_CHR8,JSON=addr_space_ind",
        "",
    ]
    for off, typ, js, trip in MAP30_EXTRA[:3]:
        lines.append(field_line(off, typ, js, trip).rstrip("\n"))
        lines.append("")
    lines += [
        "         SMF_FIELD SMF30JBN-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X",
        "               TYPE=T_CHR8,JSON=job_name",
        "",
        "         SMF_FIELD SMF30PGM-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X",
        "               TYPE=T_CHR8,JSON=program_name",
        "",
        "         SMF_FIELD SMF30STM-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X",
        "               TYPE=T_CHR8,JSON=step_name",
        "",
        "         SMF_FIELD SMF30JNM-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X",
        "               TYPE=T_CHR8,JSON=jes_job_num",
        "",
        "         SMF_FIELD SMF30USR-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X",
        "               TYPE=T_CHR20,JSON=user_name",
        "",
    ]
    for off, typ, js, trip in MAP30_EXTRA[3:14]:
        lines.append(field_line(off, typ, js, trip).rstrip("\n"))
        lines.append("")
    lines += [
        "         SMF_FIELD SMF30CPT-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X",
        "               TYPE=T_DEC4,JSON=cpu_step_time",
        "",
        "         SMF_FIELD SMF30CPS-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X",
        "               TYPE=T_DEC4,JSON=srb_time",
        "",
    ]
    for off, typ, js, trip in MAP30_EXTRA[14:]:
        lines.append(field_line(off, typ, js, trip).rstrip("\n"))
        lines.append("")
    lines += [
        "         SMF_FIELD SMF30SCC-SMF30SCC,TRIPLET=SMF30TOF-SMF30LEN,        X",
        "               TYPE=T_HEX2,JSON=step_comp_code",
        "",
        "         SMF_FIELD SMF30ARC-SMF30SCC,TRIPLET=SMF30TOF-SMF30LEN,        X",
        "               TYPE=T_DEC4,JSON=abend_reason",
        "",
    ]
    (SRC / "MAP30CMN.asm").write_text("\n".join(lines), encoding="utf-8")


def write_map70s1() -> None:
    hints = {
        "SMF70PRD": "product_name",
        "SMF70MVS": "mvs_level",
        "SMF70LPM": "lpar_name",
        "SMF70CID": "cpu_id",
        "SMF70TYP": "cpu_type",
        "SMF70SNM": "system_name",
        "SMF70XNM": "sysplex_name",
        "SMF70SAM": "sample_count",
        "SMF70MOD": "cpu_family",
        "SMF70BNP": "phys_cpu_count",
        "SMF70IFA": "zaap_online",
        "SMF70SUP": "ziip_online",
        "SMF70LPN": "lpar_number",
        "SMF70MSU": "defined_msu",
    }
    used: set[str] = set()
    lines = [
        "* ====================================================================",
        "* SMF TYPE 70 SUBTYPE 1 — CPU, PR/SM, and ICF activity",
        "* ====================================================================",
        "TABLE70_1 SMF_START",
        "",
        field_line("SMF70RTY-SMF70LEN", "T_DEC1", "smf_record_type").rstrip("\n"),
        "",
        field_line("SMF70SID-SMF70LEN", "T_CHR4", "smf_system_id").rstrip("\n"),
        "",
        field_line("SMF70TME-SMF70LEN", "T_TME", "time").rstrip("\n"),
        "",
        field_line("SMF70DTE-SMF70LEN", "T_DTE", "date").rstrip("\n"),
        "",
        field_line("SMF70SSI-SMF70LEN", "T_CHR4", "subsystem_id").rstrip("\n"),
        "",
        field_line("SMF70STY-SMF70LEN", "T_DEC2", "subtype").rstrip("\n"),
        "",
        "* --- product ---",
    ]
    used.update(
        {
            "smf_record_type",
            "smf_system_id",
            "time",
            "date",
            "subsystem_id",
            "subtype",
        }
    )
    for ibm, typ in [
        ("SMF70PRD", "T_CHR8"),
        ("SMF70DAT", "T_DTE"),
        ("SMF70SAM", "T_DEC4"),
        ("SMF70MVS", "T_CHR8"),
        ("SMF70SRL", "T_DEC1"),
        ("SMF70XNM", "T_CHR8"),
        ("SMF70SNM", "T_CHR8"),
    ]:
        js = json_key(ibm, used, hints)
        lines.append(field_line(f"{ibm}-SMF70MFV", typ, js, "SMF70PRS-SMF70LEN").rstrip("\n"))
        lines.append("")
    lines.append("* --- CPU control ---")
    for ibm, typ in [
        ("SMF70MOD", "T_HEX2"),
        ("SMF70VER", "T_DEC1"),
        ("SMF70BNP", "T_DEC1"),
        ("SMF70IFA", "T_DEC2"),
        ("SMF70SUP", "T_DEC2"),
        ("SMF70WLA", "T_DEC4"),
        ("SMF70LAC", "T_DEC4"),
        ("SMF70POM", "T_CHR4"),
    ]:
        js = json_key(ibm, used, hints)
        lines.append(field_line(f"{ibm}-SMF70MOD", typ, js, "SMF70CCS-SMF70LEN").rstrip("\n"))
        lines.append("")
    lines.append("* --- CPU data ---")
    for ibm, typ in [
        ("SMF70CID", "T_DEC2"),
        ("SMF70TYP", "T_DEC1"),
        ("SMF70SLH", "T_DEC4"),
        ("SMF70TPI", "T_DEC4"),
    ]:
        js = json_key(ibm, used, hints)
        lines.append(field_line(f"{ibm}-SMF70WAT", typ, js, "SMF70CPS-SMF70LEN").rstrip("\n"))
        lines.append("")
    lines.append("* --- PR/SM partition ---")
    for ibm, typ in [
        ("SMF70LPM", "T_CHR8"),
        ("SMF70LPN", "T_DEC1"),
        ("SMF70BDN", "T_DEC2"),
        ("SMF70MSU", "T_DEC4"),
        ("SMF70CSF", "T_DEC4"),
        ("SMF70SPN", "T_CHR8"),
        ("SMF70STN", "T_CHR8"),
        ("SMF70GNM", "T_CHR8"),
    ]:
        js = json_key(ibm, used, hints)
        lines.append(field_line(f"{ibm}-SMF70LPM", typ, js, "SMF70BCS-SMF70LEN").rstrip("\n"))
        lines.append("")
    lines.append("         SMF_END")
    lines.append("")
    (SRC / "MAP70S1.asm").write_text("\n".join(lines), encoding="utf-8")


def write_map72s3() -> None:
    hints = {
        "R723MCNM": "class_name",
        "R723MCPG": "period_count",
        "R723CPER": "period_number",
        "R723CCDE": "cpu_delay",
        "R723MNSP": "policy_name",
        "R723MWNM": "workload_name",
        "R723MIDN": "serv_def_name",
        "SMF72PRD": "product_name",
        "SMF72MVS": "mvs_level",
        "SMF72SNM": "system_name",
        "SMF72XNM": "sysplex_name",
        "R723CRCP": "tran_complete",
        "R723CCUS": "cpu_using",
        "R723CIMP": "importance",
        "R723CVAL": "goal_value",
        "R723GGNM": "res_group_name",
    }
    used: set[str] = set()
    lines = [
        "* ====================================================================",
        "* SMF TYPE 72 SUBTYPE 3 — Workload activity (WLM)",
        "* ====================================================================",
        "TABLE72_3 SMF_START",
        "",
        field_line("SMF72RTY-SMF72LEN", "T_DEC1", "smf_record_type").rstrip("\n"),
        "",
        field_line("SMF72SID-SMF72LEN", "T_CHR4", "smf_system_id").rstrip("\n"),
        "",
        field_line("SMF72TME-SMF72LEN", "T_TME", "time").rstrip("\n"),
        "",
        field_line("SMF72DTE-SMF72LEN", "T_DTE", "date").rstrip("\n"),
        "",
        field_line("SMF72SSI-SMF72LEN", "T_CHR4", "subsystem_id").rstrip("\n"),
        "",
        field_line("SMF72STY-SMF72LEN", "T_DEC2", "subtype").rstrip("\n"),
        "",
        "* --- product ---",
    ]
    used.update(
        {"smf_record_type", "smf_system_id", "time", "date", "subsystem_id", "subtype"}
    )
    for ibm, typ in [
        ("SMF72PRD", "T_CHR8"),
        ("SMF72DAT", "T_DTE"),
        ("SMF72SAM", "T_DEC4"),
        ("SMF72MVS", "T_CHR8"),
        ("SMF72XNM", "T_CHR8"),
        ("SMF72SNM", "T_CHR8"),
    ]:
        js = json_key(ibm, used, hints)
        lines.append(field_line(f"{ibm}-SMF72MFV", typ, js, "SMF72PRS-SMF72LEN").rstrip("\n"))
        lines.append("")
    lines.append("* --- WLM control ---")
    for ibm, typ in [
        ("R723MNSP", "T_CHR8"),
        ("R723MWNM", "T_CHR8"),
        ("R723MCNM", "T_CHR8"),
        ("R723MCPG", "T_DEC2"),
        ("R723MIDN", "T_CHR8"),
        ("R723MIDU", "T_CHR8"),
        ("R723MOPT", "T_CHR2"),
        ("R723MTVL", "T_DEC4"),
    ]:
        js = json_key(ibm, used, hints)
        lines.append(field_line(f"{ibm}-R723MSCF", typ, js, "SMF72WMS-SMF72LEN").rstrip("\n"))
        lines.append("")
    lines.append("* --- service/report class period ---")
    for ibm, typ in [
        ("R723CPER", "T_DEC1"),
        ("R723CVAL", "T_DEC4"),
        ("R723CPCT", "T_DEC2"),
        ("R723CIMP", "T_DEC2"),
        ("R723CRCP", "T_DEC4"),
        ("R723CARC", "T_DEC4"),
        ("R723CCUS", "T_DEC4"),
        ("R723CSWC", "T_DEC4"),
        ("R723CCDE", "T_DEC4"),
    ]:
        js = json_key(ibm, used, hints)
        lines.append(field_line(f"{ibm}-R723CRTX", typ, js, "SMF72SCS-SMF72LEN").rstrip("\n"))
        lines.append("")
    lines.append("* --- resource group ---")
    for ibm, typ in [
        ("R723GGNM", "T_CHR8"),
        ("R723GGMN", "T_DEC4"),
        ("R723GGMX", "T_DEC4"),
    ]:
        js = json_key(ibm, used, hints)
        lines.append(field_line(f"{ibm}-R723GGNM", typ, js, "SMF72RGS-SMF72LEN").rstrip("\n"))
        lines.append("")
    lines.append("         SMF_END")
    lines.append("")
    (SRC / "MAP72S3.asm").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# SMF 42 from catalog
# ---------------------------------------------------------------------------

SECTION_TRIPLET = [
    (r"Header/Self-defining", None),  # header fields, no triplet
    (r"Job header", "SMF42JHO"),
    (r"BMF totals", "SMF42BMO"),
    (r"Storage class summary", "SMF42SCO"),
    (r"Control unit cache", "SMF42CUO"),
    (r"^Volume section|SMS-managed volume", "SMF42VLO"),
    (r"Event audit", "SMF42EAO"),
    (r"CC statistics|Concurrent copy", "SMF42CCO"),
    (r"EXT statistics", "SMF42EXO"),
    (r"Storage class response time", "SMF42SRO"),
    (r"Volume header", "SMF42VHO"),
    (r"X37 abend|Abend data", "SMF42ABO"),
    (r"SMS data section", "SMF42SMO"),
    (r"Volume selection failure", "SMF42VSF"),
    (r"XRC", "SMF42XRO"),
    (r"ADSM", "SMF42T14"),
    (r"STOW Initialize(?! additional)", "SMF42KN1"),
    (r"Member Delete(?! additional| Alias)", "SMF42LN1"),
    (r"DFSMSrmm audit", "SMF42AUD"),
    (r"DFSMSrmm security|security records section", "SMF42SEC"),
    (r"Member add/replace header", "SMF42PN1"),
    (r"Member rename(?! additional| old)", "SMF42QN1"),
    (r"VTOC update header", "SMF4227R1"),
]


def match_42_triplet(section: str) -> str | None:
    for pat, trip in SECTION_TRIPLET:
        if trip is None:
            if re.search(pat, section, re.I):
                return None  # header
            continue
        if re.search(pat, section, re.I):
            return trip
    return False  # no match / skip nested


def gen_map42(sub: int) -> str:
    doc = json.loads((CAT42 / f"subtype_{sub}.json").read_text(encoding="utf-8"))
    used: set[str] = set()
    hints = {
        "SMF42RTY": "smf_record_type",
        "SMF42SID": "smf_system_id",
        "SMF42SSI": "subsystem_id",
        "SMF42STY": "subtype",
        "SMF42TME": "time",
        "SMF42DTE": "date",
        "S42JDJNM": "job_name",
        "S42JDUID": "user_id",
        "S42JDWSC": "service_class",
        "S42JDWLD": "workload_name",
        "S42JDSTN": "step_name",
        "S42DSSC": "storage_class",
        "S42DSIOR": "avg_response",
        "S42DSION": "io_count",
    }
    lines = [
        f"* ====================================================================",
        f"* SMF TYPE 42 SUBTYPE {sub} — {doc.get('title','DFSMS')}",
        f"* From catalog/smf42 (IBM Docs scrape). Nested DS sections omitted",
        f"* (offsets live inside job header — not fixed TRIPLET-safe).",
        f"* ====================================================================",
        f"TABLE42_{sub} SMF_START",
        "",
    ]
    # Group fields by section preserving order
    by_sec: dict[str, list] = {}
    order: list[str] = []
    for f in doc["fields"]:
        if f.get("status") != "todo" or not f.get("hlasm_type"):
            continue
        if f["ibm_name"] in {"*", "SMF42END"} or f["ibm_name"].startswith("*"):
            continue
        sec = f["section"]
        if sec not in by_sec:
            by_sec[sec] = []
            order.append(sec)
        by_sec[sec].append(f)

    emitted_trips: set[str] = set()
    for sec in order:
        trip = match_42_triplet(sec)
        if trip is False:
            continue  # nested / unmatched
        fields = by_sec[sec]
        if trip is None:
            # header — only useful identity/meta-ish payload
            lines.append(f"* --- {sec} ---")
            for f in fields:
                if f["ibm_name"] not in {
                    "SMF42RTY",
                    "SMF42SID",
                    "SMF42SSI",
                    "SMF42STY",
                    "SMF42TME",
                    "SMF42DTE",
                }:
                    continue
                js = json_key(f["ibm_name"], used, hints)
                lines.append(
                    field_line(
                        f"{f['ibm_name']}-SMF42RCL", f["hlasm_type"], js
                    ).rstrip("\n")
                )
                lines.append("")
            continue
        if trip in emitted_trips:
            continue
        # section base = first field name in section (DSECT start)
        base = fields[0]["ibm_name"]
        lines.append(f"* --- {sec} via {trip} ---")
        emitted_trips.add(trip)
        for f in fields:
            js = json_key(f["ibm_name"], used, hints)
            lines.append(
                field_line(
                    f"{f['ibm_name']}-{base}",
                    f["hlasm_type"],
                    js,
                    f"{trip}-SMF42RCL",
                ).rstrip("\n")
            )
            lines.append("")
    lines.append("         SMF_END")
    lines.append("")
    return "\n".join(lines)


def write_all_map42() -> list[int]:
    subs = []
    for p in sorted(CAT42.glob("subtype_*.json")):
        m = re.match(r"subtype_(\d+)\.json", p.name)
        if not m:
            continue
        sub = int(m.group(1))
        body = gen_map42(sub)
        (SRC / f"MAP42S{sub}.asm").write_text(body, encoding="utf-8")
        subs.append(sub)
    # default TABLE42 = subtype 6 (richest common analytics) fallback header-ish
    default = gen_map42(6 if 6 in subs else subs[0])
    default = default.replace(f"TABLE42_{6 if 6 in subs else subs[0]}", "TABLE42", 1)
    default = default.replace(f"SUBTYPE {6 if 6 in subs else subs[0]}", "DEFAULT", 1)
    (SRC / "MAP42.asm").write_text(default, encoding="utf-8")
    return sorted(subs)


# ---------------------------------------------------------------------------
# SMF 14 / 15 lean + richer known dataset fields
# ---------------------------------------------------------------------------

def write_map14_15() -> None:
    for typ, title in [
        (14, "INPUT or RDBACK data set activity"),
        (15, "OUTPUT/UPDAT/INOUT/OUTIN data set activity"),
    ]:
        p = f"SMF{typ}"
        lines = [
            f"* ====================================================================",
            f"* SMF TYPE {typ} — {title}",
            f"* Header + common job identity (IFASMFR). Expand sections from SA38-0667.",
            f"* ====================================================================",
            f"TABLE{typ}  SMF_START",
            "",
            field_line(f"{p}RTY-{p}LEN", "T_DEC1", "smf_record_type").rstrip("\n"),
            "",
            field_line(f"{p}SID-{p}LEN", "T_CHR4", "smf_system_id").rstrip("\n"),
            "",
            field_line(f"{p}TME-{p}LEN", "T_TME", "time").rstrip("\n"),
            "",
            field_line(f"{p}DTE-{p}LEN", "T_DTE", "date").rstrip("\n"),
            "",
            field_line(f"{p}JBN-{p}LEN", "T_CHR8", "job_name").rstrip("\n"),
            "",
            field_line(f"{p}RST-{p}LEN", "T_TME", "reader_start_t").rstrip("\n"),
            "",
            field_line(f"{p}RSD-{p}LEN", "T_DTE", "reader_start_d").rstrip("\n"),
            "",
            field_line(f"{p}UIF-{p}LEN", "T_CHR8", "user_id").rstrip("\n"),
            "",
            field_line(f"{p}NDS-{p}LEN", "T_DEC1", "dataset_count").rstrip("\n"),
            "",
            "         SMF_END",
            "",
        ]
        write_asm(SRC / f"MAP{typ}.asm", lines)


# ---------------------------------------------------------------------------
# SMF 119 from pacsys JSON
# ---------------------------------------------------------------------------

def pac_hlasm(fmt: str, length, name: str = "") -> str | None:
    f = (fmt or "").lower()
    n = name.upper()
    try:
        ln = int(re.sub(r"[^0-9]", "", str(length)) or "0")
    except ValueError:
        ln = 0
    if n.endswith("TME") and ln == 4:
        return "T_TME"
    if n.endswith("DTE") and ln == 4:
        return "T_DTE"
    if "ebcdic" in f or "character" in f:
        return {1: "T_CHR1", 2: "T_CHR2", 4: "T_CHR4", 8: "T_CHR8", 20: "T_CHR20"}.get(ln)
    if "packed" in f and ln == 4:
        return "T_DTE"
    if "binary" in f:
        return {1: "T_DEC1", 2: "T_DEC2", 4: "T_DEC4"}.get(ln)
    return None


def gen_map119(sub: int) -> str | None:
    path = PAC119 / f"st{sub:02d}.json"
    if not path.exists():
        return None
    doc = json.loads(path.read_text(encoding="utf-8"))
    used: set[str] = set()
    hints = {
        "SMF119RTY": "smf_record_type",
        "SMF119SID": "smf_system_id",
        "SMF119TME": "time",
        "SMF119DTE": "date",
        "SMF119STY": "subtype",
        "SMF119TI_SYSName": "system_name",
        "SMF119TI_SysplexName": "sysplex_name",
        "SMF119TI_Stack": "stack_name",
        "SMF119TI_ASName": "as_name",
        "SMF119TI_UserID": "user_id",
    }
    lines = [
        f"* ====================================================================",
        f"* SMF TYPE 119 SUBTYPE {sub} — TCP/IP Statistics",
        f"* Generated from temp/smf119-app pacsys layouts. Labels: CommServer/IFASMFR.",
        f"* ====================================================================",
        f"TABLE119_{sub} SMF_START",
        "",
    ]
    for sec in doc.get("sections") or []:
        trip = sec.get("triplet") or "HEADER"
        fields = sec.get("fields") or []
        # pick supported
        supported = []
        for f in fields:
            if f.get("reserved"):
                continue
            ht = pac_hlasm(f.get("format"), f.get("length"), f.get("name", ""))
            if not ht:
                continue
            supported.append((f, ht))
        if not supported:
            continue
        if trip == "HEADER":
            lines.append("* --- header ---")
            base = "SMF119LEN"
            for f, ht in supported:
                # keep common header only to avoid huge BIT dumps
                if f["name"] not in {
                    "SMF119RTY",
                    "SMF119SID",
                    "SMF119TME",
                    "SMF119DTE",
                    "SMF119STY",
                    "SMF119WID",
                    "SMF119SSI",
                }:
                    continue
                js = json_key(f["name"], used, hints)
                lines.append(field_line(f"{f['name']}-{base}", ht, js).rstrip("\n"))
                lines.append("")
        else:
            # identification / self-def sections via fixed triplet in header
            lines.append(f"* --- section via {trip} ---")
            base = supported[0][0]["name"]
            for f, ht in supported:
                js = json_key(f["name"], used, hints)
                lines.append(
                    field_line(
                        f"{f['name']}-{base}", ht, js, f"{trip}-SMF119LEN"
                    ).rstrip("\n")
                )
                lines.append("")
    lines.append("         SMF_END")
    lines.append("")
    return "\n".join(lines)


def write_map119() -> list[int]:
    # Priority subtypes for TCP/IP analytics
    wanted = [1, 2, 5, 6, 7, 8, 10, 11, 12, 20, 21]
    done = []
    for sub in wanted:
        body = gen_map119(sub)
        if not body:
            continue
        (SRC / f"MAP119S{sub}.asm").write_text(body, encoding="utf-8")
        done.append(sub)
    return done


# ---------------------------------------------------------------------------
# Patch SMF2JSON.asm
# ---------------------------------------------------------------------------

def _subtype_dispatch(typ: int, subs: list[int], default_table: str | None = None) -> str:
    subs = sorted(subs)
    out = [f"* ---  TYPE {typ} ---\n", f"         CLI   5(R9),{typ}\n", f"         BNE   NO_{typ}\n"]
    if not subs:
        out.append(f"         LARL  R8,TABLE{typ}\n")
        out.append("         J     JSONOBJ\n")
        out.append(f"NO_{typ}   EQU   *\n\n")
        return "".join(out)
    out.append("         LH    R1,22(,R9)        * subtype halfword\n")
    for i, sub in enumerate(subs):
        label = f"T{typ}_{sub}"
        nxt = f"T{typ}_{subs[i+1]}" if i + 1 < len(subs) else f"T{typ}_DEF"
        out.append(f"{label:<8} CHI   R1,{sub}\n")
        out.append(f"         BNE   {nxt}\n")
        out.append(f"         LARL  R8,TABLE{typ}_{sub}\n")
        out.append("         J     JSONOBJ\n")
    out.append(f"T{typ}_DEF EQU   *\n")
    if default_table:
        out.append(f"         LARL  R8,{default_table}\n")
        out.append("         J     JSONOBJ\n")
    else:
        out.append("         J     NEXT_SMF          * unsupported subtype\n")
    out.append(f"NO_{typ}   EQU   *\n\n")
    return "".join(out)


def patch_smf2json(subs42: list[int], subs119: list[int]) -> None:
    path = SRC / "SMF2JSON.asm"
    text = path.read_text(encoding="utf-8")

    # Expand IFASMFR list
    m = re.search(r"         IFASMFR \(([^)]+)\)[^\n]*\n", text)
    if not m:
        raise SystemExit("IFASMFR line missing")
    types = sorted({int(x) for x in m.group(1).split(",")} | {14, 15, 42, 119})
    ifasmfr = (
        "         IFASMFR ("
        + ",".join(str(t) for t in types)
        + ")  * IBM SMF Record Mappings\n"
    )
    text = text[: m.start()] + ifasmfr + text[m.end() :]

    text = re.sub(
        r"\* PURPOSE: CONVERT SMF RECORDS[^\n]*\n",
        f"* PURPOSE: CONVERT SMF RECORDS ({'/'.join(str(t) for t in types)}) TO JSON *\n",
        text,
        count=1,
    )

    extra = (
        _subtype_dispatch(14, [])
        + _subtype_dispatch(15, [])
        + _subtype_dispatch(42, subs42, "TABLE42")
        + _subtype_dispatch(119, subs119)
    )

    # Remove prior injected extra blocks, then insert before TYPE 80
    marker = "* ---  TYPE 80 ---"
    if marker not in text:
        raise SystemExit("TYPE 80 marker missing in SMF2JSON.asm")
    text = re.sub(
        r"\* ---  TYPE 14 ---.*?(?=\* ---  TYPE 80 ---)",
        "",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"\* ---  TYPE 15 ---.*?(?=\* ---  TYPE 80 ---)",
        "",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"\* ---  TYPE 42 ---.*?(?=\* ---  TYPE 80 ---)",
        "",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"\* ---  TYPE 119 ---.*?(?=\* ---  TYPE 80 ---)",
        "",
        text,
        count=1,
        flags=re.S,
    )
    text = text.replace(marker, extra + marker, 1)

    # COPY list: inject MAP14/15/42*/119* before MAP80, keep gatherer copies
    m = re.search(
        r"\*--- Mapping Tables ---\*.*?(?=DYNAMIC_WORK DSECT)",
        text,
        re.S,
    )
    if not m:
        raise SystemExit("mapping COPY block not found")
    block = m.group(0)
    copies = re.findall(r"COPY\s+(MAP\S+)", block)
    # drop previous extras then rebuild order: TYPES, MAP30*, extras, gatherer, MAP80/89
    extras = (
        ["MAP14", "MAP15", "MAP42"]
        + [f"MAP42S{s}" for s in subs42]
        + [f"MAP119S{s}" for s in subs119]
    )
    keep = [c for c in copies if c not in extras and c not in {"TYPES", "MAP80", "MAP89"}]
    # MAP30 first among keep
    map30 = [c for c in keep if c.startswith("MAP30")]
    other = [c for c in keep if not c.startswith("MAP30")]
    ordered = ["TYPES", "MAP30"] + [c for c in map30 if c != "MAP30"] + extras + other + ["MAP80", "MAP89"]
    # unique preserve order
    seen: set[str] = set()
    final = []
    for c in ordered:
        if c not in seen:
            seen.add(c)
            final.append(c)
    copy_block = (
        "*--- Mapping Tables ---*\n"
        "         DS    0F                  * Alignement\n"
        + "".join(
            f"         COPY  {c}"
            + ("               * T_* datatype constants\n" if c == "TYPES" else
               "               * type 30 default\n" if c == "MAP30" else "\n")
            for c in final
        )
        + "\n"
    )
    text = text[: m.start()] + copy_block + text[m.end() :]
    path.write_text(text, encoding="utf-8")
    print("Patched SMF2JSON.asm")


def patch_jcl(subs42: list[int], subs119: list[int]) -> None:
    for jcl in (ROOT / "jcl" / "SMFEXTRT.jcl", ROOT / "jcl" / "SMFEXTRL.jcl"):
        text = jcl.read_text(encoding="utf-8")
        m = re.search(r"OUTDD\(DUMPOUT,TYPE\(([^)]+)\)\)", text)
        if not m:
            continue
        types = sorted({int(x) for x in m.group(1).split(",")} | {14, 15, 42, 119})
        type_list = ",".join(str(t) for t in types)
        text2 = re.sub(
            r"OUTDD\(DUMPOUT,TYPE\([^)]+\)\)",
            f"OUTDD(DUMPOUT,TYPE({type_list}))",
            text,
        )
        jcl.write_text(text2, encoding="utf-8")


def main() -> int:
    write_map30cmn()
    write_map70s1()
    write_map72s3()
    subs42 = write_all_map42()
    write_map14_15()
    subs119 = write_map119()
    patch_smf2json(subs42, subs119)
    patch_jcl(subs42, subs119)
    print(f"MAP42 subtypes: {subs42}")
    print(f"MAP119 subtypes: {subs119}")
    print("Updated MAP30CMN, MAP70S1, MAP72S3, MAP14, MAP15, SMF2JSON, JCL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
