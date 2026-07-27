# SMF → HLASM mapping catalog

Machine-readable field inventory used to extend `src/MAP*.asm` without ad-hoc exploration.

## Sources

| File | Role |
| --- | --- |
| `ref/openapi_spec.json` | IBM z/OS Data Gatherer OpenAPI (IBM names, offsets, datatypes, descriptions) |
| `ref/fields_dump.json` | smfexplorer field introspection (alternate names / UI catalog) |
| `src/MAP30.asm` | Currently mapped fields (status=`mapped`) |

## Generate

```bash
python3 tools/build_smf_catalog.py
```

## SMF type 30 output (`catalog/smf30/`)

| File | Contents |
| --- | --- |
| `summary.json` | Per-subtype field counts and status tallies |
| `subtype_1.json` … `subtype_6.json` | Full field lists |
| `priority.json` | First-wave HLASM candidates |
| `priority_suggested.asm` | Suggested `SMF_FIELD` lines (verify IFASMFR labels) |

### Status values

- `mapped` — already in `MAP30.asm`
- `todo` — engine supports `hlasm_type`; safe to add after IFASMFR check
- `needs_engine` — datatype not in `SMF2ZIIP` BTAB (FLOAT, PACKED, BIT, CHAR>8, …)
- `skip_meta` — Gatherer meta (offsets/lengths/counts)
- `unknown` — missing datatype metadata

## Workflow

1. Regenerate catalog after OpenAPI / map changes.
2. Pick `todo` (+ `priority`) fields.
3. Confirm `section_base` / `triplet` against IBM SMF manual / `IFASMFR`.
4. Add `SMF_FIELD` to `MAP*.asm` (`JSON=` ≤ 16 chars).
5. Re-run the generator so status flips to `mapped`.

See Cursor skill `zsmf-catalog`.

## Planned subtype maps (Gatherer coverage)

See `catalog/planned_subtypes.json` — all OpenAPI type/subtype pairs (47) plus MAP80/MAP89.

- Handcrafted richer maps: 30.1–30.6, 70.1–70.2, 71.1, 72.3  
- Auto-generated header (+ RMF product section where present): remaining pairs  
- Regenerate: `python3 tools/gen_gatherer_maps.py`
