---
name: zsmf-add-field
description: Add or change a field in an existing zSMFtoJSON Master Mapping Table (MAPnn.asm). Use when exporting a new SMF column to JSON, wiring triplets/RS tags, or extending MAP30/MAP80/MAP89.
---

# Add a Field to an Existing Mapping Table

Load `zsmf-architecture` and `zsmf-ibm-docs` first if the field identity is unclear.

## Preconditions

1. Target SMF type already has `MAPnn.asm` and is selected in `SMF2JSON.asm`.
2. Field name exists in IBM `IFASMFR` DSECT for that type (or will after `IFASMFR` list update).
3. Chosen `TYPE=` is supported by the engine (`zsmf-data-types`).
4. JSON key ≤ 16 characters (`zsmf-json-labels`).

## Step 1 — Identify the location class

| Class | How you know | Macro shape |
| :--- | :--- | :--- |
| **Header** | Field in header / self-defining section; no section triplet | `SMF_FIELD FLD-SMFxxLEN,TYPE=…,JSON=…` |
| **Triplet section** | Docs say “located using triplet … OF/LN/ON” | `SMF_FIELD FLD-SECT,TRIPLET=xxOF-SMFxxLEN,TYPE=…,JSON=…` |
| **Relocate (RS)** | Tag-Length-Data list (SMF 80) | `SMF_FIELD SMF80REL-SMF80LEN,TYPE=T_RS_STR,TAG=T_RS_n,JSON=…` |

## Step 2 — Resolve IBM labels

From IBM SMF manual / HTML (skill `zsmf-ibm-docs`):

- **Field label**: e.g. `SMF30CPT`
- **Section start label**: first field of that section DSECT, e.g. processor section starts at `SMF30PTY`
- **Triplet offset label**: e.g. `SMF30COF` (Offset / Length / Number triplet; engine uses the **offset** fullword)
- **Format → TYPE**: EBCDIC 8 → `T_CHR8`; binary 4 → `T_DEC4`; packed date → `T_DTE`; time 1/100s → `T_TME`; RS string → `T_RS_STR`

Existing MAP30 examples:

```asm
* Header
         SMF_FIELD SMF30SID-SMF30LEN,TYPE=T_CHR4,JSON=smf_system_id

* Identification section via SMF30IOF
         SMF_FIELD SMF30PGM-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=program_name

* Processor section via SMF30COF
         SMF_FIELD SMF30CPT-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=cpu_step_time
```

MAP80 RS example:

```asm
         SMF_FIELD SMF80REL-SMF80LEN,TYPE=T_RS_STR,TAG=T_RS_17,        X
               JSON=class_name
```

If the RS tag constant is new, add it near the top of `MAP80.asm`:

```asm
T_RS_15  EQU   15    VOLSER volume serial
```

## Step 3 — Edit MAPnn.asm

1. Insert the `SMF_FIELD` **before** `SMF_END` (order = JSON field order).
2. Keep a blank line between entries (repo style).
3. Use continuation `X` in column 72 when the operand spills.
4. Do **not** redefine `T_CHR*` / `T_DEC*` outside `MAP30` unless you also fix COPY order — today `MAP30` defines shared `T_*` and must remain first in `COPY` list.

## Step 4 — Validate mentally

- Relative offset uses **section base**, not header, for triplet fields.
- Triplet operand is `…OF - SMFxxLEN` (offset into record including RDW, as IBM documents).
- Missing section at runtime → engine emits `""` for that field (triplet offset word = 0).
- RS miss → `""`.

## Step 5 — Build / smoke

- Reassemble `SMF2JSON` (maps are `COPY`’d into it); `SMF2ZIIP` unchanged for pure map edits.
- Submit `jcl/SMF2JSON.jcl`; expect RC≤4.
- Confirm new key appears in `JSONOUT` objects for that type.

## Checklist

- [ ] IBM name + format verified
- [ ] Correct case (header / triplet / RS)
- [ ] `TYPE=` / `TAG=` valid
- [ ] `JSON=` ≤ 16, snake_case, unique in table
- [ ] Placed before `SMF_END`
- [ ] No hardcoded hex offsets

## Out of scope for this skill

- New SMF **type** or subtype dispatch → `zsmf-add-type`
- New conversion types (packed decimal, float) → engine change in `SMF2ZIIP.asm` BTAB
