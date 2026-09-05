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

# Synthetic VB dump (types 30 + 80 + 119-1)
python -m smf2json --make-sample samples/sample.smf

# CLI
python -m smf2json samples/sample.smf -o samples/sample.json --debug
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
| 119 | 1 | TCP connection initiation (stack, IPs, ports) |

Other 119 subtypes are skipped until a map is added.

## GUI notes

- One **tab** per SMF type (and subtype when the map has `smf_subtype`).
- Column header = JSON key (`time`). Hover tip = IBM name + description (`SMF80TME`).
- **Columns…** (after load) saves the visible set per type/subtype to `~/.smf2json/columns.json`.
- CSV export is the current tab; JSON export is the whole dump.
