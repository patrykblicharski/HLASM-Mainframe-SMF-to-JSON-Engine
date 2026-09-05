# Python port roadmap

Companion to the HLASM engine roadmap in the repo root `README.md`.
This file is the Python desktop/CLI track only.

## Now (done)

- [x] Table-driven convert for SMF 30 (common sections), 80 (RACF + relocate), 89 (header)
- [x] VB / VBS RDW reader (spanned segments assembled)
- [x] Stdlib CLI (`json` / `csv`) and Tkinter GUI
- [x] Column tooltips: header = JSON key, tip = IBM name + description
- [x] Per-type/subtype column picker persisted in `~/.smf2json/columns.json`
- [x] Notebook tabs when a dump has several types / subtypes
- [x] SMF 119 subtype 1 (TCP connection initiation) from PACSYS / IBM layout
- [x] Synthetic sample dump (30 + 80 + 119-1) and unittest coverage

## Next maps (desktop value)

Priority is types that show up in IFASMFDP extracts and have a clear PACSYS/IBM table.

- [ ] **119-2** TCP connection termination (bytes in/out, elapsed, term code) — natural pair to 119-1
- [ ] **119-3** FTP server transfer completion
- [ ] **119-10 / 119-11** TN3270 session init/term
- [ ] **14 / 15** dataset activity (non-VSAM)
- [ ] **42** DFSMS
- [ ] Packed decimal (`P`) and more HEX/flag decode where IBM tables need it

When adding a 119 subtype: new `FIELDS` list + `MAPS_BY_SUBTYPE[(119, N)]` + sample + test. Do not reuse the 119-1 S1 layout.

## Engine / GUI

- [ ] Filter / search in the current tab
- [ ] Sort by clicking a column heading
- [ ] Export JSON of the current tab (today JSON is the whole dump)
- [ ] Persist last dump path and last selected tab
- [ ] Optional second tooltip line for flag-bit decode (e.g. `SMF119TI_Reason`)

## Quality / CI

See `.cursor/rules/python-ci.mdc`. Minimum useful CI:

- [ ] GitHub Actions: `unittest discover` on Windows + Ubuntu, Python 3.10–3.12
- [ ] Smoke: `--make-sample` then convert to JSON and assert 3 record types
- [ ] No pip install step (stdlib only)

## Out of scope for this package

- z/OS Gatherer / `smfexplorer` (that is `temp/smf-explorer-app/`)
- HLASM / zIIP engine changes (repo root)
- Adding PyPI dependencies for a “nicer” GUI
