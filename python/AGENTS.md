# SMF2JSON Python — agent notes

Stdlib-only desktop/CLI port of the HLASM table-driven SMF converter.
**Read this file instead of re-walking the package** unless you are changing the named module.

Language: English in code, comments, docs. Chat with the owner may be Polish.

## Layout

```
python/
  smf2json/
    __main__.py        CLI / GUI entry (`python -m smf2json`)
    reader.py          RECFM=VB / VBS dump walker (RDW-framed)
    engine.py          FieldSpec → dict rows
    types.py           FieldSpec + converters (CHR/DEC/HEX/DTE/TME/IP16/IPUN/VAR_CHR)
    maps/              One module per SMF type (or type+subtype); 119 sections in smf119_generated.py
    progress.py        Byte bar + elapsed-time formatting (CLI stderr / GUI status)
    gui.py             Tkinter: notebook tabs, column picker, tooltips
    column_config.py   Visible columns persisted per type/subtype
    sample_dump.py     Synthetic VB records for 30, 80, 119-1/2/3/10
    terse.py           AMATERSE/TERSE unpacker (PACK/SPACK); `python -m smf2json.terse`
  tools/
    gen_smf119_maps.py Regenerate maps/smf119_generated.py from temp/smf119-app layouts
  unterse.py           Standalone launcher for terse.py
  tests/               stdlib unittest
  samples/             generated dumps (make-sample)
  ROADMAP.md
```

No pip packages. Python 3.10+ (`from __future__ import annotations` is used throughout).

## Data flow

1. `reader.iter_dump(path)` / `read_dump(path)` → records. Each `data` **includes the 4-byte RDW** so IBM offsets (from SMFxLEN) apply as-is. The GUI uses `iter_dump` so it never builds a full `list[SmfRecord]`.
2. `engine.convert_record` looks up `maps.fields_for(type, subtype)`.
   - `MAPS_BY_TYPE[rty]` — types without distinct subtype layouts (30, 80, 89).
   - `MAPS_BY_SUBTYPE[(rty, sty)]` — types whose sections differ by subtype (119).
   - If a type has **any** subtype map, unmapped subtypes are **skipped**.
3. `gui` groups converted rows by `(smf_record_type, smf_subtype|None)` into notebook tabs. Subtype is taken only from the mapped `smf_subtype` field (do not invent it from raw bytes 22–23 on types 30/80).
4. Export: JSON = all rows; CSV = **current tab** (visible columns).

## Input dump format

Binary IFASMFDP / IFASMFDL dump: **RECFM=VB or VBS**, big-endian RDW (`LL` + flags).
Not text, not hex listings, not SYSOUT. Types 2 and 3 (dump control) are skipped.

## Maps (how to add one)

Port of `SMF_FIELD` macros. `FieldSpec`:

| attr | meaning |
|---|---|
| `json_key` | Table header / JSON key (`time`, `remote_ip`) |
| `ibm_name` | Tooltip first line (`SMF119AP_TIRIP`) |
| `description` | Tooltip second line |
| `offset` | Relative to section base (absolute if `triplet_offset` is None) |
| `triplet_offset` | Absolute offset of the section triplet (offset/length/number) in the header |
| `ftype` | See `types.TYPE_LENGTHS` + `convert_value` |
| `tag` | Relocate-section tag (`RS_STR` only) |

Register in `maps/__init__.py`. Add converters in `types.py` only when the IBM format is new. Add `sample_dump.build_*` + a `tests/test_engine.py` case.

PACSYS HTML tables (e.g. smf119_subtype01) are a valid layout source; keep IBM names exact.
SMF 119 subtype sections live in `maps/smf119_generated.py` (header + ident in `maps/smf119.py`).

**Mapped today:** 30 (common sections), 80 (RACF header + RS tags 1/17), 89 (header), 119 subtypes 1–3, 5–8, 10–12, 20–24, 32–45, 48–52, 70–81. Not mapped: 119-4 (NMTP profile), 119-94..98 (OpenSSH, external).

## GUI conventions

- Column **header** = `json_key`. **Tooltip / Field bar** = IBM name + description.
- **Columns…** appears after a dump is loaded. Checkboxes show source key, friendly label, IBM name. Saved to `~/.smf2json/columns.json` under `"30"` or `"119-1"`.
- Header width = `TkHeadingFont.measure(title) + 28`.
- Load runs on a worker thread in batches of 250; the table fills incrementally. A determinate **progress bar** tracks file bytes (percent + MB). When finished, log/status show **records** time (convert loop) and **dump** time (whole load including read + UI). Debug pane gets progress / errors, not per-field DEBUG (that is CLI `--debug`). **Cancel load** keeps rows already shown.

## CLI conventions

- Streams convert in batches of 250 with the same byte progress bar on stderr (`--no-progress` to hide; off with `--debug`).
- End of run always prints `INFO: timing  records … — dump …` (records = parse/convert/write loop; dump = file read + that loop).
- JSON is written as a streaming array. CSV header is taken from the first 250 mapped rows.

## Commands

```text
cd python
python -m smf2json --make-sample samples/sample.smf
python -m smf2json samples/sample.smf -o samples/sample.json --debug
python -m smf2json samples/sample.smf -f csv -o samples/sample.csv
python -m smf2json --gui samples/sample.smf
python unterse.py dump.trs
python -m smf2json.terse dump.trs
python -m unittest discover -s tests -v
```

## Do not

- Add pip dependencies without an explicit ask.
- Parse dumps as text / assume little-endian integers.
- Apply a 119-1 section map to other 119 subtypes.
- Treat type-30/80 bytes 22–23 as `SMFxSTY`.
- Re-read the whole package for column/tooltip/tab behavior — it is all in `gui.py` + `column_config.py`.
