# SMF Dump Explorer — offline binary dump reader (Tkinter)

Standalone app: **no Gatherer, no smfexplorer**. Reads a classic IFASMFDP
SMF dump downloaded as a binary file, discovers which Gatherer-supported
SMF type/subtype pairs are present, and shows a decoded table for the
selected pair.

## Run

```bat
cd smf-dump-app
py -3 main.py
```

Default dump path pre-filled if `../IZYP.SMFT000.EXPLORER.bin` exists.

## How discovery works

The sample dump is not a clean contiguous RDW/VBS byte stream — SMF records
are interleaved with padding. The scanner finds standard 24-byte SMF headers
where:

- record type/subtype is in the IBM z/OS Data Gatherer set (30, 70–79, 99, 113)
- SID and SSI decode as EBCDIC identifiers
- header flag bit “subtypes used” is set

## Decoding

1. Always: standard header (`System ID`, `Subtype`, `Time`, …)
2. Plus leaf fields from `SMF{type}_SUBTYPE{subtype}` in
   `smf-mock/mock_server/openapi_spec.json` (`x-zml-*` layouts)
3. Table headers use OpenAPI **descriptions** (documentation text)
4. Only **default** columns are shown initially (header defaults + first 12
   non-meta OpenAPI fields); **Columns…** opens a picker with descriptions
   for the remaining fields (same idea as `smf-explorer-app`)

Nested section expansion (self-defining triplets → section schemas) is a
follow-up; v1 focuses on discovery + root/header fields.
