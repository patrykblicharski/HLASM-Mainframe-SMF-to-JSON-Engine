# SMF 119 Dump Explorer

Standalone offline decoder for **SMF Type 119** (z/OS Communications Server
TCP/IP). Independent of Data Gatherer, `smfexplorer`, and the other apps in
this repository.

Layouts are Python re-expressions of the packed C mappings in IBM headers
`ezasmf.h` (record/header/triplets/all subtypes) and `ezbnmmpc.h` (TCP/IP
profile sections for subtype 4). Status baseline: **ZCSV2R5**. Where the
local IBM headers are unavailable, PACSYS public offset tables are used as an
additional source for field order/size (see `tools/`).

## Run

```bat
cd smf119-app
py -3 main.py
```

No virtualenv or pip install required (stdlib + Tkinter).

Validate layout registry:

```bash
python3 tools/check_layouts.py
```

## What it does

1. Scans a binary IFASMFDP-style dump for SMF records with type **119**
2. Inventories subtypes present with a coverage badge (`mapped` / `external`)
3. Decodes each record via **self-defining triplets**
4. Shows a **summary record list** (per-subtype business columns) plus full
   section field tables in the detail pane
5. Supports **Labels ↔ IBM names**, hide-empty optional sections, and export:
   - list CSV (summary columns)
   - record JSON / flat CSV (every decoded `section.field`)
6. Field / subtype catalog with mapped section and field counts

## Coverage

| Status | Subtypes | Notes |
|--------|----------|-------|
| mapped | 1–8, 10–12, 20–24, 32–45, 48–52, 70–81 | Full section layouts + summary columns |
| external | 94–98 | OpenSSH — no layouts in `ezasmf.h`; Ident + raw preview only |

Subtype **4** (TCP/IP profile) uses the full `NMTP_*` section set from
`ezbnmmpc.h`. Other subtypes live under `parser/layouts/stXX.py`.

## Presentation model

Do not dump every field into one mega-wide record grid. Two layers:

1. **Record list** — 5–12 summary columns per subtype (time, SID, stack, plus
   business keys such as IP:port, bytes, user, DSN, LU)
2. **Record detail** — section tree; each section is a full field table.
   Optional sections with `Num=0` are hidden unless “Show empty” is on.

## Architecture

```
smf119-app/
├── main.py
├── gui/app.py                 # Tkinter UI (summary list + section tables)
├── tools/
│   ├── check_layouts.py       # registry / coverage validation
│   ├── parse_pacsys.py        # optional PACSYS HTML → JSON
│   └── gen_layouts_from_pacsys.py
└── parser/
    ├── layout.py              # packed BE field engine (ipv6mapped, var_ebcdic, …)
    ├── header_layouts.py      # header / triplets / Ident
    ├── nmtp_layouts.py        # subtype-4 profile sections
    ├── layouts/stXX.py        # per-subtype section layouts
    ├── layouts_loader.py      # discovers + registers stXX modules
    ├── registry.py            # SUBTYPE_SECTIONS / EYE_LAYOUTS / COVERAGE
    ├── views.py               # SUMMARY columns + summarize()
    ├── subtypes.py
    ├── catalog.py
    ├── dump_index.py
    ├── decode.py
    └── ebcdic.py
```

## Decode path

```
Smf119Header (24)
 → SMF119SDefSect (TRN + triplets)
 → SMF119Ident (triplet 0)
 → record-specific sections (triplet 1..)
      registry SUBTYPE_SECTIONS[subtype] or eyecatcher / NMTP profile
```

## Notes

- Endianness: big-endian; packing: 1-byte aligned (IBM `_Packed` / `#pragma pack(1)`)
- Text fields: EBCDIC CP037
- IPv4-mapped IPv6 addresses decode to dotted IPv4 when applicable
- Variable EBCDIC sections (FTP DSN, hostnames, IPSec DN trails) use triplet Len
- IBM headers are Licensed Materials; this app does not redistribute them
