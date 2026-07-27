---
name: zsmf-data-types
description: zSMFtoJSON T_* data type constants, SMF_FIELD entry layout, and SMF2ZIIP conversion cases. Use when choosing TYPE=/TAG= for a map entry or extending the converter BTAB.
---

# Data Types & Engine Behavior

Constants are defined in `MAP30.asm` (shared via COPY order). RS tag ids are local to `MAP80.asm`.

## Supported `TYPE=` values

| Constant | Code | IBM format | Routine | JSON shape |
| :--- | ---: | :--- | :--- | :--- |
| `T_BIN1` | 0 | — | **CASE0 skip** (not a real converter) | field omitted path / no-op |
| `T_CHR1` | 1 | EBCDIC 1 | `GET_CHR` | `"x"` |
| `T_CHR2` | 2 | EBCDIC 2 | `GET_CHR` | string |
| `T_CHR4` | 3 | EBCDIC 4 | `GET_CHR` | string |
| `T_CHR8` | 4 | EBCDIC 8 | `GET_CHR` | string |
| `T_DEC1` | 5 | binary 1 | `GET_DEC` | digits in quotes |
| `T_DEC2` | 6 | binary 2 | `GET_DEC` | digits in quotes |
| `T_DEC4` | 7 | binary 4 | `GET_DEC` | digits in quotes |
| `T_DTE` | 8 | packed `0cyydddF` | `GET_DATE` | `"YYYY-MM-DD"` |
| `T_TME` | 9 | binary 1/100s | `GET_TIME` | `"HH:MM:SS"` |
| `T_RS_STR` | 10 | RS tag-len-data | `GET_RS_STR` | EBCDIC string |
| `T_CHR20` | 11 | EBCDIC 20 | `GET_CHR` | string |
| `T_HEX2` | 12 | binary 2 | `GET_HEX2` | `"XXXX"` hex |

Source of truth: `SMF2ZIIP.asm` `BTAB` / `CASEn`. README’s “T_BIN1 → Number” is **aspirational** — code 0 currently skips.

## Format selection guide

| IBM “Format” column | Prefer |
| :--- | :--- |
| EBCDIC length 1/2/4/8 | `T_CHR1`…`T_CHR8` |
| binary 1/2/4 (unsigned counters/times in hundredths as integers) | `T_DEC1`…`T_DEC4` |
| packed date `0cyydddF` | `T_DTE` |
| SMF time (hundredths since midnight) | `T_TME` |
| Relocate variable EBCDIC | `T_RS_STR` + `TAG=` |
| Packed decimal (P), floating, bit flags, >8 EBCDIC | **not supported** — extend engine first |

Note: JSON numbers are still emitted **inside quotes** by `GET_DEC` today (`"1906"`). Analytics often coerce later; do not assume bare JSON numbers.

## `TAG=` (Relocate Section)

Used only with `TYPE=T_RS_STR`. Stored in entry byte 9.

Known tags in `MAP80.asm`:

| EQU | Id | Meaning (from map comments) |
| :--- | ---: | :--- |
| `T_RS_1` | 1 | Old resource name |
| `T_RS_2` | 2 | New data set name |
| `T_RS_8` | 8 | User-name |
| `T_RS_9` | 9 | Resource name |
| `T_RS_13` | 13 | FROM resource name |
| `T_RS_15` | 15 | VOLSER |
| `T_RS_17` | 17 | Class name |

`GET_RS_STR` walks `SMF80REL` using `SMF80CNT` and matches tag at `9(R8)`.

## Entry layout reminder

```
DC AL4(offset) AL4(triplet) AL1(type) AL1(tag) AL2(0) CL16'json'
```

Stride **28** bytes. Label at +12.

## Triplet runtime semantics

For `GET_CHR` / `GET_DEC`:

1. Load triplet fullword at `record + table.triplet`.
2. If **zero** → write `""` and return (section absent).
3. Else data address = `record + triplet_offset + field_relative_offset`.

Header fields: triplet word in table is 0 → skip triplet logic.

## Extending types (engine work)

When README roadmap items need Packed/Float/longer strings:

1. Add `T_xxx EQU n` in `MAP30.asm`.
2. Append `DC A(CASEn)` to `BTAB` in `SMF2ZIIP.asm` (codes must stay contiguous from 0).
3. Implement `CASEn` + helper; keep reentrancy (use `DYNAMIC_WORK` only, no static mutable state).
4. Document in README type table.
5. Maps can then reference the new `TYPE=`.

Never renumber existing `T_*` codes — shipped maps depend on them.
