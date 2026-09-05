---
name: zsmf-architecture
description: Mental model of the zSMFtoJSON HLASM engine — modules, mapping tables, dispatch, macros, and portability rules. Use when exploring the repo, planning SMF map work, or before adding types/fields.
---

# zSMFtoJSON — Architecture Notes

High-performance z/OS HLASM engine that parses raw SMF records into JSON via **table-driven** Master Mapping Tables. Core conversion logic stays unchanged when fields are added.

## Modules

| File | Role |
| :--- | :--- |
| `src/SMF2JSON.asm` | Driver: open SMF/JSON DDs, filter record types, pick mapping table, call converter, write VB JSON lines |
| `src/SMF2ZIIP.asm` | Reentrant converter: walk mapping table → emit one JSON object |
| `src/MAP30.asm` / `MAP80.asm` / `MAP89.asm` | Per-type field tables (`TABLE30`, `TABLE80`, `TABLE89`) |
| `src/CONFIG.asm` | `&USEZIIP` (0=TCB public default, 1=SRB/zIIP private) |
| `jcl/SMF2JSON.jcl` | Assemble + link + run |
| `jcl/SMFEXTRT.jcl` / `SMFEXTRL.jcl` | Extract SMF from MAN / Logstream |

IBM DSECTs come from `IFASMFR (30,80,89)` in `SMF2JSON.asm` (macros from SYS1.MACLIB / product MACLIBs).

## Data flow

1. `GET SMFFILE` → RDW in R9
2. Skip spanned segments; skip types 2 and 3
3. `CLI 5(R9),type` → `LARL R8,TABLEnn` → `JSONOBJ`
4. Pass `MYPARMS` (`P_SMFREC`, `P_TABLE`, `P_JSONBUF`, `P_WORKAREA`) to `SMF2ZIIP`
5. Converter loops table entries until offset sentinel `AL4(0)`
6. Driver wraps objects in a JSON array (`[` … `,` … `]`)

## Mapping macros (defined in SMF2JSON.asm)

```asm
TABLEnn  SMF_START
         SMF_FIELD offset-expr,TYPE=T_xxx,JSON=json_key
         SMF_FIELD offset-expr,TRIPLET=trip-expr,TYPE=T_xxx,JSON=json_key
         SMF_FIELD offset-expr,TYPE=T_RS_STR,TAG=T_RS_n,JSON=json_key
         SMF_END
```

### Entry layout (28 bytes — trust the code, not README “24”)

| Bytes | Content |
| ---: | :--- |
| 0–3 | `AL4` relative field offset |
| 4–7 | `AL4` triplet offset (0 = header / no triplet) |
| 8 | `AL1` data type (`T_*`) |
| 9 | `AL1` RS tag id (or 0) |
| 10–11 | `AL2` padding |
| 12–27 | `CL16` JSON label |

Engine advances with `LA R8,28(,R8)`.

## Portability rules (prefer these always)

1. **Never hardcode numeric offsets** — use IBM `IFASMFR` labels: `SMF30CPT-SMF30PTY`.
2. **Header fields**: `FIELD - SMFxxLEN`, no `TRIPLET=`.
3. **Section fields**: `FIELD - SECTION_START`, `TRIPLET=TRIPLET_OF-SMFxxLEN`.
4. **RS fields** (SMF 80): `SMF80REL-SMF80LEN`, `TYPE=T_RS_STR`, `TAG=T_RS_n`.
5. Keep JSON keys ≤ 16 chars (macro truncates / pads `CL16`).
6. Continuation column for long lines: `X` in column 72.

## Current type coverage

Gatherer OpenAPI set (47 pairs) + 80/89 — see `catalog/planned_subtypes.json`.

| Family | Maps | Notes |
| :--- | :--- | :--- |
| 30.1–30.6 | `MAP30S*` + `MAP30CMN` | Rich handcrafted fields |
| 70–79, 72.4–5, 73… | `MAPxxSy.asm` | Header + product (generated) |
| 99.*, 113.* | `MAP99S*` / `MAP113S*` | Header |
| 80 / 89 | `MAP80` / `MAP89` | Non-Gatherer |

Datatype EQU: `src/TYPES.asm`. Generator: `tools/gen_gatherer_maps.py`.

## Subtypes

Generated dispatch in `SMF2JSON.asm` reads halfword @ +22 after type match, then `LARL` `TABLExx_y`. Unknown 30 subtype → `TABLE30`. Missing sections → `""`.

## Mode notes

- Public build: TCB (`&USEZIIP=0`), direct `BASR` to `SMF2ZIIP`.
- SRB path needs proprietary `ZSCHDSRB` / auth; not in this repo.
- Converter is reentrant: per-call work area via `P_WORKAREA` / `DYNAMIC_WORK`.

## Related skills

- `zsmf-add-field` — add/change one mapped field
- `zsmf-add-type` — new SMF type or subtype table
- `zsmf-ibm-docs` — look up IBM field names / formats
- `zsmf-data-types` — `T_*` constants vs engine cases
- `zsmf-json-labels` — JSON key / column naming
