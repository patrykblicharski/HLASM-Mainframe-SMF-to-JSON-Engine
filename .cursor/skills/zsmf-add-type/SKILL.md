---
name: zsmf-add-type
description: Add a new SMF record type (or subtype-aware map) to zSMFtoJSON — MAPnn, IFASMFR, dispatch, JCL extract filters. Use when introducing types like 14/15/42/101/110 or planning subtype-specific tables.
---

# Add a New SMF Type or Subtype Map

Use this when the type is not yet selected in `SMF2JSON.asm`. For fields inside an existing type, use `zsmf-add-field` instead.

## A. New record type (current architecture)

### 1. Create `src/MAPnn.asm`

Minimal portable template (header only — extend with `zsmf-add-field`):

```asm
* ====================================================================
* MASTER MAPPING TABLE FOR SMF TYPE nn (JSON CONVERSION)
* ====================================================================

TABLEnn  SMF_START

         SMF_FIELD SMFnnRTY-SMFnnLEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMFnnSID-SMFnnLEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMFnnTME-SMFnnLEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMFnnDTE-SMFnnLEN,TYPE=T_DTE,JSON=date

         SMF_END
```

Rules:

- Label the table `TABLEnn` (must match `LARL` target).
- Do **not** re-copy `T_*` EQU blocks unless this map is assembled alone — shared constants live in `MAP30.asm` and rely on COPY order.
- RS tag EQU blocks belong in the map that uses them (see `MAP80.asm`).
- Verify real header labels in IBM docs / `IFASMFR` (not every type uses `SMFnnSID` at the same layout; adjust names from the manual).

### 2. Wire `src/SMF2JSON.asm`

1. Extend IBM mappings:

```asm
         IFASMFR (30,80,89,nn)
```

2. Add dispatch **before** the final fall-through to `NEXT_SMF` (pattern from type 89):

```asm
         CLI   5(R9),nn
         BNE   NO_nn
         LARL  R8,TABLEnn
         J     JSONOBJ
NO_nn    EQU   *
```

3. `COPY` the map with the others (keep `MAP30` first so `T_*` exist):

```asm
         COPY  MAP30
         COPY  MAP80
         COPY  MAP89
         COPY  MAPnn
```

### 3. Update extract JCL (optional but usual)

`jcl/SMFEXTRT.jcl` / `SMFEXTRL.jcl`:

```
OUTDD(DUMPOUT,TYPE(30,80,101,102,nn))
```

### 4. Docs / README

- Add type to Supported / Roadmap checkboxes when work lands.
- Prefer documenting real exported JSON keys.

## B. Subtypes — current vs portable future

### Current behavior

- Dispatch reads **one byte** at `5(R9)` = record type only.
- Type 30 subtype is `SMF30STP` (halfword in header); ignored today.
- One `TABLEnn` serves all subtypes; absent sections → `""`.

### When you need subtype-specific maps

Typical reasons:

- Type 30 subtype 1 vs 4/5 expose different useful sections.
- Type 42 / 70–79 / 110 families are subtype-heavy.
- Want smaller JSON per event class.

### Recommended portable approach (engine change)

Keep table-driven style; avoid scattering business logic:

1. **Tables**: `TABLE30_1`, `TABLE30_4`, … or `MAP30S1.asm` etc.
2. **Dispatch** after type match:
   - Load subtype from the IBM label (`SMF30STP` via offset from R9, or a tiny shared helper).
   - `LARL` the matching table; default table if unknown subtype.
3. **Still use IFASMFR labels** for all offsets — subtype only selects which table pointer to pass in `P_TABLE`.
4. Do **not** encode subtype in the 28-byte entry until the engine grows a filter column; selecting the whole table is simpler and portable.

Pseudo-structure:

```
IF type=30
   load subtype
   select TABLE30_s or TABLE30_DEFAULT
   → JSONOBJ
```

### Interim workaround (no engine change)

Map only fields common across subtypes, or accept empty strings for sections not present on some subtypes. Document which subtypes were validated.

## C. Special type families

| Family | Extra complexity | Notes |
| :--- | :--- | :--- |
| 14/15 | Mostly fixed + some sections | Good first extended-library targets (README) |
| 42 | Many subtypes | Prefer subtype tables early |
| 80 | Relocate tags | Needs `T_RS_STR` + tag EQU list |
| 101/102 | Db2 | Often needs Db2 MACLIB (`&DB2MAC` already in JCL) |
| 110 | CICS dictionary | Dictionary-based; may need engine extensions beyond current `T_*` |

If IBM format is Packed/Float and not in BTAB, stop and extend `SMF2ZIIP` (`zsmf-data-types`) before mapping.

## D. Checklist

- [ ] `MAPnn.asm` with `TABLEnn` / `SMF_END`
- [ ] `IFASMFR` includes `nn`
- [ ] Type dispatch + `LARL`
- [ ] `COPY MAPnn` after `MAP30`
- [ ] Extract JCL TYPE list updated if used
- [ ] At least header fields smoke-tested
- [ ] Subtype strategy decided (shared table vs future per-subtype)
