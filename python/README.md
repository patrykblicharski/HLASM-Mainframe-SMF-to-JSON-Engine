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

# Synthetic VB dump (types 30 + 80 + 119-1/2/3/10)
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
| 30 | — | Common sections (ident, I/O, completion, processor, …) |
| 80 | — | RACF header + relocate tags 1 / 17 |
| 89 | — | Header subset |
| 119 | 1–3, 5–8, 10–12, 20–24, 32–45, 48–52, 70–81 | TCP/IP (connections, FTP, TN3270, DVIPA, CSSMTP, IPSec, …) |

Unmapped 119 subtypes: **4** (TCP/IP profile / NMTP) and **94–98** (OpenSSH). Other types are skipped until a map is added.

## GUI notes

- One **tab** per SMF type (and subtype when the map has `smf_subtype`).
- Column header = JSON key (`time`). Hover tip = IBM name + description (`SMF80TME`).
- **Columns…** (after load) saves the visible set per type/subtype to `~/.smf2json/columns.json`.
- Large dumps load on a background thread in batches; a progress bar shows percent of the file. When done, status shows **records** vs **dump** elapsed time. **Cancel load** keeps rows already shown.
- CSV export is the current tab; JSON export is the whole dump.
