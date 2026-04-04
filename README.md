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

Standard Triplets (Example SMF 30) :
```asm
BASE OFFSET(4) | OFFSET TRIPLET IF NEEDED(4) | TYPE(1) | PAD(3) | JSON LABEL (16)
DC    AL4(SMF30CPT-SMF30PTY),AL4(SMF30COF-SMF30LEN)
DC    AL1(T_DEC4),AL3(0)
DC    CL16'cpu_step_time'
```
Relocate Sections (Example SMF 80) :
```asm
BASE OFFSET(4) | UNUSED (4)  | TYPE(T_RS_STR) | TAG_ID(1) | JSON LABEL
DC    AL4(SMF80REL-SMF80LEN),AL4(0)
DC    AL1(T_RS_STR),AL1(T_RS_17),AL2(0)
DC    CL16'class_name'
```

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

2. Build & Run

   Submit the JCL to compile all modules (PROC101, PROC30, HPSMF), link-edit them, and execute the engine:

   Command: SUBMIT 'YOUR.PREFIX.JCL(SMF2JSON)'

   Check Results:
   Ensure all steps finished with RC=0000 or RC=0004.

   The JSON output will be available in the JSONOUT DD (either directed to SYSOUT or the dataset defined in the configuration).


