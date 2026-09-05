---
name: zsmf-ibm-docs
description: Look up IBM z/OS SMF field names, formats, triplets, subtypes, and relocate tags for zSMFtoJSON mapping work. Use whenever adding maps/fields or resolving SMFxx* labels from the official SMF manual referenced in README.
---

# Search IBM SMF Documentation

README requires: **z/OS MVS System Management Facilities (SMF)** before adding mappings. Assembler labels come from IBM `IFASMFR` / that manual — not invented names.

## Primary sources

| Source | URL / id | Use for |
| :--- | :--- | :--- |
| IBM Docs HTML (z/OS 3.2) | `https://www.ibm.com/docs/en/zos/3.2.0` — search “Record type NN” | Quick field meaning, subtypes |
| SMF PDF (current) | IBM Docs PDF `ieag200` / publication **SA38-0667** | Full offset tables: Offsets / Name / Length / Format / Description |
| Older PDF mirrors | `publibz` / `publibfp` `iea*g*.pdf` | Offline / alternate editions |
| Macro mappings | `IFASMFR (types)` on z/OS MACLIB | Authoritative assembler labels & DSECT starts |

Type 30 HTML example topic pattern:

`Record type 30 (X'1E') — Common address space work`

PDF chapter: **Chapter 17. SMF records**.

## What to extract per field

From the record’s field table, capture:

1. **Name** — assembler label (`SMF30CPT`)
2. **Length + Format** — maps to `TYPE=` (`zsmf-data-types`)
3. **Description** — basis for JSON key / column wording (`zsmf-json-labels`)
4. **Section** — which DSECT / section start label
5. **Triplet** — if the section lists Offset/Length/Number (`SMF30COF` / `CLN` / `CON`)
6. **Subtype applicability** — which subtypes include the section

IBM table columns look like:

```
Offsets   Name      Length  Format   Description
4    4    SMF30CPT  4       binary   All standard CPU step time…
14   E    SMF30SID  4       EBCDIC   System identification…
```

Triplet blurb pattern:

> Triplet information: located using … **SMF30COF** (offset), **SMF30CLN** (length), **SMF30CON** (number)

## Search recipe

1. Open SMF manual → Chapter 17 → **Record type NN**.
2. Read subtype list (if any) and which sections appear per subtype.
3. Find the section (Header, Identification, Processor, …).
4. Note section **start field** (first named field / DSECT name in IFASMFR — e.g. processor accounting starts at `SMF30PTY`).
5. Note triplet `*OF` field in the header/self-defining section.
6. Pick the data field; map Format → `T_*`.
7. For SMF 80 relocate / “data element” tags: find tag id ↔ meaning (MAP80 already documents tags 1,2,8,9,13,15,17 — extend from the same manual section).

## Web / tooling tips

- Prefer IBM Docs search: `SMF record type 30 SMF30CPT` or `SMF30SOF triplet`.
- IBM Docs HTML is an SPA: use Playwright + classic `ieag200` package URLs (see `tools/ibm_docs/`) when scraping field tables. Carbon topic IDs can collide (e.g. `configuration-subtype-1`).
- Type 42 DFSMS catalog: `catalog/smf42/` from `tools/ibm_docs/crawl_smf42.mjs` + `tools/build_smf42_catalog.py`.
- If HTML 403/blocked in the agent environment, use the PDF (`ieag200_v3r1.pdf` or current z/OS edition) and `rg` over extracted text.
- Cross-check label spelling against existing maps (`MAP30`/`MAP80`) and `IFASMFR` assembly listings when available.
- Db2 101/102 may need **Db2** manuals / `DSNxxx` MACLIB in addition to SA38-0667.
- CICS 110 often needs **CICS** performance/dictionary docs — not only the base SMF book.

## Map to this repo’s three cases

| Docs say | Repo case | Macro |
| :--- | :--- | :--- |
| Field in header / self-defining | Case 1 | `FIELD-SMFxxLEN`, no triplet |
| “Triplet information” + section offsets | Case 2 | `FIELD-SECTSTART`, `TRIPLET=xxOF-SMFxxLEN` |
| Relocate / tag-length-data elements | Case 3 | `TYPE=T_RS_STR`, `TAG=` |

## Type 30 quick anchors (verified patterns in MAP30)

| Triplet | Section theme | Example fields |
| :--- | :--- | :--- |
| `SMF30SOF` | Subsystem / product | `SMF30RVN`, `SMF30PNM` (base `SMF30PSS`) |
| `SMF30IOF` | Identification | `SMF30PGM`, `SMF30STM` (base `SMF30JBN`) |
| `SMF30COF` | Processor accounting | `SMF30CPT`, `SMF30CPS` (base `SMF30PTY`) |
| Header | — | `SMF30RTY`, `SMF30SID`, `SMF30TME`, `SMF30DTE` |
| Subtype | `SMF30STP` | 1 job start … 5 job end … 6 system AS |

## Roadmap doc entry points

| Type | Manual title fragment |
| ---: | :--- |
| 14/15 | INPUT/RDBACK / OUTPUT data set activity |
| 42 | DFSMS statistics and configuration |
| 80 | Security Product Processing |
| 89 | Usage Data |
| 101 | Db2 Accounting |
| 110 | CICS TS Statistics |

## Do not

- Invent `SMF*` names not in IBM docs / IFASMFR.
- Copy decimal offsets into maps — always label differences.
- Assume a section exists on every subtype — check the subtype matrix.
