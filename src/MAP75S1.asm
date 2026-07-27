* ====================================================================
* SMF TYPE 75 SUBTYPE 1 — Page data set activity
* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)
* ====================================================================
TABLE75_1 SMF_START

         SMF_FIELD SMF75RTY-SMF75LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF75SID-SMF75LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF75TME-SMF75LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF75DTE-SMF75LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF75SSI-SMF75LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF75STY-SMF75LEN,TYPE=T_DEC2,JSON=subtype

         SMF_FIELD SMF75PRD-SMF75MFV,TRIPLET=SMF75PRS-SMF75LEN,        X
               TYPE=T_CHR8,JSON=product_name

         SMF_FIELD SMF75MVS-SMF75MFV,TRIPLET=SMF75PRS-SMF75LEN,        X
               TYPE=T_CHR8,JSON=mvs_level

         SMF_END
