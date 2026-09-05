# Python port roadmap

Companion to the HLASM engine roadmap in the repo root `README.md`.
This file is the Python desktop/CLI track only.

## Now (done)

- [x] Table-driven convert for SMF 30 (subtypes 1–6), 80 (RACF z/OS 3.1 fixed + relocate), 89 (header)
- [x] VB / VBS RDW reader (spanned segments assembled)
- [x] Stdlib CLI (`json` / `csv`) and Tkinter GUI
- [x] Column tooltips: header = JSON key, tip = IBM name + description
- [x] Per-type/subtype column picker persisted in `~/.smf2json/columns.json`
- [x] Notebook tabs when a dump has several types / subtypes
- [x] SMF 119 subtypes 1–4, 5–8, 10–12, 20–24, 32–45, 48–52, 70–81 from PACSYS / IBM layouts (119-4 NMTP partial)
- [x] Synthetic sample dump (14 + 15 + 17 + 30-1/4/5 + 42-20/21/24 + 61 + 65 + 66 + 80 + 119-1/2/3/4/10) and unittest coverage

## Next maps (desktop value)

Priority is types that show up in IFASMFDP extracts and have a clear PACSYS/IBM table.

- [x] **119-2** TCP connection termination (bytes in/out, elapsed, term code)
- [x] **119-3 / 119-70** FTP client / server transfer completion
- [x] **119-10** UDP endpoint close
- [x] **119-11 / 119-12** zERT connection detail / summary
- [x] **119-20 / 119-21** TN3270E session init/term
- [x] **119-4** TCP/IP profile (NMTP) — **partial**: PICommon, PIDS, ALPROC, V4CFG, V6CFG, TCPCFG, UDPCFG, GBLCFG. Unmapped: PORT, INTF, IPA6, ROUT, SRCIP, MGMT, IPSec*, NETACC, DV*, DASP, FLTP/FLTE
- [x] **14** INPUT DATA SET ACTIVITY (non-VSAM)
- [x] **15** OUTPUT DATA SET ACTIVITY (non-VSAM)
- [x] **17** SCRATCH DATA SET STATUS
- [x] **80** (RACF) — **z/OS 3.1 / 3.01.00**, PACSYS fixed layout
  ([smf80.htm](https://www.pacsys.com/smf/smf80.htm)): full fixed section through
  `SMF80AU2`, classic relocate tags **1–4, 6, 8, 9, 13, 15–17, 20**, extended
  relocate (`SMF80TP2`) tags **441 / 444** (MFA). `MAPS_BY_TYPE[80]` (bytes 22–23
  = `SMF80USR`). Samples: EVT **2** resource access + MFA factor; EVT **1** job init.
  Remaining optional polish (same map):
  - [ ] DEFINE / RENAME / DELETE (EVT 3–7) — tag 2/13 sample records
  - [ ] RACF command EVT samples (tag 6/9 payloads)
  - [ ] APPCLU / UNIX / more MFA TP2 tags beyond 441/444
- [x] **30** — per-`SMF30STP` subtype maps **1–6** via `MAPS_BY_SUBTYPE` (COMMON = header + subsystem + identification; resource sections per IBM/PACSYS):
  - [x] **30-1** Job initiation (COMMON only — no resource sections)
  - [x] **30-2** Interval (I/O, processor, storage, performance)
  - [x] **30-3** Step or interval termination (same sections as 30-2)
  - [x] **30-4** Step total (I/O, completion, processor, storage, performance, operator)
  - [x] **30-5** Job termination (same sections as 30-4)
  - [x] **30-6** System address space (I/O, processor, storage, performance; partial fields on real dumps)
- [x] **61** ICF DEFINE ACTIVITY
- [x] **65** ICF DELETE ACTIVITY
- [x] **66** ICF ALTER ACTIVITY
- [x] **42** DFSMS — subtypes **20, 21, 22, 23, 24, 25** (STOW init / member delete / DFSMSrmm audit+security / member add-replace / rename via `MAPS_BY_SUBTYPE`)
- [ ] Packed decimal (`P`) and more HEX/flag decode where IBM tables need it

When adding a 119 subtype: extend the temp/smf119-app layout, run `python python/tools/gen_smf119_maps.py`, add a sample + test. Do not reuse another subtype's S1 layout. Subtype 4 NMTP coverage is partial (see checkbox note). OpenSSH 94–98 stay unmapped.

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
