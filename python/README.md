# SMF2JSON Desktop — Python port of the HLASM engine

Stdlib only (tkinter for GUI). No pip packages required.

How the code is structured (for agents and contributors): **[AGENTS.md](AGENTS.md)**.  
What is planned next: **[ROADMAP.md](ROADMAP.md)**.

```
python/
  smf2json/          # importable package
  samples/           # generated sample dumps
  tests/             # unit tests
  AGENTS.md
  ROADMAP.md
  README.md
```

## Quick start

```text
cd python

# Synthetic VB dump (14/15/17, 30-1/4/5, 42, 61/65/66, 80, 119-1/2/3/4/10)
python -m smf2json --make-sample samples/sample.smf

# Real SMF 119 dump (TERSE → convert)
python -m smf2json.terse samples/119/A910826.SMF119.TRS -o samples/119/A910826.SMF119.smf
python -m smf2json samples/119/A910826.SMF119.smf -o samples/119/out.json

# CLI (stderr progress bar + records/dump timing; --no-progress to hide the bar)
python -m smf2json samples/sample.smf -o samples/sample.json
python -m smf2json samples/sample.smf -f csv -o samples/sample.csv

# GUI (tabs per type/subtype, column tooltips, Columns… picker)
python -m smf2json
python -m smf2json --gui samples/sample.smf

# Tests
python -m unittest discover -s tests -v
```

## Input

Binary **RECFM=VB / VBS** dump (RDW-framed), as produced by IFASMFDP / IFASMFDL.
Copy the file in binary mode. Text / hex listings / SYSOUT will not parse.

## Supported maps

| Type | Subtype | Contents |
|---|---|---|
| 14 | — | INPUT data set activity (non-VSAM) |
| 15 | — | OUTPUT data set activity (non-VSAM) |
| 17 | — | Scratch data set status |
| 30 | 1–6 | Address space work via `SMF30STP` (`MAPS_BY_SUBTYPE`) |
| 42 | 20–25 | DFSMS STOW / member / DFSMSrmm |
| 61 / 65 / 66 | — | ICF DEFINE / DELETE / ALTER |
| 80 | — | RACF z/OS 3.1 fixed + relocate tags 1/2/3/4/8/9/13/15/16/17/20 (`MAPS_BY_TYPE`; bytes 22–23 = `SMF80USR`) |
| 89 | — | Header subset |
| 119 | 1–4, 5–8, 10–12, 20–24, 32–45, 48–52, 70–81 | TCP/IP (connections, FTP, profile/NMTP partial, TN3270, DVIPA, CSSMTP, IPSec, …) |

Unmapped 119 subtypes: **94–98** (OpenSSH). Subtype **4** is mapped **partially** (common + stack cfg NMTP sections). Other types are skipped until a map is added.

## GUI notes

- One **tab** per SMF type (and subtype when the map has `smf_subtype`).
- Column header = JSON key (`time`). Hover tip = IBM name + description (`SMF80TME`).
- **Columns…** (after load) saves the visible set per type/subtype to `~/.smf2json/columns.json`.
- Large dumps load on a background thread in batches; a progress bar shows percent of the file. When done, status shows **records** vs **dump** elapsed time. **Cancel load** keeps rows already shown.
- CSV export is the current tab; JSON export is the whole dump.
