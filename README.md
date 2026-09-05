```text
      ____  __  __ _____ _            _ ____   ___  _   _ 
 ____/ ___||  \/  |  ___| |_ ___     | / ___| / _ \| \ | |
|_  /\___ \| |\/| | |_  | __/ _ \ _  | \___ \| | | |  \| |
 / /  ___) | |  | |  _| | || (_) | |_| |___) | |_| | |\  |
/___||____/|_|  |_|_|    \__\___/ \___/|____/ \___/|_| \_|
```
# zSMFtoJSON

A high-performance z/OS HLASM (High Level Assembler) engine designed to parse raw System Management Facilities (SMF) records and convert them into standardized, analytics-ready JSON.

## Overview
Raw SMF records are stored in complex binary formats (triplets, offsets, and relocate sections) that are difficult for modern platforms to ingest. This engine bridges the gap by providing a Table-Driven conversion that is both ultra-fast and highly customizable.

## Enterprise Architecture

<p align="center">
  <img src="img/zIIP-offload.webp" alt="zIIP offload" width="300">
</p>

The engine is built with a dual-mode execution architecture:
- **Standard Mode (TCB):** Runs as a standard task, compatible with any z/OS environment.
- **Offload-Ready (SRB):** The core logic is **fully reentrant** and thread-safe, architectured to be dispatched via Service Request Blocks (SRB) within a WLM Enclave

> **Note:** The public version of this repository is configured for TCB mode. The SRB dispatcher and WLM management modules used for performance testing on experimental environments are not included in this public release.

## Python desktop port

A stdlib-only Python rewrite lives under `python/` — table-driven maps for types 30/80/89 and 119 subtype 1, plus a Tkinter GUI (tabs per type/subtype, column tooltips, export JSON/CSV). See [`python/README.md`](python/README.md), [`python/AGENTS.md`](python/AGENTS.md), [`python/ROADMAP.md`](python/ROADMAP.md).

## New: Data-Driven Architecture
The engine has been refactored to use Master Mapping Tables. This allows developers to choose exactly which fields to export to JSON by simply editing a table, without modifying the core logic.

## Supported Data Types

The engine handles the complexity of SMF formats automatically based on the table definition:
Binary/EBCDIC: Fixed length strings (T_CHR1 to T_CHR8).
Numeric: Decimal conversions (T_DEC1 to T_DEC4).
Temporal: Native SMF Date (T_DTE) and Time (T_TME) to ISO-like strings.
Relocate Sections (RS): Advanced parsing of Tag-Length-Data structures (SMF 80) via T_RS_STR.

## Sample JSON Output
```json
[
{"smf_record_type":"30","smf_system_id":"PROD","time":"12:13:59","date":"2026-03-25","rec_version":"05","addr_space_ind":"SMF     ","program_name":"IFASMFDP","step_name":"STEP1   ","cpu_step_time":"1906","srb_time":"679"}
,{"smf_record_type":"30","smf_system_id":"PROD","time":"12:16:08","date":"2026-03-25","rec_version":"05","addr_space_ind":"SMF     ","program_name":"BPXPRECP","step_name":"*OMVSEX ","cpu_step_time":"30","srb_time":""}
,{"smf_record_type":"80","smf_system_id":"PROD","time":"12:20:29","date":"2026-03-25","user_id":"IBMUSER ","group_name":"SYS1    ","old_res":"IBMUSER.REXX","class_name":"DATASET "}
]
```

## Technical Implementation: Mapping Tables
Each SMF type is defined by a mapping table. Here is how you define a field:

Standard header field (Example SMF 30) :
```asm
         SMF_FIELD SMF30SID-SMF30LEN,TYPE=T_CHR4,JSON=smf_system_id
```
Triplets field (Example SMF 30) :
```asm
         SMF_FIELD SMF30CPT-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,TYPE=T_DEC4,JSON=cpu_step_time
```
Relocate Sections field (Example SMF 80) :
```asm
         SMF_FIELD SMF80REL-SMF80LEN,TYPE=T_RS_STR,TAG=T_RS_17,JSON=class_name
```

## How To: Add New Mappings

Contributions to Mapping Tables are highly encouraged! Any new mapping added to the library automatically benefits from the engine conversion logic and is designed to be thread-safe for future performance upgrades

To add a new field to the JSON output, you need the IBM Official Documentation : *z/OS MVS System Management Facilities (SMF)*
Each entry in the mapping table (e.g., MAP30.asm) follows a 24-byte structured format.

**Case 1:** Field located in the Standard Header
If the field is part of the fixed header (no triplet involved):

- Relative Offset: FIELD_NAME - HEADER_START_LABEL
- Triplet Offset: Set to AL4(0) (Indicates no triplet)
- Data Type (1 byte): Choose from T_XXX constants (e.g., T_CHR4, T_DEC1).
- 3 bytes of padding to maintain the 24-byte alignment.
- JSON Label: Up to 16 characters for the output key.

Example (System ID):
```asm
         SMF_FIELD SMF30SID-SMF30LEN,TYPE=T_CHR4,JSON=smf_system_id
```

**Case 2:** Field located via a Triplet (Sections)
Most SMF data (like CPU times or Product sections) are located via triplets (Offset, Length, Number).

- Relative Offset: FIELD_NAME - SECTION_START_LABEL
- Triplet Offset: TRIPLET_OFFSET - HEADER_START_LABEL
- Data Type (1 byte) : The engine will automatically calculate the real memory address using the triplet.
- 3 bytes of padding to maintain the 24-byte alignment.
- JSON Label: Up to 16 characters for the output key.

Example (CPU Step time):
```asm
         SMF_FIELD SMF30CPT-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,TYPE=T_DEC4,JSON=cpu_step_time
```

**Case 3:** Relocated Sections (Tag-Length-Data)
Relocated sections (common in SMF 80) don't use standard triplets. Instead, they consist of a series of variable-length sections identified by a Tag ID.

- Relative Offset: FIELD_NAME - HEADER_START_LABEL
- Triplet Offset: Set to AL4(0) (Not used for RS).
- Data Type (1 byte): Must be T_RS_STR
- Tag ID (1 byte): The specific Tag ID you want to extract (e.g., 17 for Class Name).
- Padding (2 bytes): 2 bytes of padding to maintain the 24-byte alignment.
- JSON Label: Up to 16 characters for the output key.

Example (Class Name, Tag ID : 17):
```asm
         SMF_FIELD SMF80REL-SMF80LEN,TYPE=T_RS_STR,TAG=T_RS_17,JSON=class_name
```


### Data Type Reference Mapping

Use these constants in your mapping tables (`MAP30`, `MAP80`) to define how the engine should process each field.

| Constant | Code | IBM SMF Format | Description | JSON Output |
| :--- | :--- | :--- | :--- | :--- |
| **`T_BIN1`** | `0` | Binary (1) | Single byte binary value | Number |
| **`T_CHR1`** | `1` | EBCDIC (1) | 1-byte character string | String |
| **`T_CHR2`** | `2` | EBCDIC (2) | 2-byte character string | String |
| **`T_CHR4`** | `3` | EBCDIC (4) | 4-byte character string | String |
| **`T_CHR8`** | `4` | EBCDIC (8) | 8-byte character string | String |
| **`T_DEC1`** | `5` | Binary (1) | Unsigned integer (8-bit) | Number |
| **`T_DEC2`** | `6` | Binary (2) | Unsigned integer (16-bit) | Number |
| **`T_DEC4`** | `7` | Binary (4) | Unsigned integer (32-bit) | Number |
| **`T_DTE`** | `8` | Packed (PL4) | SMF Date (0cyydddF) | "YYYY-MM-DD" |
| **`T_TME`** | `9` | Binary (4) | SMF Time (1/100th sec) | "HH:MM:SS" |
| **`T_RS_STR`**| `10`| RS Tag | Relocate Section Variable Data | String |


# Prerequisites
z/OS Environment with HLASM compiler.

SMF Data: A dumped SMF dataset.

# Quick Start
Follow these steps to deploy and run the SMF-to-JSON engine on your system.

1. Configuration

   Open the JCL located in jcl/SMF2JSON.jcl and customize the SET symbols at the top of the job:
   ```jcl
   // SET SRC='USER.SRC'         <-- Source PDS (.asm files)
   // SET SMFIN='USER.SMF.FILE'  <-- INPUT: Your raw SMF dump file   
   // SET OBJ='USER.OBJ'         <-- OUTPUT : intermediate object modules
   // SET LOAD='USER.LOAD'       <-- OUTPUT: Executable library
   ```
   You should have an existing SRC, OBJ, and LOAD PDS (e.g., USER.SRC, USER.OBJ, USER.LOAD)

   In the provided `CONFIG`, the variable `&USEZIIP` is set to `0` by default. This ensures compatibility for all users. Turning this on requires the proprietary SRB Dispatcher module.

2. Build & Run

   Submit the JCL to compile all modules (PROC101, PROC30, HPSMF), link-edit them, and execute the engine:

   Command: SUBMIT 'YOUR.PREFIX.JCL(SMF2JSON)'

   Check Results:
   Ensure all steps finished with RC=0000 or RC=0004.

   The JSON output will be available in the JSONOUT DD (either directed to SYSOUT or the dataset defined in the configuration).

# Roadmap / TODO List

### Phase 1: Core Engine & Data Mapping
- [X] **Mapping Tables**:  The engine must be refactored to use Master Mapping Tables
- [x] **Relocate Section Support**: Native parsing of SMF 80 (RACF) Tag-Length-Data structures.
- [ ] **Extended Mapping Library**:
    - [ ] **SMF 14/15**: Dataset Activity (Non-VSAM).
    - [ ] **SMF 42**: DFSMS Statistics.
    - [ ] **SMF 110**: CICS Performance Data (Dictionary-based parsing).
    - [ ] **SMF 101/102**: DB2 Statistics/Performance.
- [ ] **Numerical Formatting**: Support for **Packed Decimal (P)** and **Floating Point** conversion to JSON numbers.

### Phase 2: Performance & Cost Optimization
- [x] **Reentrant Transformation Engine:** Core logic optimized for concurrent execution.
- [X] **zIIP Offload (Internal):** SRB scheduling and WLM Enclave integration (Private build).
- [ ] **Double Buffering:** Asynchronous I/O to prevent TCB bottlenecks during high-volume processing.

### Phase 3: Extensibility & Integration
- [ ] **User Exit Interface (`SMF2EXIT`)**: 
    - [ ] Provide a standard linkage for User Exits to filter or mask sensitive data (PII) before JSON serialization.
- [ ] **Live Streaming**: Direct integration with **z/OS Logstream (IFASMFDL)** to convert records in real-time instead of batch dumps.

