---
name: zsmf-json-labels
description: Choose and add JSON keys (analytics column names) for zSMFtoJSON SMF_FIELD entries from IBM field descriptions. Use when naming columns, renaming exports, or documenting mapped fields.
---

# JSON Labels / Column Descriptions

In this engine, the **JSON key is the column name** for downstream analytics. It is the `JSON=` operand of `SMF_FIELD`, stored as `CL16`.

## Constraints

- **Max 16 characters** (macro `DC CL16'&JSON'`). Longer names are invalid / truncated by assembler rules — keep ≤16.
- EBCDIC source; use plain ASCII identifiers: `a-z`, `0-9`, `_`.
- Unique within a single mapping table (duplicate keys → duplicate JSON keys in one object).
- Order of `SMF_FIELD` lines = order of keys in the object.

## Naming conventions (repo style)

Existing keys:

```
smf_record_type  smf_system_id  time  date
rec_version  addr_space_ind  program_name  step_name
cpu_step_time  srb_time
user_id  group_name  old_resource  class_name
```

Rules:

1. **snake_case**, lowercase.
2. Prefer meaning over raw IBM name: `SMF30CPT` → `cpu_step_time` (not `smf30cpt`).
3. Keep a stable `smf_` prefix only for record identity fields (`smf_record_type`, `smf_system_id`).
4. Shorten IBM descriptions to ≤16 chars without cryptic codes when possible.
5. For RS tags, name the **business entity** (`class_name`, `old_resource`), not `tag_17`.

## Derive from IBM description

| IBM description (examples) | Good `JSON=` |
| :--- | :--- |
| System identification (SID) | `smf_system_id` |
| Record type | `smf_record_type` |
| All standard CPU step time… | `cpu_step_time` |
| Step CPU time under SRB… | `srb_time` |
| Program name | `program_name` |
| Step name | `step_name` |
| Class name (RS tag 17) | `class_name` |
| Record subtype | `subtype` or `smf_subtype` |

If the clear name exceeds 16 characters, abbreviate the least important words first:

| Too long | ≤16 alternative |
| :--- | :--- |
| `initiator_cpu_tcb_time` | `init_tcb_time` |
| `identification_section` | (don’t expose section names — expose fields) |

## Adding / changing a column label

1. Confirm field via `zsmf-ibm-docs`.
2. Pick `JSON=` with the rules above.
3. Set or replace `JSON=` on the `SMF_FIELD` line in `MAPnn.asm`.
4. Grep other maps for the same key if you care about cross-type schema consistency (e.g. always `time` / `date` / `smf_system_id` for headers).
5. Rebuild `SMF2JSON`; no converter change needed for rename-only edits.

## Cross-type header consistency

Prefer the same keys for common header concepts across `MAP30` / `MAP80` / `MAP89`:

| Concept | Canonical key |
| :--- | :--- |
| Record type | `smf_record_type` |
| System id | `smf_system_id` |
| SMF time | `time` |
| SMF date | `date` |

## Optional comment documentation

Maps today rarely comment each field. When adding non-obvious columns, a one-line comment above the entry helps:

```asm
* SMF30CPT — CPU step time (hundredths), processor section
         SMF_FIELD SMF30CPT-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=cpu_step_time
```

Comments are for humans; JSON keys are the external contract.

## Analytics note

Values are JSON **strings** today (including decimals and dates). Column “type” in warehouses may need casting; do not encode SQL types in the key name.
