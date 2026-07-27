* ====================================================================
* SMF TYPE 76 SUBTYPE 1 — Trace activity
* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)
* ====================================================================
TABLE76_1 SMF_START

         SMF_FIELD SMF76RTY-SMF76LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF76SID-SMF76LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF76TME-SMF76LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF76DTE-SMF76LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF76SSI-SMF76LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF76STY-SMF76LEN,TYPE=T_DEC2,JSON=subtype

         SMF_FIELD SMF76PRD-SMF76MFV,TRIPLET=SMF76PRS-SMF76LEN,        X
               TYPE=T_CHR8,JSON=product_name

         SMF_FIELD SMF76MVS-SMF76MFV,TRIPLET=SMF76PRS-SMF76LEN,        X
               TYPE=T_CHR8,JSON=mvs_level

         SMF_END
