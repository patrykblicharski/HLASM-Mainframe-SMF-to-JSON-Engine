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
- [x] SMF 119 subtypes 1–3, 5–8, 10–12, 20–24, 32–45, 48–52, 70–81 from PACSYS / IBM layouts
- [x] Synthetic sample dump (30 + 80 + 119-1/2/3/10) and unittest coverage

## Next maps (desktop value)

Priority is types that show up in IFASMFDP extracts and have a clear PACSYS/IBM table.

- [x] **119-2** TCP connection termination (bytes in/out, elapsed, term code)
- [x] **119-3 / 119-70** FTP client / server transfer completion
- [x] **119-10** UDP endpoint close
- [x] **119-11 / 119-12** zERT connection detail / summary
- [x] **119-20 / 119-21** TN3270E session init/term
- [ ] **119-4** TCP/IP profile (NMTP eyecatcher sections)
- [ ] **14 / 15** dataset activity (non-VSAM)
- [ ] **42** DFSMS
- [ ] Packed decimal (`P`) and more HEX/flag decode where IBM tables need it

When adding a 119 subtype: extend the temp/smf119-app layout, run `python python/tools/gen_smf119_maps.py`, add a sample + test. Do not reuse another subtype's S1 layout. Subtype 4 (profile) and 94–98 (OpenSSH) stay unmapped.

## Engine / GUI

- [x] GUI stays responsive on large dumps (background convert, batched tree insert)
- [x] CLI streams convert in batches with a stderr progress bar and records/dump timing
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
