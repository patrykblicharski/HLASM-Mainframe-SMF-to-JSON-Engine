---
name: zsmf-catalog
description: Build and use the SMF field catalog (OpenAPI + fields_dump → catalog/smf30) when planning or adding HLASM MAP fields/types/subtypes and JSON keys.
---

# SMF mapping catalog

Use this skill whenever extending HLASM maps from Gatherer/OpenAPI knowledge instead of guessing fields.

## Layout

- `ref/openapi_spec.json` — Gatherer schemas (`SMF30_SUBTYPE1`…)
- `ref/fields_dump.json` — smfexplorer names/descriptions
- `tools/build_smf_catalog.py` — generator
- `catalog/smf30/` — generated inventories + `priority.json`

## Commands

```bash
python3 tools/build_smf_catalog.py
```

## How to pick fields

1. Open `catalog/smf30/priority.json` for first-wave candidates.
2. Or filter `subtype_N.json` where `status == "todo"` and `hlasm_type` is set.
3. Use `json_key` as `JSON=` (already ≤16).
4. Use `case` / `section_base` / `triplet` as **hints only** — confirm with IFASMFR / IBM Docs (`zsmf-ibm-docs`).
5. Skip `needs_engine` until `SMF2ZIIP` BTAB grows (`zsmf-data-types`).
6. After editing `MAP30.asm`, regenerate so statuses update.

## Related skills

- `zsmf-add-field` — write the `SMF_FIELD` line
- `zsmf-add-type` — new type / subtype tables
- `zsmf-json-labels` — naming rules if inventing keys not in catalog
- `zsmf-architecture` — engine constraints (28-byte entries, type-only dispatch today)

## Important limits

- Catalog covers Gatherer types (30, 70–79, 99, 113, …). **Not** SMF 80/89 — those stay IBM-Docs-driven.
- OpenAPI `x-zml-offset` is section-relative; never paste it as a hard-coded ASM displacement.
- Subtype-specific tables are not dispatched yet; one `TABLE30` serves all subtypes until engine work lands.
