# AGENTS.md

## Cursor Cloud specific instructions

### What this repository is
`zSMFtoJSON` is a **z/OS mainframe** engine written in **IBM High Level Assembler (HLASM)** plus **JCL**. It parses raw binary SMF (System Management Facilities) records and emits JSON. Source lives in `src/*.asm`; job control lives in `jcl/*.jcl`.

### Important: it cannot be built, run, tested, or linted on this Linux VM
There is intentionally **nothing to install** and **no way to build/run** this codebase in the cloud (Linux/x86) environment. This is expected, not a broken setup:
- HLASM is IBM-proprietary and only runs on z/OS. No HLASM assembler is installable on Linux, so the update script is a deliberate no-op.
- The code depends on IBM macro libraries that only exist on a mainframe: `IFASMFR` (SMF record DSECTs, from `SYS1.MACLIB`), DB2 macros (`DSNB10.SDSNMACS`), and z/OS services (`WTO`, `DCB`, `OPEN`/`GET`/`PUT`/`CLOSE`, `STORAGE`, `BAKR`/`PR` linkage stack, `TESTAUTH`, `ABEND`).
- There is no package manager, no build script, no automated test suite, no linter config, and no CI/git hooks. Do not try to add or install a Linux build toolchain (gcc/as/z390/Hercules will not assemble these z/Architecture + `IFASMFR`/DB2 sources).

### How it is actually built and run (on a mainframe, not here)
Building/running requires a z/OS system with the HLASM compiler (`ASMAC` proc) and the IBM linker (`IEWL`). See the README "Quick Start". In short:
1. Edit the `// SET` symbols at the top of `jcl/SMF2JSON.jcl` (source/obj/load PDS names, SMF input file, JSON output dataset).
2. `SUBMIT 'YOUR.PREFIX.JCL(SMF2JSON)'` — this assembles `SMF2ZIIP` and `SMF2JSON`, link-edits them into a load module, then executes it. JSON is written to the `JSONOUT` DD. Success = all steps `RC=0000` or `RC=0004`.
- `jcl/SMFEXTRT.jcl` / `jcl/SMFEXTRL.jcl` extract SMF data (via `IFASMFDP` / `IFASMFDL`) to feed the engine.

### Non-obvious gotchas
- The public repo is **TCB mode only**: `src/CONFIG.asm` sets `&USEZIIP 0`. Setting it to `1` (SRB/zIIP) references the proprietary SRB dispatcher (`ZSCHDSRB`, `ZSRBPRE`) and WLM modules that are **not included** here, so it will not assemble.
- To add SMF field mappings you edit the `MAPxx.asm` tables (24-byte `SMF_FIELD` entries); the engine (`SMF2ZIIP.asm`) is table-driven, so no core-logic changes are needed. Requires IBM SMF documentation for offsets.
- `test.json` at the repo root is empty (a placeholder), not a fixture.

### Off-mainframe development
Realistic non-mainframe dev is limited to editing `.asm`/`.jcl` files (optionally with a VS Code HLASM extension for syntax diagnostics, which still needs the mainframe macro libraries to fully resolve). Verification of behavior must happen on z/OS.
